# OpenCharly website style guide

> Canonical design reference: the supplied OpenCharly visual style guide and GitHub avatar. This document governs the Astro/Starlight site at https://opencharly.ai.

## Design identity

OpenCharly is the agentic DevOps tool for people and their agents. The website should feel like a premium chocolatier's workshop fused with precision engineering: cinematic, richly rendered, warm, whimsical and technically credible. **A kinder internet.**

Use the original gold crown with colored droplets and the original OpenCharly wordmark. **Do not redraw the logo as generic flat SVG geometry.** The supplied Charly avatar is the canonical mascot: cream armor, copper mechanisms, black faceplate, amber eyes and chocolate apron with a gold crown. Keep its proportions and materials.

## Brand palette

| Token | Hex | Purpose |
| --- | --- | --- |
| Cocoa | `#1A0F0A` | Dark canvas |
| Ganache | `#382A22` | Panels |
| Caramel | `#D4A574` | Warm highlights |
| Crème | `#F8EBD7` | Dark-mode text |
| Flame blue | `#2563EB` | Interactive brand hue |
| Gold | `#D4AF37` | Crown and signature accents |
| Ivory | `#FAF9F4` | Light background |

The source palette is retained verbatim. For accessibility, links on dark cocoa use a lighter derived blue (`#9BC3FF`), and light-theme links use `#1746B2`. Derived UI colors are implementation choices, not new official brand swatches.

## Nine families

| Family | Color | Visual metaphor |
| --- | --- | --- |
| Forge & Build | `#F97316` | Forged gear |
| Proof & Evaluation | `#10B981` | Verification emblem |
| Agents & Intelligence | `#A855F7` | Illuminated brain |
| Runtime & Boxes | `#3B82F6` | Crystal cube |
| Network & Connectivity | `#06B6D4` | Connected sphere |
| Systems & Security | `#F59E0B` | Shield |
| Tooling & Developer UX | `#64748B` | Terminal |
| Media & Interfaces | `#EC4899` | Media symbol |
| Packaging & Distribution | `#8B5CF6` | Package |

Keep the nine original family illustrations from the visual guide as visual references. Never replace them with unrelated stock icons. Family colors are accents, not full-page background colors. Family names describe the website's visual taxonomy; product claims must be verified against the `charly` and `marketplace` sources.

## Typography

Use **Playfair Display** for display headings and **Inter** for UI, navigation and body copy; use a system monospace stack for CLI and code. The CSS theme loads the two display families through Google Fonts via Starlight's `head` entries. Keep code copyable and technical content readable.

## Website design

- Rich original artwork belongs in the homepage hero, social previews and family cards; documentation should retain clear hierarchy and generous whitespace.
- Prefer dark cocoa as the signature experience, with an accessible warm ivory light theme.
- Use fine caramel borders, restrained gold highlights, softly rounded cards, and subtle lighting. Avoid neon gradients and generic SaaS iconography.
- Keep navigation, search, code blocks and generated reference pages intact.
- Do not edit generated `src/content/docs/index.md`, `reference/**`, or `recipes/**` by hand. The homepage content comes from `charly/README.md`.
- Use responsive raster formats for cinematic illustrations. SVG is appropriate only for authentic source vector artwork or simple functional UI symbols, never as a cheap redraw of the official logo.

## Implementation

The live Starlight tokens are in `src/styles/opencharly.css`, included via `astro.config.mjs`. The theme sets dark and light surfaces, contrast-safe links, typography, keyboard focus and reduced motion. It deliberately does **not** install a generic third-party theme or replace the favicon with an approximation.

### Asset acceptance checklist

- [ ] Obtain original layered/high-resolution crown and wordmark source, then export approved web formats.
- [ ] Prepare the canonical GitHub avatar for web delivery without changing Charly's design.
- [ ] Export the nine family illustrations from approved source art (not text-bearing screenshots).
- [ ] Compose one cinematic homepage hero using original artwork.
- [ ] Export approved favicon and social sharing preview from original brand artwork.

The flattened guide crops produced during exploration are **reference material only**, not approved production-ready transparent logos. Until source-quality artwork is available, preserve the site's existing favicon rather than ship a degraded replacement.

## Quality bar

Check WCAG AA text contrast, keyboard and focus states, light/dark modes, mobile layouts, 200% zoom, reduced motion, and `npm ci && npm run build`. Keep the generated-docs workflow and the repository's PR-only validation policy intact.
