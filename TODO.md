# InkStone — Backlog

*Completed items live in [DONE.md](DONE.md).*

---

## P0 — High Priority

- [ ] **[Bug][Content Discovery] See also should exclude language variants of the same post** — in related-post selection, do not show sibling translations (same canonical post content in another `lang`); show only genuinely different posts.
- [ ] **[Bug][Canvas Publishing] Canvas publish marker gets removed by Obsidian** — current `.canvas` JSON keys (`"website": true`, `"title": "..."`) are stripped after editing in Obsidian. Replace with a durable publish signal or add a reliable workaround.

---

## P1 — Medium Priority

- [ ] **[Enhancement][Canvas UX] Canvas connectors need directionality** — replace plain curved lines with directional arrows so graph flow is clear and semantically closer to Obsidian canvas.
- [ ] **[Enhancement][Canvas UX] Render note content inside file cards** — file/note cards should show real scrollable note preview instead of title-only display.
- [ ] **[Tech Debt][Frontend] Remove Mermaid SVG background workaround** — adopt proper Mermaid v11 config/API so `fixSvgBg()` is no longer needed.
- [ ] **[Design][Branding] Logo polish pass** — refine provided logo concept/mock-up for geometry balance, contrast, and small-size legibility; ship final web SVG plus favicon-ready variants.

---

## P2 — Lower Priority

- [ ] **[Enhancement][Canvas UX] Upgrade canvas toward jsoncanvas-level experience** — overall canvas rendering is still basic and should move closer to `jsoncanvas.org` capabilities while matching site styling.
- [ ] **[Business][Domain] Register production domain** — secure `inkstone.dev` or a close alternative.
- [ ] **[Business][Hosting] Choose and set up production hosting** — evaluate and deploy in this order:
  1. **Fly.io** — Docker-native, fast path from repo root.
  2. **Render** — GitHub auto-deploy, easy setup.
  3. **Railway** — minimal config with `gunicorn`.
  4. **Hetzner VPS** — lowest recurring cost, manual infra.
  5. **DigitalOcean App Platform** — managed deployment from GitHub.
