# Orbit Paper 3:4 Canvas Pack

This pack turns the approved neutral canvas into a portable asset for other Skills and projects.

## Contents

- `background.png` — the reusable 3:4 background canvas.
- `canvas.json` — dimensions, hash, palette, visual language, and a recommended text-safe region.
- `background-orange-cats-v1.png` — a selectable variant with playful orange tabby cats around the perimeter.
- `variants.json` — the variant index, hashes, and per-variant selection metadata.

## Use in HTML/CSS

```css
.canvas {
  width: 1080px;
  height: 1440px;
  background: url("./assets/canvases/orbit-paper-3x4/background.png") center / cover no-repeat;
}
```

Put Chinese text, numbers, tables, and charts in editable HTML/SVG layers. Do not paint corrective text into the PNG.

## Copy to another Skill

Copy the complete `orbit-paper-3x4` directory into that Skill's `assets/canvases/` directory. Keep `background.png` and `canvas.json` together so consumers can verify the SHA-256 and read the safe-area metadata.

When a new background is generated, add it as a versioned sibling PNG in this same directory and add one entry to `variants.json`; never replace an existing background unless the user explicitly asks for replacement.

## Use in another project

Copy the directory into the project's `assets/canvases/` directory, then reference the image with a project-relative path. Do not depend on the temporary `generated_images` location.

Select either `background.png` or `background-orange-cats-v1.png` according to the content mood. The cat variant uses a smaller central text-safe region because the cats occupy the outer edges.

## Use with Reference Visual Studio

For a hybrid job, attach this existing background and then render and QA the editable text layer:

```powershell
python .agents/skills/reference-visual-studio/scripts/rvs.py attach-ai `
  --job <job-directory> `
  --image <path-to-pack>\background.png `
  --role background
python .agents/skills/reference-visual-studio/scripts/rvs.py render --job <job-directory>
python .agents/skills/reference-visual-studio/scripts/rvs.py qa --job <job-directory>
```

To make it searchable as a visual reference, place a copy in a source directory and ingest it into a library with `rvs.py ingest --library <id> --source <directory>`.

## Prompt guidance for an AI-capable Skill

Use the canvas as a visual reference for palette, framing, negative space, and line language. If the background must remain exact, use it as the fixed background in a hybrid workflow instead of asking an image model to redraw it.
