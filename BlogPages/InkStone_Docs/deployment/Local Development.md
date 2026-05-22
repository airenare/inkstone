---
website: true
title: Local Development
date: 2026-05-21
summary: Run InkStone locally with hot-reload for writing and development.
featured: true
priority: 0
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

Edit any vault file and refresh the browser — no restart needed. InkStone watches modification times on every request and reloads automatically when anything changes.

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
