# OnyxFolio

> Your notes, published.

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

Notes placed in the **vault root** (no subfolder) are served at `/slug` with no section prefix. They don't appear in any auto-generated listing — ideal for standalone pages like About, Contact, or Uses. Link to them via `[[wiki-links]]` from your content, or pin them to the top nav with `menu_order` in frontmatter.

---

## Features

### Obsidian-native syntax

- **Callouts** — `> [!tip]` boxes; all standard Obsidian types; collapsible (`> [!type]-`) or pinned open (`> [!type]+`); rendered as native `<details>`
- **Wiki-links** — `[[Note]]`, `[[Note|alias]]`, `[[Note#Heading]]`, `[[Note^block-id]]` — resolved across all vault sections even when filename, title, and slug differ
- **Image embeds** — `![[file.jpg]]` on its own line becomes a lightbox-enabled image; multiple on one line become a slider; `![[photo.jpg|Caption]]` renders a `<figcaption>`
- **Note transclusion** — `![[Note Title]]` or `![[Note Title#Heading]]` embeds another note (or just one section) inline
- **Audio embeds** — `![[file.mp3]]` → `<audio>` element; `.mp3`, `.ogg`, `.wav`, `.flac`, `.m4a` supported
- **Checkboxes** — `- [ ]` / `- [x]` → HTML checkbox lists with proper nesting
- **Highlights** — `==text==` → `<mark>` tags
- **Footnotes** — `[^1]` / `[^note]` syntax with backlinks
- **Block references** — `^block-id` on a paragraph creates an anchor target; `[[Note^id]]` links scroll to it
- **Aliases** — `aliases:` frontmatter registers alternate wiki-link names that resolve to the same post

### Math & diagrams

- **Mermaid** — fenced ` ```mermaid ``` ` blocks rendered client-side via Mermaid.js; adapts to dark and light theme automatically
- **LaTeX / KaTeX** — `$inline$` and `$$block$$`; expressions protected from the markdown parser before rendering

### Dataview

- **Table and list queries** — `TABLE` and `LIST` queries in fenced ` ```dataview ``` ` blocks executed server-side; supports `FROM`, `WHERE`, `SORT`, `LIMIT`, `GROUP BY` with per-group headings
- **Inline queries** — `` `= this.field` `` expressions in prose evaluated against the current note's frontmatter

### Publishing & structure

- **Private notes** — notes without `website: true` are invisible as web pages but fully queryable by Dataview; navigating to their URL shows a styled placeholder
- **Auto-listings** — folders with no explicit index file get an auto-generated listing page automatically
- **Banner images** — `banner: "url"` in frontmatter for a hero image; `banner_x`/`banner_y` control the focal point
- **Vault-wide attachments** — media resolution falls back to vault root `_attachments/`, then `ATTACHMENTS_PATH` from `.env`
- **Favicon** — default OnyxFolio favicon included; override by placing `favicon.ico`, `favicon.png`, or `favicon.svg` in your vault root
- **Author field** — `author:` frontmatter (string or list) shown below the post title and in JSON-LD
- **Date last modified** — `updated:` frontmatter shows "Updated …" in post meta and populates `dateModified` in JSON-LD
- **Site icon** — `icon: path/to/image` shows an image beside the site title; cascades to all child pages unless overridden
- **Custom header title** — `site_title: My Brand` changes the displayed title in the header; also cascades to child pages

### Navigation & discovery

- **Full-text search** — `/search` with tag filter; opt-in via `show_search: true` on the root homepage
- **Tags** — `tags:` frontmatter + inline `#hashtag` body mentions; clickable badges; `/tag/<name>` archive pages; `/tags` index opt-in via `show_tags: true`
- **Breadcrumb navigation** — `Home › Section › Post` trail; useful for nested paths like `/gallery/arts/post`
- **Nav pinning** — `menu_order: N` in any note's frontmatter pins it to the top nav; lower = further left
- **Related posts** — automatic "See also" section scored by shared tags and section; top four results
- **Next / previous navigation** — "← Older" / "Newer →" links at the bottom of each post, ordered by date within the same section
- **Pagination** — listing pages paginate at 20 posts per page
- **Reading time** — estimated reading time shown on post pages and listing cards

