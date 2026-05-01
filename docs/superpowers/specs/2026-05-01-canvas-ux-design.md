# Canvas UX Upgrade — Design Spec

**Date:** 2026-05-01  
**Status:** Approved  
**Branch:** `feature/canvas-ux`

---

## Overview

Upgrade InkStone's canvas rendering from a basic static layout toward a jsoncanvas-level experience. Four improvement areas: interactive pan/zoom, full markdown in text nodes, correct edge directionality, and visual polish. Developed on a feature branch and merged when complete.

---

## Area 1 — Interactive Pan & Zoom

### Goal
Users can pan by dragging and zoom by scrolling/pinching. A fit-to-view button resets the viewport. Works on desktop (mouse) and mobile (touch).

### Structure change
The current `<div class="canvas-view">` (viewport) gains `overflow: hidden` and a fixed height. Inside it, a new `<div class="canvas-stage">` wraps the SVG edge layer and all node divs. JS applies `transform: translate(Xpx, Ypx) scale(Z)` to the stage only.

Node positions switch from **percentage-based** (current) to **absolute pixel** values matching the canvas coordinate system. The stage is sized exactly to the canvas bounding box in px. This makes transform math exact and eliminates rounding artifacts.

### Interactions
- **Pan:** `mousedown` on the viewport starts drag tracking; `mousemove` updates translate by the pointer delta; `mouseup`/`mouseleave` ends drag. Cursor changes to `grab`/`grabbing`.
- **Zoom:** `wheel` event on the viewport. Zoom is centered on the cursor position — translate is adjusted so the point under the cursor stays fixed. Formula: `newTranslate = cursor - (cursor - oldTranslate) * (newScale / oldScale)`.
- **Touch pan:** single-finger `pointermove` delta applied to translate.
- **Touch pinch zoom:** two-pointer `pointermove` — distance delta between the two pointers drives scale; midpoint between them is the zoom center.
- **Fit to view:** calculates `scale = min(viewportW / stageW, viewportH / stageH) * 0.9` and centers the stage. Called on initial load and on button click.

### Controls
A small button overlaid in the bottom-right corner of the viewport (`position: absolute`, `z-index: 10`). Icon: ⊡ or a simple "fit" SVG. Styled to match the site theme (same border/background as edge labels).

### Zoom limits
Clamped to `0.2×` minimum and `4×` maximum to prevent accidental loss of content.

### JavaScript location
New `initCanvas(container)` function added to `base.html`'s inline script block. Called once per `.canvas-view` element on `DOMContentLoaded`. No external library dependency. Approximately 80–100 lines.

---

## Area 2 — Text Node Rendering

### Goal
Text nodes render the same markdown as notes: headings, links, bullet lists, blockquotes, code blocks, callouts, wiki-links, and all other Obsidian syntax.

### Change
Replace `_canvas_text_to_html(text)` in `canvas.py` with a call to `converters.render_markdown(text, canvas_path, url_index)`.

**One adjustment:** `render_markdown()` calls `strip_leading_h1()` which removes the first `# Heading` on the assumption it's the page title. In a canvas text node, any heading is content — not a title. The call must pass a flag or the text must be pre-processed to skip that step. Simplest approach: add an optional `skip_strip_h1=False` parameter to `render_markdown()` and pass `True` for canvas text nodes.

**Import:** `canvas.py` already imports from `config` and `obsidian_syntax`. It will need to import `render_markdown` from `converters`. This is a new dependency in the chain — acceptable since `canvas.py` is only called from `posts.py` which already imports `converters`.

---

## Area 3 — Edge Directionality

### Goal
Respect the jsoncanvas `fromEnd` / `toEnd` fields per spec. Currently InkStone always draws an arrow at `toNode` and nothing at `fromNode`.

### jsoncanvas spec
Each edge may declare:
- `toEnd: "arrow" | "none"` (default `"arrow"`)
- `fromEnd: "arrow" | "none"` (default `"none"`)

### Change
- Read `edge.get("toEnd", "arrow")` and `edge.get("fromEnd", "none")` for each edge.
- Conditionally apply `marker-end` and/or `marker-start` on the `<path>` element.
- The `<marker>` for `marker-start` points in the opposite direction — use `refX="0"` and reverse the path: `M10,0 L0,5 L10,10 Z`.
- Each unique `(stroke, has_start_arrow, has_end_arrow)` combination gets its own marker ID in `<defs>`.

---

## Area 4 — Visual Polish

### Viewport height
Switch from the padding-bottom aspect-ratio trick to an explicit height: `min(80vh, 600px)`. The aspect-ratio approach was necessary when the canvas was a static image; with a pannable stage it no longer applies.

### Node borders
Colored nodes (those with a `color` field) get `border-width: 2px` using the mapped color. Uncolored nodes keep the default `1px var(--border)`.

### Link nodes
Minor polish only (no URL fetching, no iframe). Show a small external-link icon (↗) before the domain name (bold), with the full URL in a smaller muted line below.

### Group nodes
Switch from `border: 2px dashed` to `border: 2px solid` with lower opacity (`opacity: 0.5` on the border color). If the group has a color set, tint the background with that color at very low opacity (e.g. 8%).

### Fit-to-view button
`position: absolute; bottom: 8px; right: 8px` within `.canvas-view`. Styled with `background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 4px 7px; cursor: pointer; font-size: 0.8rem`.

---

## Out of Scope

- Minimap
- URL preview fetching for link nodes (title/og:image)
- Rendering unpublished vault notes inside file node cards (title-only fallback is correct)
- Canvas `__featured` filename marker (separate feature)

---

## Files Changed

| File | Change |
|------|--------|
| `canvas.py` | Import `render_markdown`; replace `_canvas_text_to_html`; add `fromEnd`/`toEnd` marker logic; switch node positions to px; wrap nodes in `canvas-stage` div |
| `converters.py` | Add `skip_strip_h1` param to `render_markdown()` |
| `frontend/static/base.css` | Update `.canvas-view` height; add `.canvas-stage`; node border improvements; link node polish; group tint; fit button styles |
| `frontend/templates/base.html` | Add `initCanvas()` JS function; fit-to-view button injected per canvas |

---

## Testing

- Run local server against `BlogPages/` with the demo canvas.
- Verify pan/drag and scroll-zoom on desktop.
- Verify fit-to-view button centers all nodes.
- Verify pinch zoom on a touch device (or browser DevTools touch simulation).
- Add a text node with headings, links, and a list to the demo canvas; verify full markdown renders.
- Add an edge with `"fromEnd": "arrow"` to the demo canvas; verify bidirectional arrow renders.
- Check both themes (obsidian + omarchy).
