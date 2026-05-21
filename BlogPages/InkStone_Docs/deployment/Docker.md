---
website: true
title: Docker
date: 2026-01-01
summary: Run InkStone in a container with a mounted vault or a cloned private repo.
featured: true
priority: 1
---

## Quick start with docker compose

The repo includes a `docker-compose.yml`. Create a `.env` file next to it:

```bash
VAULT_REPO=https://<token>@github.com/you/your-vault-repo
WEBHOOK_SECRET=some-long-random-string
```

Then start the container:

```bash
docker compose up -d
```

On first start the entrypoint clones the vault into the container. On subsequent starts it does a `git pull` to fetch the latest notes. The site is served at `http://localhost:8000`.

> [!tip] Automatic updates
> Set up a GitHub webhook pointing at `http://yourhost:8000/webhook` with the same `WEBHOOK_SECRET` to trigger a vault pull on every push — no restart needed.

## Build and run manually

```bash
docker build -t inkstone .
docker run -p 8000:8000 \
  -e VAULT_REPO=https://<token>@github.com/you/your-vault-repo \
  inkstone
```

## Mount a local vault instead

If you prefer to mount a local directory rather than cloning from git, omit `VAULT_REPO` and bind-mount your vault to `/vault`:

```bash
docker run -p 8000:8000 \
  -v /path/to/your/vault:/vault \
  inkstone
```

Or with compose — replace the contents of `docker-compose.yml` with:

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=change-me-to-a-long-random-string
    volumes:
      - /path/to/your/vault:/vault
    restart: unless-stopped
```

## Passing additional environment variables

```bash
docker run -p 8000:8000 \
  -e VAULT_REPO=https://<token>@github.com/you/vault \
  -e SECRET_KEY=mysecretkey \
  -e ACCESS_TOKEN=masterkey \
  inkstone
```

Or pass a file:

```bash
docker run -p 8000:8000 --env-file .env inkstone
```

See [[Configuration Reference]] for the full list of supported environment variables.
