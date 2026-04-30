# InkStone — Backlog

*Completed items live in [DONE.md](DONE.md).*

---

## Immediate  *(small, pick up and finish in one session)*

---

## Polish & Bugs

- **Canvas is extremely basic** - we need something much more https://jsoncanvas.org/ looking. It can still be looking like a webpage of our website, but the contents need to be much more advanced. For example, there is a way to insert a whole note in a card. Very powerful tool. Current state of implementation in our engine is just a card with a link to the post.

- **Marking canvas to be published** - is done by editing the json file (.canvas) and adding two more key-value pairs ("website": true, "title": "my title"). Which works until you try to edit this .canvas in obsidian again. Once it's opened in obsidian, these key-value pairs are removed, and the page is not posted anymore. Either we need another way to mark canvas for publishing, or need to find a workaround.

- **Mermaid inner background** — Mermaid v11 injects an inline `style="background: ..."` on the SVG that overwrites transparent background. The current `fixSvgBg()` strip in `base.html` is a workaround. Investigate the correct v11 init API (`mermaid.initialize({ ... })`) and remove the JS workaround.

---

## Ideas  *(not committed — explore when the time is right)*

- **Canvas file rendering** — Obsidian `.canvas` files are JSON graphs of nodes and edges. Render as a read-only visual board: parse JSON, position `<div>`s or draw SVG. Effort: high; reward: unique.

---

## Business / External

- **Domain** — register `inkstone.dev` or similar

- **Hosting** — try in order of simplicity:
  1. **Fly.io** — Docker-native, `fly deploy` from repo root, free tier
  2. **Render** — GitHub auto-deploy, free tier (spin-down on idle)
  3. **Railway** — minimal config, generous free tier, `gunicorn` start command
  4. **Hetzner VPS** — €4/mo, persistent, gunicorn + nginx reverse proxy
  5. **DigitalOcean App Platform** — auto-deploy from GitHub like Render
