# Utility methods [​](#utility-methods){.header-anchor aria-label="Permalink to \"Utility methods\""} {#utility-methods tabindex="-1"}

Besides the methods that are specified in the Component configuration
object, each Blits Component comes with a number of *utility methods*
built in.

Utility methods are prefixed with a `$`-sign, to clearly indicate they
are *framework provided* methods, that are *not private*, but intended
to be *used by the developer*. The `$`-prefix also helps prevent
accidental naming collisions.

### \$select [​](#select){.header-anchor aria-label="Permalink to \"$select\""} {#select tabindex="-1"}

`this.$select()` is used to search for child Elements and Components by
reference (`ref`).

The `$select()`-method accepts a string pointing to a reference as it\'s
only argument, and returns the Element or Component that matches that
`ref`. In order to make an Element or Component findable, the
`ref`-attribute should be provided on said Element of Component in the
template.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
export default Blits.Component('MyComponent', {
  components: {
    Button,
  },
  template: `
    <Element>
      <Element w="1920" h="5" color="green" ref="topBorder" />
      <Button text="Button 1" ref="btn1" y="100" />
      <Button text="Button 2" ref="btn2" y="200" />
      <Button text="Button 3" ref="btn3" y="200" />
    </Element>
  `,
  hooks: {
    ready() {
      const topBorderElement = this.$select('topBorder')
      const button2 = this.$select('btn2')
    }
  }
})
```
:::

> As the `this.$select()` gives direct access to an Element or a
> Component, it allows the developer to directly interact with it. There
> are valid use cases, but direct manipulation of Elements, calling
> methods and changing properties on a Component comes with risks. It
> circumvents the whole structure of reactivity and props communication
> built into Blits, and can lead to unexpected situations or
> anti-patterns. So use with care!

### \$focus [​](#focus){.header-anchor aria-label="Permalink to \"$focus\""} {#focus tabindex="-1"}

The `$focus()`-method can be used to set the focus to a Component
instance. It can either be called on the instance itself, in order to
\"claim\" the focus. But more often it will be used to delegate the
focus from on Component to another.

> It is important to understand that only a Component can receive focus
> in Blits. Elements don\'t have a focus method, and also have no way of
> reacting to focus changes (because they have no hooks etc.).

Often focus will be passed onto a child component, for example in the
case of a list or swimlane, where you want to delegate the focus to a
poster. In this case the focus method will be used in combination with
`this.$select()` to first select the desired child Component by ref, and
subsequently call the `$focus()` method on that Component.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
export default Blits.Component('MyComponent', {
  components: {
    Button,
  },
  template: `
    <Element>
      <Element w="1920" h="5" color="green" ref="topBorder" />
      <Button text="Button 1" ref="btn1" y="100" />
      <Button text="Button 2" ref="btn2" y="200" />
      <Button text="Button 3" ref="btn3" y="200" />
    </Element>
  `,
  state() {
    focusIndex: 1
  },
  input: {
    down() {
      this.focusIndex--
      const button = this.$select(`btn${this.focusIndex}`)
      if(button) {
        button.$focus()
      }
    },
    up() {
      this.focusIndex++
      const button = this.$select(`btn${this.focusIndex}`)
      if(button) {
        button.$focus()
      }
    },
  }
})
```
:::

Another frequent case is that focus is passed on to the parent
Component. The parent component is available on the Component scope as
`this.parent`. So passing the focus to the parent is as simple as
calling `this.parent.$focus()`.

The `$focus`-method accepts an optional `event` parameter, which is of
the type `KeyboardEvent`. When the `event` parameter is provided, not
only will the selected Component receive focus, but the input event will
be emitted again on the component that just received focus.

This can be used to *bubble up* input events (specified in the `input`
key of the component configuration object) and helps to create a smooth
experience, preventing a user to click multiple times.

### \$trigger [​](#trigger){.header-anchor aria-label="Permalink to \"$trigger\""} {#trigger tabindex="-1"}

Blits has reactivity built-in, which means that re-renders in the
template, as well as watchers and computed properties, are automatically
fired whenever a state value changes. But sometimes you may want trigger
the side effects of a state values change, without actually changing the
value. This often is useful when a Component first receives focus and
you want to ensure that the default state values are applied.

