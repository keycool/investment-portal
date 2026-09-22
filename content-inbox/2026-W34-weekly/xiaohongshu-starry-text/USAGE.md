# Xiaohongshu Starry Text Canvas Pack

This pack is designed for Xiaohongshu posts where Chinese text is the primary content and the background supplies a dreamy, quiet atmosphere.

## Contents

- `background-v1.png` — the current starry background, with no text.
- `canvas.json` — dimensions, hash, palette, visual elements, and the recommended text-safe area.
- `variants.json` — version index for future starry background variants.

## Use in HTML/CSS

```css
.post-canvas {
  width: 1080px;
  height: 1440px;
  background: url("./assets/canvases/xiaohongshu-starry-text/background-v1.png") center / cover no-repeat;
}
```

Put the exact title, body, lists, dates, and data in editable HTML/CSS/SVG layers. Do not repair text by painting over the PNG.

## Add future backgrounds

Save each new image as a versioned sibling such as `background-purple-v2.png`, then add one entry to `variants.json`. Keep old variants available so each post can choose the appropriate atmosphere.

## Recommended use

Use the central area for the main text block and keep decorative stars, constellation lines, and brighter nebula edges outside dense copy. For exact Chinese text, use the hybrid route in Reference Visual Studio.
