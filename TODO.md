# InkStone — Backlog

*Completed items live in [DONE.md](DONE.md).*

---

## P2 — Lower Priority

- [ ] **[Obsidian plugin] Migrate the settings tab to the declarative settings API** — `InkStone Preview` (`airenare/inkstone-obsidian-plugin`) still builds its settings screen imperatively in `display()`. Obsidian 1.13+ wants `getSettingDefinitions()` (clears three directory-review warnings and makes the settings show up in Obsidian's settings search), and `this.update()` instead of `this.display()`. The custom pieces (site-folder field with Browse button, live validation status line, Python path auto-fill) need rebuilding in the declarative model. Do it together with Anton, since it has to be click-tested in a running Obsidian. Next plugin version.

- [ ] **[Business][Analytics] Discover live InkStone sites** — two approaches:
  1. **Passive:** Search for `"built with InkStone"` attribution footer (e.g. via PublicWWW or Google); check GitHub fork count.
  2. **Active:** Add opt-out telemetry ping on server boot (version + Python version only, no PII); disclose in README; honor `INKSTONE_TELEMETRY=0` env var.

- [ ] **[Business][Domain] Register production domain** — secure `inkstone.dev` or a close alternative.
- [ ] **[Business][Hosting] Choose and set up production hosting** — evaluate and deploy in this order:
  1. **Fly.io** — Docker-native, fast path from repo root.
  2. **Render** — GitHub auto-deploy, easy setup.
  3. **Railway** — minimal config with `gunicorn`. (!)
  4. **Hetzner VPS** — lowest recurring cost, manual infra.
  5. **DigitalOcean App Platform** — managed deployment from GitHub.
