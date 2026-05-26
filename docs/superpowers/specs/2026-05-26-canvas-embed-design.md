# Canvas Embed in Notes — Design Spec

**Date:** 2026-05-26  
**Status:** approved

## Problem

Canvas boards are published as standalone pages but can't be referenced inline inside a regular note. Authors who want to use a canvas as an interactive diagram inside a post have no way to do so.

## Goal

Allow any `.canvas` file in the vault to be embedded inline inside a markdown note using the standard Obsidian embed syntax: `![[CanvasName]]` or `![[CanvasName.canvas]]`. The embed renders as a scrollable, interactive SVG block within the host page — the same SVG output the standalone page produces, minus scrollable post-content previews inside file-node cards (link + title only).

## Non-goals

- Post-content previews inside embedded file nodes (architectural sequencing conflict; can be revisited)
- Slider or multi-embed behavior (canvas embeds are always block-level)
- Size customisation via pipe syntax (fixed 400 px height covers the typical use case)

## Architecture

### New function: `convert_canvas_embed(md, url_index)`

Lives in **`converters.py`** (not `canvas.py`) to avoid a circular import: `canvas.py` already imports `render_markdown` from `converters.py` at module level; putting the embed converter in `converters.py` with a lazy `from canvas import render_canvas` inside the function body breaks the cycle cleanly.

**Algorithm:**

1. Walk `VAULT_PATH` for all `*.canvas` files; build `canvas_index: {stem.lower(): filepath}` and `{slugify(stem).lower(): filepath}` entries.
2. If `canvas_index` is empty, return `md` unchanged.
3. Apply a regex across `md` that matches `![[Name]]` and `![[Name.canvas]]` (with optional `|alias` suffix), skipping lines inside fenced code blocks (same fence-marker tracking used by all other converters).
4. For each match:
   - Extract stem, look up in `canvas_index`.
   - If not found → return match unchanged (let `convert_transclusion` handle it).
   - If found → call `render_canvas(filepath, url_index=url_index, post_html_by_url=None, post_title_by_url=None)` and wrap in `<div class="canvas-embed">…</div>`.
   - On exception → emit `<em class="canvas-embed-error">Canvas error: {stem}</em>`.

### Pipeline insertion

In `render_markdown()` in `converters.py`:

```
convert_media()          ← consumes image/video/audio embeds
convert_canvas_embed()   ← NEW: consumes canvas embeds (any remaining ![[]])
convert_transclusion()   ← consumes note transclusions
convert_links()
…
```

`convert_media()` does not touch `![[name.canvas]]` (`.canvas` is not in `_MEDIA_EXTS`) or `![[name]]` without an extension, so all canvas embeds survive to the new step.

### `render_canvas()` call parameters

- `url_index` passed through from `render_markdown` — file nodes inside the canvas link to their published URLs.
- `post_html_by_url=None`, `post_title_by_url=None` — node content preview is omitted; nodes show the linked title and a "view" link, same as any unresolved file node in the standalone renderer.

## CSS

`.canvas-embed` wrapper added to `obsidian.css` and `omarchy.css`:

```css
.canvas-embed {
    width: 100%;
    height: 400px;
    overflow: auto;
    border: 1px solid var(--color-border, #444);
    border-radius: 8px;
    margin: 1.5em 0;
    background: var(--color-bg, #1e1e2e);
}
```

The inner SVG already fills its bounding box; `overflow: auto` gives horizontal + vertical scrolling when the canvas is wider or taller than 400 px.

## Affected files

| File | Change |
|------|--------|
| `converters.py` | Add `convert_canvas_embed()`; insert call in `render_markdown()` |
| `frontend/static/obsidian.css` | Add `.canvas-embed` styles |
| `frontend/static/omarchy.css` | Add `.canvas-embed` styles |
| `tests/fixtures/vault/blog/dv_post.md` | Add an `![[…]]` canvas embed example |
| `tests/fixtures/vault/blog/embed_test__website.canvas` (new) | Minimal fixture canvas for testing |
| `tests/unit/test_canvas_embed.py` (new) | Unit tests for `convert_canvas_embed` |
| `tests/integration/test_routes.py` | Integration assertion that embed renders |

## Test plan

**Unit tests (`test_canvas_embed.py`):**
- Canvas name matches by stem → `canvas-embed` div present in output.
- Canvas name with `.canvas` extension → same result.
- Unknown name → `![[...]]` left untouched.
- Inside fenced code block → untouched.
- Canvas file raises exception → `canvas-embed-error` span.

**Integration test:**
- Fixture post contains `![[embed_test]]`; response HTML includes `class="canvas-embed"`.
- Response HTML does NOT contain the literal `![[embed_test]]` string.
