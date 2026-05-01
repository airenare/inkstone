# InkStone — Backlog

*Completed items live in [DONE.md](DONE.md).*

---

## P1 — Medium Priority

- [ ] **[Enhancement][Bases] Respect Obsidian `.base` view filters** — Bases can be filtered in Obsidian; filter definitions live in the `.base` file under `views` (e.g. `type: table`, `filters`, `order`). InkStone should parse and apply the same filter tree the app uses when resolving rows, not only ad-hoc `website: true` table logic. Example shape:

  ```yaml
  views:
    - type: table
      name: Table
      filters:
        and:
          - file.tags.contains("inkstone")
      order:
        - file.name
        - file.folder
        - website
        - type
        - summary
  ```

- [ ] **[Enhancement][Bases] Durable publish + feature flags for `.base` files** — `.base` is not comfortable to edit as plain YAML for `website:` / `featured:` inside Obsidian; today those flags may require external editing. Add a filename-based convention (similar to canvas `Title__website.canvas`), e.g. optional suffix tokens for publish and featured so Obsidian re-saves do not strip intent — design markers, document, and wire `bases.py` / `posts.py` pass 3.

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
