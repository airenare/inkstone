# InkStone — Backlog

*Completed items live in [DONE.md](DONE.md).*

---

## P2 — Lower Priority

- [ ] **[Obsidian plugin] Stop the local server when Obsidian is hard-killed** — the plugin (`airenare/inkstone-obsidian-plugin`) starts `app.py` as a child; a crash or force-quit of Obsidian leaves it running. Add an env-gated stdin-EOF watcher in InkStone (e.g. `INKSTONE_EXIT_ON_STDIN_EOF=1`, exit when stdin closes; Werkzeug's reloader child inherits stdin), then have the plugin set the flag and keep a pipe on stdin. Needs both sides; target the plugin's next version.

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
