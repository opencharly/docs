# OpenCharly website style guide

> Canonical design reference: the supplied OpenCharly Cinematic Assetboard. This document governs the Astro/Starlight site at https://opencharly.ai.

## Design identity

OpenCharly is the agentic DevOps tool for people and their agents. The website should feel like a premium chocolatier's workshop fused with precision engineering: cinematic, richly rendered, warm, whimsical and technically credible. **A kinder internet.**

Use the original gold crown with colored droplets and the original OpenCharly wordmark. **Do not redraw the logo as generic flat SVG geometry.** The supplied Charly illustration is the canonical mascot: cream armor, copper mechanisms, black faceplate, amber eyes and chocolate apron with a gold crown. Keep its proportions and materials.

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

The theme uses this warm palette. For accessibility, links on dark cocoa use a lighter derived blue (`#9BC3FF`), and light-theme links use `#1746B2`. Derived UI colors are implementation choices, not new official brand swatches.

## Nine families

| Family | Color | Visual metaphor |
| --- | --- | --- |
| Forge & Build | `#F97316` | Forged gear |
| Proof & Evaluation | `#10B981` | Verification emblem |
| Agents & Intelligence | `#AB50F6` | Illuminated brain |
| Runtime & Boxes | `#3B82F6` | Crystal cube |
| Network & Connectivity | `#06B6D4` | Connected sphere |
| Systems & Security | `#F4A308` | Shield |
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

## Implementation and source limits

`src/styles/opencharly.css` defines the warm neutral ramps, contrast-safe links, typography, focus and reduced-motion behavior. Starlight retains its navigation, search, sidebar, code controls and generated narrative. The `Hero` override adds artwork only on the homepage; the original hero renders its generated title, tagline and actions. The `SiteTitle` override presents the crown and wordmark on an intentional black plaque in both themes. Family cards are a visual showcase, not a new navigation taxonomy.

The operator approved extraction from the flattened **1774 × 887 RGB assetboard**. `assets/brand/assetboard.png` is the sole source copy. The dimensions printed inside the board describe unavailable originals; they are not the dimensions or transparency of these supplied pixels. All extracted assets preserve the black background. Do not remove it with color keying, redraw the logo, or enlarge the source and imply added detail.

Run `node scripts/extract-brand.mjs` after `npm ci` to reproduce `public/brand/`. The script is the canonical crop manifest, with pixel coordinates excluding printed filenames, family labels and swatches. It exports:

- Crown (216 × 178), wordmark (462 × 88), workshop hero (826 × 300) and waving mascot (305 × 291) as WebP.
- Nine family illustrations (190 × 152; packaging 184 × 152) as WebP, with HTML labels supplied separately for accessibility.
- Smaller 400px and 640px hero variants, without upscaling.
- Opaque 16px, 32px, 48px and 180px PNG favicons from the crown. Padding accommodates the crown's original aspect ratio.
- A 1200 × 630 PNG social card composed from native-size crops on black, without enlarging their pixels.

The hero is capped at its source width, the mascot at 190 CSS pixels, family artwork at 190 CSS pixels, and the header wordmark below its native dimensions. These are intentionally compact web assets from a reference board; future higher-resolution source art should replace the canonical board and crop manifest together.

## Quality bar

The site includes branded English search labels and a custom recovery page built with StarlightPage. The recovery route owns the 404 output, with links home and to installation; it is excluded from search indexing.

Check WCAG AA text contrast, keyboard and focus states, light/dark modes, mobile layouts, 200% zoom, reduced motion, reproducible asset extraction and `npm ci && npm run build`. Verify favicon and social metadata in the built HTML. Keep generated content owned by its generation workflow and retain the repository's PR-only validation policy.
