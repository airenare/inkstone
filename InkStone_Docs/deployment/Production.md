---
website: true
title: Production Deployment
date: 2026-01-01
summary: "Deploy with Coolify, configure webhooks, and set up SSL."
---

> [!warning] Use gunicorn in production
> Never run `python3 app.py` in production — it starts Flask's development server which is single-threaded and not safe for public traffic. Always use gunicorn.

## Coolify (recommended)

[Coolify](https://coolify.io) is a self-hosted PaaS that handles Docker builds, SSL, and deployments.

1. Add a new resource → **Docker Compose** or **Dockerfile**
2. Set the build arg `VAULT_REPO` to your vault's Git URL (if cloning at build time)
3. Set environment variables: `SECRET_KEY`, `VAULT_PATH`, `HIDE_ATTRIBUTION`, etc.
4. Set the exposed port to `8000`
5. Enable **Let's Encrypt** for automatic SSL
6. Deploy

On each deploy, Coolify builds the image, pulls the latest vault (if using `VAULT_REPO`), and restarts the container.

## Webhook for live updates

To update the site content without redeploying:

1. Set `WEBHOOK_SECRET` in your environment:
   ```bash
   WEBHOOK_SECRET=a-random-secret-string
   ```
2. Add a GitHub webhook on your vault repository:
   - **Payload URL**: `https://yourdomain.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: same value as `WEBHOOK_SECRET`
   - **Events**: Just the push event

On every push to the vault repo, GitHub sends a POST to `/webhook`. InkStone validates the signature with `WEBHOOK_SECRET`, then pulls the latest vault content and reloads — no container restart needed.

## Subpath hosting

If InkStone is hosted at a path prefix rather than the root (e.g. `https://example.com/inkstone/`):

```bash
URL_PATH_PREFIX=/inkstone
```

All generated attachment URLs, nav links, and feeds will include the prefix.

## SSL

InkStone itself is HTTP only. SSL termination should be handled by a reverse proxy:

- **Coolify** — built-in Let's Encrypt
- **Caddy** — automatic HTTPS with a `Caddyfile`
- **Nginx** — configure as a proxy pass to `localhost:8000` with Certbot

## SECRET_KEY

Set a long random string to persist visitor sessions (theme preference, unlocked private notes) across restarts:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Without it, every server restart invalidates all sessions.
