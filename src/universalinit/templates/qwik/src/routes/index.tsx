import { component$ } from "@builder.io/qwik";
import type { DocumentHead } from "@builder.io/qwik-city";

// PUBLIC_INTERFACE
export default component$(() => {
  return (
    <div class="page-container">
      <h1 class="main-title">Welcome</h1>
    </div>
  );
});

export const head: DocumentHead = {
  title: "Ultralight Qwik Template",
  meta: [
    {
      name: "description",
      content: "Ultralight Qwik template with centered h1 title",
    },
  ],
};
