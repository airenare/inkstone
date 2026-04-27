---
website: true
title: Start Here
menu_order: 0
date: 2026-04-21
summary: "Get InkStone running and your first note live — three paths to choose from."
---

# Start Here

Get your Obsidian vault live on the web. Pick one path below.

---

## Option A — Run locally

**Requirements:** Python 3.11+, Git

```bash
git clone https://github.com/airenare/inkstone
cd inkstone
pip3 install -r requirements.txt
python3 app.py
# → http://127.0.0.1:8000
```

To serve your own vault instead of this demo:

```bash
echo "VAULT_PATH=/path/to/your/obsidian/vault" > .env
python3 app.py
```

The server watches your files and reloads automatically — no restart needed.

---

## Option B — Docker

```bash
git clone https://github.com/airenare/inkstone
cd inkstone
docker build -t inkstone .
docker run -p 8000:8000 -v /path/to/your/vault:/vault inkstone
# → http://127.0.0.1:8000
```

If no `/vault` is mounted, the bundled demo vault loads instead.

---

## Option C — Deploy with Coolify

For a production site that updates automatically when you push your vault to GitHub:

→ See the [Deployment guide](https://antonbakulin.com/inkstone/deployment) for step-by-step instructions.

---

## Your first published note

Add `website: true` to any note's frontmatter:

```yaml
---
website: true
title: My First Post
date: 2026-01-15
---

Write whatever you want here.
```

That note is now live. Its URL is `/my-first-post` if it's in the vault root, or `/section/my-first-post` if it's in a subfolder.

---

## Vault structure basics

| Vault path                            | URL             |
| ------------------------------------- | --------------- |
| `Home.md` (with `type: homepage`)     | `/`             |
| `blog/Blog.md` (with `type: listing`) | `/blog`         |
| `blog/My Post.md`                     | `/blog/my-post` |
| `About.md`                            | `/about`        |

---

## Next steps

Full configuration reference — theming, Dataview, multilingual, deployment, and more:

→ [antonbakulin.com/inkstone](https://antonbakulin.com/inkstone)