Instead of setting a value to `null` and then setting it back to the
initial value (which would trigger side effects), the `this.$trigger()`
method can be used. The method accepts the name of the state variable as
its argument.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
export default Blits.Component('MyComponent', {
  state() {
    focusIndex: 1
  },
  watchers: {
    focusIndex(v) {
      console.log('I trigger when focusIndex changes')
    }
  },
  hooks: {
    focus() {
      // even though focusIndex didn't change
      // the watcher on focusIndex will be fired
      this.$trigger('focusIndex')
    }
  }
})
```
:::

## Emitting events and passing data [​](#emitting-events-and-passing-data){.header-anchor aria-label="Permalink to \"Emitting events and passing data\""} {#emitting-events-and-passing-data tabindex="-1"}

### \$emit [​](#emit){.header-anchor aria-label="Permalink to \"$emit\""} {#emit tabindex="-1"}

When working with Components in Blits you will often want to send data
from one to another. In the case of (direct) child Component, using
props is the defacto way for inter-component communication.

For passing data from a child to a parent component, you may be tempted
to use the `this.parent` reference and change the state directly. While
this works, it does create a strict dependency on the parent, meaning
the child Component only works properly when tied directly to a specific
parent. This reduces reusability of Components and may cause limitations
or problems later on.

Instead the `this.$emit()` method can be used, which is available on
each Component as a utility function. It\'s designed to easily emit data
to anywhere in an App. The first argument is the `name` of the event
that will be emitted (i.e. `changeBackground`) and optionally a second
argument with additional `data` can be passed.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
export default Blits.Component('MyComponent', {
  input: {
    enter() {
      // sending a activate event, without any additional data
      this.$emit('activate')
    },
    space() {
      // sending a changeBackground event, with additional data
      this.$emit('changeBackground', {
        img: './assets/background1.jpg',
        delay: 400
      })
    }
  }
})
```
:::

### \$listen [​](#listen){.header-anchor aria-label="Permalink to \"$listen\""} {#listen tabindex="-1"}

The `$listen` utility method (which is available on each Blits
Component) is designed to listen for events emitted by `this.$emit()`.
Any Component can subscribe to any event emitted and as such a flexible
system of passing data around can be constructed.

The first argument of the `$listen()`-method is the event `name` to
listen for, and the second argument is a `callback` to be executed
anytime the event occurs. When the event is emitted with additional
data, it\'s passed as the first argument in the callback.

Generally the listeners are registered in the Component `ready` or
`init` hook. Blits automatically takes care of deregistering the
listeners whenever a Component is destroyed.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
export default Blits.Component('MyComponent', {
  hooks: {
    init() {
      // activate event without any additional value
      this.$listen('activate', () => {
        console.log('activated')
        // set a text state valuye
        this.text = 'We are active!'
      })

      // change background event
      this.$listen('changeBackground', (data) => {
        setTimeout(() => {
          this.backgroundImage = data.img
        }, data.delay)
      })
    },
  }
})
```
:::

### \$unlisten [​](#unlisten){.header-anchor aria-label="Permalink to \"$unlisten\""} {#unlisten tabindex="-1"}

The `$unlisten` utility method (which is available on each Blits
Component) is designed to remove event listeners that were previously
registered using `$listen()`. This method helps in managing event
listeners manually when needed.

The first argument of the `$unlisten()` method is the event `name` to
stop listening for. This ensures that all listeners for the specified
event are removed from the component.

Generally, you might not need to call `$unlisten()` manually, as Blits
automatically deregisters listeners when a Component is destroyed.
However, it can be useful in scenarios where you need to stop listening
for events before the Component is destroyed.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
export default Blits.Component('MyComponent', {
  hooks: {
    init() {
      this.activateListener = () => {
        console.log('activated')
        this.text = 'We are active!'
      }

      this.changeBackgroundListener = (data) => {
        setTimeout(() => {
          this.backgroundImage = data.img
        }, data.delay)
      }

      // Register listeners
      this.$listen('activate', this.activateListener)
      this.$listen('changeBackground', this.changeBackgroundListener)
    },
    unfocus() {
      // Remove listeners when Component is unfocused
      this.$unlisten('activate')
      this.$unlisten('changeBackground')
    }
  }
})
```
:::

## Timeouts [​](#timeouts){.header-anchor aria-label="Permalink to \"Timeouts\""} {#timeouts tabindex="-1"}

Setting a timeout is a typical way in JS to execute functionality with a
delay. But timeouts can also be a common cause of memory leaks.

