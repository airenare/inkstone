---
website: true
title: Canvas Boards
date: 2026-05-21
summary: Publish Obsidian .canvas files as interactive boards with pan, zoom, and node previews.
featured: true
priority: 6
tags:
  - writing
  - canvas
---

## Publishing a canvas

Name the file with `__website` before the `.canvas` extension:

```
My Board__website.canvas
```

> [!warning] Use the filename marker
> Do **not** add `"website": true` inside the canvas JSON. Obsidian may overwrite the JSON on save and will erase it. The `__website` filename suffix is the only reliable way to publish a canvas.

The title is the filename with `__website` stripped: `My Board__website.canvas` → title "My Board", URL `/my-board`.

## Node types

| Node type | Rendered as |
|---|---|
| Text node | Markdown with full callout, checkbox, and Dataview support |
| File node | Scrollable HTML preview of the linked published post |
| Link node | Clickable card with the domain and an ↗ external link icon |
| Group node | Color-tinted background region grouping other nodes |

File nodes show the post's title and full body HTML. The linked vault file must be a published note — unpublished files render as an empty card.

## Edge directionality

Edges drawn with `fromEnd`/`toEnd` in Obsidian get SVG arrow markers pointing toward the target node. Bidirectional and undirected edges render without arrowheads.

## Embedding a canvas in a note

Embed a published canvas inline inside any markdown note:

```
![[My Board__website]]
![[My Board__website.canvas]]
```

Obsidian sometimes inserts the full vault-relative path when you use its link picker — that works too:

```
![[blog/My Board__website.canvas|My Board__website]]
```

The canvas renders as a fully interactive block — pan, zoom, wide mode, and all — right inside the note body. The canvas must be published (via the `__website` filename suffix) for the embed to resolve; if it isn't, the syntax is left as-is in the output.

Regular wiki-links (`[[My Board__website.canvas]]`) also resolve correctly — InkStone strips the path prefix, `.canvas` extension, and `__website` marker from both the URL and the displayed link text automatically.

[[InkStone_Docs/writing/My Writing Process__website.canvas|My Writing Process__website]]
![[InkStone_Docs/writing/My Writing Process__website.canvas|My Writing Process__website]]

## Controls

| Action | How |
|---|---|
| Pan | Click and drag on the canvas background |
| Zoom | Scroll wheel |
| Fit to view | Click the fit button (⛶) in the toolbar |
| Wide mode | Click the wide-view button (⛶) — canvas fills the window; press Esc to exit |
