// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// Generated documentation and autogeneration are intentionally preserved.
export default defineConfig({
  site: 'https://opencharly.ai',
  integrations: [
    starlight({
      title: 'OpenCharly',
      description: 'The wonky DevOps tool for you and your agents.',
      customCss: ['./src/styles/opencharly.css'],
      head: [
        { tag: 'link', attrs: { rel: 'preconnect', href: 'https://fonts.googleapis.com' } },
        { tag: 'link', attrs: { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: 'anonymous' } },
        { tag: 'link', attrs: { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap' } },
      ],
      social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/opencharly/charly' }],
      editLink: { baseUrl: 'https://github.com/opencharly/docs/edit/main/' },
      sidebar: [
        { label: 'Start here', items: [{ autogenerate: { directory: 'start' } }] },
        { label: 'Concepts', items: [{ autogenerate: { directory: 'concepts' } }] },
        { label: 'Guides', items: [{ autogenerate: { directory: 'guides' } }] },
        {
          label: 'Reference',
          items: [
            { label: 'Provider index', link: '/reference/providers/' },
            { label: 'CLI', collapsed: true, items: [{ autogenerate: { directory: 'reference/cli' } }] },
            { label: 'Candies', collapsed: true, items: [{ autogenerate: { directory: 'reference/candy' } }] },
            { label: 'Boxes', collapsed: true, items: [{ autogenerate: { directory: 'reference/box' } }] },
            { label: 'Plugins', collapsed: true, items: [{ autogenerate: { directory: 'reference/plugin' } }] },
          ],
        },
        { label: 'Recipe cards', collapsed: true, items: [{ autogenerate: { directory: 'recipes' } }] },
        { label: 'Who We Are', link: '/soul/' },
        { label: 'The Vision', link: '/vision/' },
        { label: 'What it is reacting to', link: '/grievances/' },
        { label: 'Liberation', link: '/liberation/' },
      ],
    }),
  ],
});