As long as the timeout is still pending it, it will hold on to
references which can prevent a proper garbage collection from happening.
That\'s why it\'s important to clear timeouts when destroying a
component.

Blits comes with some built-in methods to register and clear timeouts.
Under the hood these methods use regular timeouts, but using the Blits
built-in methods ensures that timeouts properly are cleared whenever a
component is being disposed.

### \$setTimeout [​](#settimeout){.header-anchor aria-label="Permalink to \"$setTimeout\""} {#settimeout tabindex="-1"}

The `this.$setTimeout()`-method creates a timeout, using a thin wrapper
around the `window.setTimeout()` method. The first argument is the
`callback` to be executed after the `delay` specified in the second
argument. The method returns a `timeout id`, which can be used to
mannually clear the timeout.

### \$clearTimeout [​](#cleartimeout){.header-anchor aria-label="Permalink to \"$clearTimeout\""} {#cleartimeout tabindex="-1"}

The `this.$clearTimeout()`-method is a thin wrapper around the
`window.clearTimeout()`-method. By passing in the `id` of a timeout, it
will clear and remove the timeout.

### \$clearTimeouts [​](#cleartimeouts){.header-anchor aria-label="Permalink to \"$clearTimeouts\""} {#cleartimeouts tabindex="-1"}

The `this.$clearTimeouts()`-method is a utility method that is used to
clear all the timeouts created via the `this.$setTimeout()` method in
one go. The method doesn\'t require to pass any timeout ids. This method
is automatically called when destroying a Component, and with that it
prevents memory leaks due to dangling timeouts.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
export default Blits.Component('MyComponent', {
  state() {
    timeout: null
  },
  hooks: {
    init() {
      this.timeout = this.$setTimeout(() => {
        console.log('1 minute has passed!')
      }, 60000)

      this.$setTimeout(() => {
        console.log('10 seconds have passed!')
      }, 10000)
    },
    unfocus() {
      // clear all timeouts when Component is unfocused
      this.$clearTimeouts()
    }
  },
  input: {
    enter() {
      // clear the timeout
      this.$clearTimeout(this.timeout)
    }
  }
})
```
:::

## Intervals [​](#intervals){.header-anchor aria-label="Permalink to \"Intervals\""} {#intervals tabindex="-1"}

Timeouts are a great way to execute recurring logic, such as polling for
updates or periodically updating an animation.

But similar to timeouts, intervals (more specifically failing to clear
them) are a common source of memory leaks - maybe even more than
dangling timeouts.

For this reason Blits has 3 built-in utility methods to help registering
and clearing intervals.

### \$setInterval [​](#setinterval){.header-anchor aria-label="Permalink to \"$setInterval\""} {#setinterval tabindex="-1"}

The `this.$setInterval()`-method create an interval, using a thin
wrapper around the `window.setInterval()` method. The first argument is
the `callback` to be executed after each interval `delay` specified in
the second argument. The method returns an `interval id`, which can be
used to manually clear the interval.

### \$clearInterval [​](#clearinterval){.header-anchor aria-label="Permalink to \"$clearInterval\""} {#clearinterval tabindex="-1"}

The `this.$clearInterval()`-method is a thin wrapper around the
`window.clearInterval()`-method. By passing in the `id` of an interval,
it will clear and remove the interval.

### \$clearIntervals [​](#clearintervals){.header-anchor aria-label="Permalink to \"$clearIntervals\""} {#clearintervals tabindex="-1"}

The `this.$clearIntervals()`-method is a utility method that is used to
clear all the intervals created via the `this.$setInterval()` method in
one go. The method doesn\'t require to pass any interval ids. This
method is automatically called when destroying a Component, and with
that it prevents memory leaks due to dangling intervals.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
export default Blits.Component('MyComponent', {
  state() {
    return {
      interval: null,
      secondCount: 0,
      minuteCount: 0,
    }
  },
  hooks: {
    init() {
      this.interval = this.$setInterval(() => {
        this.secondCount++
        console.log(`${this.secondCount} second(s) have passed`)
      }, 1000)

      this.$setInterval(() => {
        this.minuteCount++
        console.log(`${this.minuteCount} minute(s) have passed`)
      }, 60000)
    },
    unfocus() {
      // clear all intervals when Component is unfocused
      this.$clearIntervals()
    }
  },
  input: {
    enter() {
      // clear the interval
      this.$clearInterval(this.interval)
    }
  }
})
```
:::
