---
website: true
title: Docker
date: 2026-01-01
summary: "Run InkStone in a container with a mounted vault or a cloned private repo."
---

## Basic run

Mount your vault as a volume and set `VAULT_PATH`:

```bash
docker run -p 8000:8000 \
  -e VAULT_PATH=/vault \
  -v /path/to/your/vault:/vault \
  inkstone
```

## Build from source

```bash
docker build -t inkstone .
docker run -p 8000:8000 -e VAULT_PATH=/vault -v /path/to/vault:/vault inkstone
```

## docker-compose.yml

```yaml
services:
  inkstone:
    build: .
    ports:
      - "8000:8000"
    environment:
      - VAULT_PATH=/vault
      - SECRET_KEY=change-me-to-a-long-random-string
      - HIDE_ATTRIBUTION=0
    volumes:
      - /path/to/your/vault:/vault
    restart: unless-stopped
```

Run with:

```bash
docker compose up -d
```

## Private vault at build time

To clone a private vault during the Docker build (useful when you don't want to mount a local directory):

```bash
docker build \
  --build-arg VAULT_REPO=https://token@github.com/you/vault-repo \
  -t inkstone .
```

The vault is cloned into the image at build time. To update it, rebuild the image and redeploy.

## Passing environment variables

Inline with `-e`:

```bash
docker run -p 8000:8000 \
  -e VAULT_PATH=/vault \
  -e SECRET_KEY=mysecretkey \
  -e ACCESS_TOKEN=masterkey \
  -v /path/to/vault:/vault \
  inkstone
```

From a file with `--env-file`:

```bash
docker run -p 8000:8000 --env-file .env -v /path/to/vault:/vault inkstone
```

See [[Configuration Reference]] for the full list of supported environment variables.
