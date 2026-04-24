# OnyxFolio — Backlog

*Completed items live in [DONE.md](DONE.md).*

---

## Immediate  *(small, pick up and finish in one session)*

- **Inline Dataview `dv.pages()` expression** — extend `convert_dataview_inline` in `dataview.py` beyond `this.*`. **Stage 1 (narrow):** detect `` `= dv.pages("#tag").length` ``, run filtered count against `DATAVIEW_INDEX`. **Stage 2 (later):** richer expressions — field access (`dv.pages("#tag").file.name`), sorting, limiting. Keep server-side.

---

## Polish & Bugs

- **Mermaid inner background** — Mermaid v11 injects an inline `style="background: ..."` on the SVG that overwrites transparent background. The current `fixSvgBg()` strip in `base.html` is a workaround. Investigate the correct v11 init API (`mermaid.initialize({ ... })`) and remove the JS workaround.

---

## Ideas  *(not committed — explore when the time is right)*

- **Canvas file rendering** — Obsidian `.canvas` files are JSON graphs of nodes and edges. Render as a read-only visual board: parse JSON, position `<div>`s or draw SVG. Effort: high; reward: unique.

---

## Business / External

- **Domain** — register `onyxfolio.com`, `.dev`, or `.app`

- **Hosting** — try in order of simplicity:
  1. **Fly.io** — Docker-native, `fly deploy` from repo root, free tier
  2. **Render** — GitHub auto-deploy, free tier (spin-down on idle)
  3. **Railway** — minimal config, generous free tier, `gunicorn` start command
  4. **Hetzner VPS** — €4/mo, persistent, gunicorn + nginx reverse proxy
  5. **DigitalOcean App Platform** — auto-deploy from GitHub like Render
