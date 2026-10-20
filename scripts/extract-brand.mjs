// Rebuild from the supplied flattened RGB board. Coordinates exclude its printed labels.
import sharp from 'sharp';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
const root = new URL('../', import.meta.url);
const source = fileURLToPath(new URL('assets/brand/assetboard.png', root));
const output = fileURLToPath(new URL('public/brand/', root));
await mkdir(output, { recursive: true });
export const crops = {
  crown: [1006, 16, 216, 178],
  wordmark: [202, 48, 462, 88],
  hero: [24, 243, 826, 300],
  mascot: [862, 253, 305, 291],
  forge: [10, 584, 190, 152],
  proof: [208, 584, 190, 152],
  agents: [404, 584, 190, 152],
  runtime: [600, 584, 190, 152],
  network: [796, 584, 190, 152],
  security: [992, 584, 190, 152],
  tooling: [1188, 584, 190, 152],
  media: [1384, 584, 190, 152],
  packaging: [1580, 584, 184, 152],
};
const metadata = await sharp(source).metadata();
if (metadata.width !== 1774 || metadata.height !== 887 || metadata.hasAlpha) {
  throw new Error('Expected the original 1774 × 887 opaque assetboard');
}
const crop = (name) => {
  const [left, top, width, height] = crops[name];
  return sharp(source).extract({ left, top, width, height });
};
for (const name of Object.keys(crops)) {
  await crop(name).webp({ quality: 88 }).toFile(`${output}/${name}.webp`);
}
for (const width of [400, 640]) {
  await crop('hero').resize({ width, withoutEnlargement: true }).webp({ quality: 86 }).toFile(`${output}/hero-${width}.webp`);
}
for (const size of [16, 32, 48, 180]) {
  await crop('crown').resize(size, size, { fit: 'contain', background: '#000', withoutEnlargement: true }).png().toFile(`${output}/favicon-${size}.png`);
}
// Compose at social-card size; each source crop retains its native pixel dimensions.
await sharp({ create: { width: 1200, height: 630, channels: 3, background: '#000' } })
  .composite([
    { input: await crop('crown').resize({ width: 110 }).png().toBuffer(), left: 105, top: 43 },
    { input: await crop('wordmark').png().toBuffer(), left: 248, top: 48 },
    { input: await crop('hero').png().toBuffer(), left: 24, top: 236 },
    { input: await crop('mascot').png().toBuffer(), left: 875, top: 244 },
  ]).png().toFile(`${output}/social.png`);
console.log(`Extracted ${Object.keys(crops).length} opaque artwork crops, responsive hero, four favicons and social card.`);