### SEO & feeds

- **RSS feed** — latest 20 posts at `/feed.xml`; per-section feeds at `/blog/feed.xml`, `/gallery/feed.xml`, etc.
- **Sitemap** — auto-generated from all published routes at `/sitemap.xml`
- **OpenGraph / Twitter Card** — per-page meta tags for rich link previews; uses banner image if set
- **JSON-LD structured data** — Article, Book, and WebSite schemas for rich Google results

### Developer experience

- **Hot-reload** — the server watches file modification times and reloads the vault on any change; no restart needed
- **Syntax highlighting** — fenced code blocks get language labels, a copy button, and Tokyo Night Dark theme via highlight.js
- **Dark / light mode** — toggle button in the header; preference persisted in `localStorage`
- **Inline body tags** — `#hashtag` mentions in the note body are collected as tags; merged with frontmatter `tags:`
- **Mobile nav** — nav links wrap below the site title on narrow viewports (≤ 600 px)
- **Print stylesheet** — `@media print` hides nav and interactive chrome, resets colours, appends link URLs inline
- **Custom 404** — styled 404 page consistent with the rest of the site
- **Docker-ready** — pass `VAULT_REPO` as a build arg to clone your private vault at deploy time

### Multilingual

- **Language routing** — add a two-letter suffix to any filename (`Post_RU.md` → `/post/ru`), or set `lang:` in frontmatter; language toggle in header; `hreflang` meta tags; auto-redirect for missing translations; "not yet translated" placeholder for content that exists only in a non-default language
- **UI string translations** — create a `type: translations` vault note with `lang:` and a `strings:` dict to translate fixed UI labels (Tags, Search, nav items) into any language without editing templates

---

## Frontmatter reference

```yaml
---
website: true         # required to publish the note as a web page
type: homepage        # optional: homepage | listing | book
                      #   homepage — serves this note's content at the section root URL
                      #   listing  — auto-generates a post index at the section root URL
                      #   book     — uses the book template with cover/metadata header
featured: true        # optional: highlight this post in the section's featured area
show_search: true     # root homepage only: show a Search link in the top nav
show_tags: true       # root homepage only: show a Tags link in the top nav
date: 2026-01-15
title: My Post        # optional; overrides H1 and filename
slug: my-post         # optional; auto-generated from title if omitted
priority: 0           # featured posts only; lower = higher (date breaks ties)
summary: "..."        # shown on listing pages; auto-derived from content if omitted
menu_order: 1         # pin to top nav; lower number = further left; appended after section links
banner: "https://example.com/image.jpg"
banner_x: 0.5         # horizontal focal point (0–1)
banner_y: 0.4         # vertical focal point (0–1)
aliases:
  - alternate name    # extra wiki-link targets that resolve to this post
author: "Jane Doe"    # optional; shown in post meta and JSON-LD (string or list)
updated: 2026-04-01   # optional; shown as "Updated …" when different from date
icon: _attachments/logo.png  # optional; image shown beside the site title in the header;
                              #   cascades to all child pages unless overridden at a lower level
site_title: "My Brand"       # optional; replaces the website name displayed in the header;
                              #   cascades to child pages the same way as icon
tags:                 # user content tags — shown as badges, used for /tag/<name> archive pages,
  - python            #   search filtering, related posts, and Dataview FROM queries
  - philosophy        #   body #hashtags are also collected as tags automatically
---
```

---

## Running locally

**Requirements:** Python 3.11+

```bash
git clone https://github.com/airenare/onyxfolio
cd onyxfolio

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
docker build -t onyxfolio .
docker run -p 8000:8000 -v /path/to/vault:/vault onyxfolio
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
  templates/     base, index, post, listing, book, private, search, tag, 404
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

[PolyForm Noncommercial 1.0.0](LICENSE) — free for personal and non-commercial use; commercial use requires permission from the author.
