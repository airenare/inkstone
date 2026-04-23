# OnyxFolio — Backlog

*Completed items live in [DONE.md](DONE.md).*

---

## Immediate  *(small, pick up and finish in one session)*

- **Inline Dataview `dv.pages()` expression** — extend `convert_dataview_inline` in `dataview.py` beyond `this.*` to handle `` `= dv.pages("#tag").length` `` and similar cross-note expressions. Detect `dv.pages(selector)`, run filtered count/list against `DATAVIEW_INDEX`. Start with `.length` and `FROM #tag`; keep scope narrow.

- **Obsidian template workflow** — Create a template or workflow to auto-generate notes with the correct frontmatter. Check if Obsidian's core Templates plugin is sufficient or if Templater/QuickAdd is still needed.

---

## Polish & Bugs

- **Mermaid inner background** — Mermaid v11 injects an inline `style="background: ..."` on the SVG element that overwrites the transparent background. The current `fixSvgBg()` post-render strip in `base.html` is a workaround. Investigate the correct Mermaid v11 initialisation API: `mermaid.initialize({ htmlLabels: false, ... })` or `suppressErrorRendering`. Goal: remove the JS workaround and let Mermaid initialise cleanly.

- **Lowercase URLs audit** — slugify already lowercases; verify that vault folders with mixed-case names (e.g. `Blog/`, `Gallery/`) produce lowercase section URLs in practice. If not, apply `.lower()` to each path segment in `_section_from_filepath`. Mark done once confirmed.

---

## Ideas  *(not committed — explore when the time is right)*

- **System theme option** — third theme selector state "System" that follows `prefers-color-scheme`. Currently the toggle is binary dark/light. Implementation: read `window.matchMedia("(prefers-color-scheme: light)").matches` when no `localStorage.theme` is set; add third button state; remove saved localStorage entry when "System" is selected.

- **Canvas file rendering** — Obsidian `.canvas` files are JSON graphs of nodes and edges. Render as a read-only visual board: parse JSON, position `<div>`s or draw SVG to mirror the layout. Effort: high; reward: unique.

- **`dv.pages()` full expression support** — after the `.length` case, support richer expressions: field access (`dv.pages("#tag").file.name`), sorting, limiting. Makes inline Dataview genuinely powerful. Keep server-side.

- **Private note access control** — opt-in password/token gate (HTTP Basic or query-param token) to share drafts without publishing. Niche use case.

---

## Business / External

- **Domain** — register `onyxfolio.com`, `.dev`, or `.app`

- **Hosting** — try in order of simplicity:
  1. **Fly.io** — Docker-native, `fly deploy` from repo root, free tier
  2. **Render** — GitHub auto-deploy, free tier (spin-down on idle)
  3. **Railway** — minimal config, generous free tier, `gunicorn` start command
  4. **Hetzner VPS** — €4/mo, persistent, gunicorn + nginx reverse proxy
  5. **DigitalOcean App Platform** — auto-deploy from GitHub like Render
