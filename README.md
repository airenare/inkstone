# Obsidian Blog Engine

A lightweight Python/Flask server that turns an **Obsidian vault into a website**. Write in Obsidian, push to GitHub, see it live — no export step, no build pipeline, no CMS.

---

## How it works

Your vault's folder structure maps directly to URL paths:

| Vault path | URL |
|---|---|
| `blog/My Post.md` | `/blog/My-Post` |
| `gallery/Neon Dreams.md` | `/gallery/Neon-Dreams` |
| `books/Anathem.md` | `/books/Anathem` |

A note tagged `homepage` serves its content at the section root (`/`, `/blog`, `/gallery`). A note tagged `listing` renders an auto-generated post index at the section root instead.

---

## Features

- **Native Obsidian syntax** — callouts (`> [!tip]`), wiki-links (`[[Note]]`), image embeds (`![[file.jpg]]`), checkboxes — all rendered without any client-side plugins
- **Dataview queries** — `TABLE` queries in fenced ` ```dataview ``` ` blocks are executed server-side and rendered as HTML tables; queries can reference any note in the vault, including unpublished ones
- **Lightbox gallery** — `![[img.jpg]]` on its own line becomes a lightbox-enabled image; multiple images on one line become a slider
- **Syntax highlighting** — fenced code blocks get language labels, a copy button, and Tokyo Night Dark theme via highlight.js
- **Banner images** — set `banner: "url"` in frontmatter for a hero image; `banner_x`/`banner_y` control the focal point
- **Private notes** — notes without a `website` tag are invisible as web pages but fully queryable by Dataview; navigating to their URL shows a styled placeholder with instructions to publish
- **Hot-reload** — the server watches file modification times and reloads the vault on any change, no restart needed
- **Search** — full-text search across all published posts at `/search`
- **Auto-listings** — sections with no explicit index file get an auto-generated listing page

---

## Frontmatter reference

```yaml
---
tags:
  - website      # required to publish the note as a web page
  - homepage     # serve this note's content at the section root URL
  - listing      # auto-generate a post index at the section root URL
  - featured     # highlight this post in the section's featured area
date: 2026-01-15
title: My Post   # optional; overrides H1 and filename
slug: my-post    # optional; auto-generated from title if omitted
priority: 0      # featured posts only; lower = higher (date breaks ties)
summary: "..."   # shown on listing pages; auto-derived from content if omitted
banner: "https://example.com/image.jpg"
banner_x: 0.5   # horizontal focal point (0–1)
banner_y: 0.4   # vertical focal point (0–1)
---
```

---

## Running locally

**Requirements:** Python 3.11+

```bash
git clone https://github.com/you/obsidian-blog-engine
cd obsidian-blog-engine

pip install -r requirements.txt

# Point at your vault (or omit to use the bundled demo vault)
echo "VAULT_PATH=/path/to/your/vault" > .env

python3 app.py
# → http://127.0.0.1:8000
```

The server hot-reloads when vault files change.

---

## Docker

```bash
docker build -t obsidian-blog .
docker run -p 8000:8000 -v /path/to/vault:/vault obsidian-blog
```

If `/vault` is not mounted or doesn't exist, the server falls back to the bundled `BlogPages/` demo vault.

---

## Deployment (Coolify + separate vault repo)

This is the recommended production setup. Your Obsidian vault lives in its own private GitHub repo. Pushing to it triggers a rebuild of the blog.

### 1. Dockerfile build arg

Pass your vault repo URL as the `VAULT_REPO` build arg in Coolify's build settings:

```
VAULT_REPO=https://<token>@github.com/you/your-vault
```

Use a [fine-grained personal access token](https://github.com/settings/tokens) scoped to read-only on that repo. The `.git` directory is removed after cloning so the token doesn't persist in the image.

### 2. Vault webhook → Coolify redeploy

In your vault's GitHub repo:

- **Settings → Webhooks → Add webhook**
- Payload URL: your Coolify app's redeploy webhook (found in the app's **Webhooks** tab)
- Content type: `application/json`
- Trigger: **Just the push event**

From then on:

```
edit note in Obsidian → git push vault → GitHub webhook → Coolify rebuild → site updated
```

---

## Project structure

```
app.py           Flask app, single catch-all route
config.py        Loads .env, VAULT_PATH, tag constants
converters.py    Markdown pipeline + Dataview query engine
posts.py         Two-pass vault loader, ALL_POSTS, SECTION_ROUTES, DATAVIEW_INDEX
frontend/
  templates/     base, index, post, listing, private, search
  static/        obsidian.css, callouts.css, code.css
BlogPages/       Bundled demo vault (fallback when no VAULT_PATH set)
Dockerfile
```

The import chain is strictly one-way: `config ← converters ← posts ← app`.

---

## Demo vault

`BlogPages/` ships with the engine as a working example:

| URL | Content |
|---|---|
| `/` | Engine homepage |
| `/blog` | Blog listing with featured posts |
| `/blog/Test-Post-One` | Callouts, checkboxes, images |
| `/blog/Test-Post-Two` | Slider gallery |
| `/gallery` | Image gallery with lightbox |
| `/books` | Dataview-powered bookshelf |
| `/books/Project-Hail-Mary` | Example of a private note placeholder |

---

## License

MIT
