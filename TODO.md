# InkStone — Backlog

*Completed items live in [DONE.md](DONE.md).*

---
## P1 — Medium Priority

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
