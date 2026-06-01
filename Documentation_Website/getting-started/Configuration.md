---
website: true
title: Configuration Reference
date: 2026-05-21
summary: All environment variables and .env options.
featured: true
priority: 2
---

InkStone is configured entirely through environment variables. Create a `.env` file in the project root:

```bash
VAULT_PATH=/path/to/your/obsidian/vault
SECRET_KEY=change-me-to-a-long-random-string
ACCESS_TOKEN=optional-master-unlock-key
HIDE_ATTRIBUTION=0
```

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `VAULT_PATH` | Yes | `./BlogPages` | Absolute path to your Obsidian vault directory. Falls back to `./BlogPages` if unset or missing. |
| `SECRET_KEY` | Recommended | `inkstone-dev-secret` | Flask session signing key. Sessions are invalidated on restart if not set. |
| `ACCESS_TOKEN` | No | — | Master key that unlocks **all** private notes. Set to a long random string. |
| `HIDE_ATTRIBUTION` | No | `0` | Set to `1` or `true` to remove the "built with InkStone" footer line. |
| `GISCUS_REPO` | No* | — | GitHub repo for Giscus comments (e.g. `user/repo`). All three Giscus vars required. |
| `GISCUS_REPO_ID` | No* | — | Giscus repo ID from [giscus.app](https://giscus.app). |
| `GISCUS_CATEGORY_ID` | No* | — | Giscus discussion category ID. |
| `VAULT_REPO` | No | — | Git URL to clone a private vault at Docker build time. |
| `WEBHOOK_SECRET` | No | — | Secret for validating GitHub webhook payloads on `/webhook`. |
| `URL_PATH_PREFIX` | No | — | Subpath prefix when serving under a subdirectory (e.g. `/inkstone`). Also accepted as `APPLICATION_ROOT`. |

*All three `GISCUS_*` variables must be set together to enable comments.

> [!tip] SECRET_KEY in production
> Generate a secure key with:
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```
> Set it as an environment variable or in `.env`. Without it, sessions (theme, unlocked private notes) reset every time the server restarts.
