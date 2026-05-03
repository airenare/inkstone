# InkStone — Backlog

*Completed items live in [DONE.md](DONE.md).*

---
## P0 - High Priority

Before next task - The working directory was renamed from OnyxFolio to InkStone. Make sure everything works with this name change (docs, memory, index, etc.)

## P1 — Medium Priority

- [ ] **[Design][Branding] Logo polish pass** — refine provided logo concept/mock-up for geometry balance, contrast, and small-size legibility; ship final web SVG plus favicon-ready variants.

- [ ] **[Enhancement][Canvas UX]** Add wide mode for canvas pages: a button that user can press to make the canvas span almost the whole window width and height. Might be necessary to view a complex canvas and don't feel restrained.

- [ ] **[Enhancement][Canvas UX]** Make the lines connecting the cards more curvy at the ends. They should curve from vertical to horizontal with less radius.

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
