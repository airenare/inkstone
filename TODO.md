# OnyxFolio — Backlog

*Completed items live in [DONE.md](DONE.md).*

---

## Immediate  *(small, pick up and finish in one session)*

- **Inline Dataview `dv.pages()` expression** — extend `convert_dataview_inline` in `dataview.py` beyond `this.*`. **Stage 1 (narrow):** detect `` `= dv.pages("#tag").length` ``, run filtered count against `DATAVIEW_INDEX`. **Stage 2 (later):** richer expressions — field access (`dv.pages("#tag").file.name`), sorting, limiting. Keep server-side.

- **Lowercase URLs audit** — `slugify` already lowercases slugs; verify that vault folders with mixed-case names (e.g. `Blog/`, `Gallery/`) produce lowercase section URLs in practice. If not, apply `.lower()` to each path segment in `_section_from_filepath`. Mark done once confirmed.

---

## Polish & Bugs

- **Mermaid inner background** — Mermaid v11 injects an inline `style="background: ..."` on the SVG that overwrites transparent background. The current `fixSvgBg()` strip in `base.html` is a workaround. Investigate the correct v11 init API (`mermaid.initialize({ ... })`) and remove the JS workaround.

---

## Ideas  *(not committed — explore when the time is right)*

- **System theme option** — third toggle state "System" that follows `prefers-color-scheme`. Read `window.matchMedia("(prefers-color-scheme: light)").matches` when no `localStorage.theme` is set; add third button state; remove saved entry when "System" is selected.

- **Canvas file rendering** — Obsidian `.canvas` files are JSON graphs of nodes and edges. Render as a read-only visual board: parse JSON, position `<div>`s or draw SVG. Effort: high; reward: unique.

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
