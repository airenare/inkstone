---
website: true
title: Local Development
date: 2026-05-21
summary: Run InkStone locally with hot-reload for writing and development.
featured: true
priority: 0
tags:
  - deployment
---

## Requirements

- Python 3.11 or newer
- pip

## Setup and run

```bash
git clone https://github.com/airenare/inkstone.git
cd inkstone
pip install -r requirements.txt
python3 app.py
```

## Set VAULT_PATH

Create a `.env` file in the project root:

```bash
VAULT_PATH=/path/to/your/obsidian/vault
```

Or pass it inline:

```bash
VAULT_PATH=/path/to/vault python3 app.py
```

If `VAULT_PATH` is unset, InkStone falls back to `./BlogPages` (the demo vault in the repo).

## Hot-reload

Edit any vault file and refresh the browser. No restart needed. InkStone watches modification times on every request and reloads automatically when anything changes.

## Change the port

`python3 app.py` listens on port 8000 by default. Set `PORT` to use another one:

```bash
PORT=8001 python3 app.py
```

## Dev source-map API

Set `INKSTONE_DEV_API=1` to enable a development-only endpoint, `GET /__inkstone/source-map`. It returns JSON listing every vault file (`.md`, `.base`, `.canvas`) with its served URL:

```json
{"version": "1.57.0", "files": [{"file": "blog/post.md", "url": "/blog/post", "published": true, "private": false, "has_own_token": false}]}
```

`file` is relative to the vault with forward slashes. Unpublished notes are `private: true` and keep their real URL, because the master `ACCESS_TOKEN` (or the note's own `access_token`, flagged by `has_own_token`) unlocks them at that URL. `url` is `null` only for unpublished homepage, listing, and feed notes. Unpublished `.base` and `.canvas` files are absent from the map; treat a missing file as unpublished. Without the flag the route does not exist and returns 404. Don't enable it in production.

## Production mode locally

To test with gunicorn (closer to production behaviour):

```bash
gunicorn -b 0.0.0.0:8000 app:app
```

Note: gunicorn does not hot-reload by default. Use `--reload` flag during development only:

```bash
gunicorn --reload -b 0.0.0.0:8000 app:app
```

> [!tip] Use a virtual environment
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate
> pip install -r requirements.txt
> ```
> Keeps dependencies isolated and avoids conflicts with system packages.
