# Directives [​](#directives){.header-anchor aria-label="Permalink to \"Directives\""} {#directives tabindex="-1"}

Blits comes with a few built-in attributes that tap into specific
behaviour provided by the framework - also known as *directives*. Most
of them can be used in the template on both Elements and Components.

## Show-directive [​](#show-directive){.header-anchor aria-label="Permalink to \"Show-directive\""} {#show-directive tabindex="-1"}

The `show` attribute allows you to conditionally show and hide
Components and Elements.

When passed a *truthy* value, such as `true` or `1`, the element will be
made visible. And when passed a *falsey* value (`false` or `0`) it will
not be visible.

::: {.language-xml .vp-adaptive-theme}
[xml]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
<Element>
  <Element w="100" h="100" color="purple" :show="$active"></Element>
  <Element w="100" h="100" y="200" color="purple" show="false"></Element>
</Element>
```
:::

## Is-directive [​](#is-directive){.header-anchor aria-label="Permalink to \"Is-directive\""} {#is-directive tabindex="-1"}

The `is` directive allows you to dynamically instantiate a Component
based on a `state` variable or a passed `prop`.

It is very useful in combination with API driven Apps, where the type of
Component to use, depends on what data is returned (i.e. a `Poster` or a
`HeroImage`).

The `is`-component should always be used together with the built-in
`Component`-tag.

::: {.language-js .vp-adaptive-theme}
[js]{.lang}

``` {.shiki .shiki-themes .github-light .github-dark .vp-code tabindex="0"}
export default Blits.Component('DynamicComponents', {
  template: `
    <Element>
      <Component is="$firstComponent" />
      <Component is="$secondComponent" x="500" />
    </Element>
  `,
  props: ['firstComponent', 'secondComponent'],
})
```
:::

At the moment it\'s not possible to use the `is`-attribute as a
*reactive* attribute and have a component change type after
instantiation.

## Ref-attribute [​](#ref-attribute){.header-anchor aria-label="Permalink to \"Ref-attribute\""} {#ref-attribute tabindex="-1"}

The declarative coding style that is promoted in Blits components,
should generally remove the need to directly interact with individual
Elements or Components in your template. However, in some cases you may
need to reference them directly. For example, in order to delegate the
focus.

For this use case, you can specify a `ref`-attribute on Elements (or
Components). And by using the helper function `this.select()`, which is
available on every Blits component, you can gain access to the child
Element or Component inside your business logic.

The `select()`-function accepts the `ref`-value that you are looking for
as a single argument, and returns the Element or Component if found.
