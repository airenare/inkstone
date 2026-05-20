---
website: true
title: Installation
date: 2026-01-01
summary: "Requirements, install paths, and first-run checklist."
---

## Requirements

- Python 3.11 or newer
- Git

## Step by step

```bash
# 1. Clone the repository
git clone https://github.com/your-org/inkstone
cd inkstone

# 2. Install dependencies
pip install -r requirements.txt

# 3. Point at your vault
echo "VAULT_PATH=/path/to/your/vault" > .env

# 4. Run
python3 app.py
```

> [!tip] Use a virtual environment
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate
> pip install -r requirements.txt
> ```
> This keeps InkStone's dependencies isolated from your system Python.

## Docker alternative

If you'd rather not touch Python at all:

```bash
docker build -t inkstone .
docker run -p 8000:8000 -e VAULT_PATH=/vault -v /path/to/vault:/vault inkstone
```

See [[Docker]] for compose examples and private vault setup.

## First-run checklist

- [ ] Repository cloned
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `VAULT_PATH` set in `.env` or as an environment variable
- [ ] At least one note has `website: true` in frontmatter
- [ ] Server running (`python3 app.py`)
- [ ] Site visible at `http://localhost:5000`
