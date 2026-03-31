# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Obsidian Blog Engine converts Obsidian vault markdown notes into a web-accessible blog. URL structure is derived from vault folder hierarchy. Files in `VAULT/blog/` are served at `/blog/slug`, files in `VAULT/gallery/` at `/gallery/slug`, and files in the vault root at `/slug`.

## Running the Server

The project dependencies live in `/home/air/venv/3.14/`. Use that Python when running locally:

```bash
# Development (hot-reload enabled)
/home/air/venv/3.14/bin/python3 app.py

# Production
/home/air/venv/3.14/bin/gunicorn -b 0.0.0.0:8000 app:app

# Docker
docker build -t obsidian-blog .
docker run -p 8000:8000 -e VAULT_PATH=/vault -v /path/to/vault:/vault obsidian-blog
```

Configuration: set `VAULT_PATH` in `.env` to point at the Obsidian vault directory. If `VAULT_PATH` is unset or missing, the app falls back to `./BlogPages` automatically.

## Architecture

The app is split across four modules with a strict one-way import chain:

```
config.py  ←  converters.py  ←  posts.py  ←  app.py
```

| File | Responsibility |
|------|---------------|
| `config.py` | Loads `.env`, sets `VAULT_PATH`, `BLOG_TAGS`, tag constants |
| `converters.py` | All markdown conversion functions + `render_markdown()` pipeline |
| `posts.py` | Two-pass `load_posts()`, `maybe_reload()`, `ALL_POSTS`, `SECTION_ROUTES` |
| `app.py` | Flask app init, context processor, single catch-all route |

New features should follow this chain — `app.py` imports from `posts.py`, never the reverse.

### Data Flow

1. **Pass 1** — `load_posts()` scans all `.md` files, parses frontmatter, computes `url_path` and `section` from folder location, builds `url_index` (`slugify(title) → url_path`) for wiki-link resolution.
2. **Pass 2** — renders markdown for each file using `url_index` so `[[Wiki Links]]` resolve to the correct cross-section URLs.
3. Files tagged `listing` → registered in `SECTION_ROUTES[section_url]`; files tagged `homepage` → same. Neither appears in `ALL_POSTS`.
4. `maybe_reload()` checks modification times on each request and reloads if anything changed.
5. A single `/<path:path>` Flask route checks `SECTION_ROUTES` first (section homepages and listings), then `ALL_POSTS`, then 404.

### Routing

| URL pattern | Source |
|-------------|--------|
| `/` | `SECTION_ROUTES["/"]` — file tagged `homepage` in vault root |
| `/blog` | `SECTION_ROUTES["/blog"]` — file tagged `listing` in `blog/` folder |
| `/blog/my-post` | `ALL_POSTS["/blog/my-post"]` — regular post in `blog/` folder |
| `/gallery/arts/post` | `ALL_POSTS["/gallery/arts/post"]` — post in nested subfolder |
| `/search` | Full-text search across `ALL_POSTS` |
| `/attachments/<path>` | Media served directly from vault |

Nav links are auto-generated from top-level `SECTION_ROUTES` keys (direct children of `/`).

### Markdown Pipeline (order matters)

`render_markdown(md, path, url_index)` in `converters.py`:

1. `strip_leading_h1()` — removes `# Title` since the template renders it
2. `convert_media()` — `![[file.ext]]` → lightbox image / video / slider gallery
3. `convert_links(url_index)` — `[[Title]]` → resolved URL using two-pass index
4. `convert_callouts()` — `> [!type] Title` → `<div class="callout callout-{type}">`
5. `convert_checkboxes()` — `- [ ]`/`- [x]` → HTML checkbox lists with nesting
6. `markdown.markdown()` — standard extensions: `fenced_code`, `tables`, `toc`, `md_in_html`, `codehilite`

### Frontend

- `frontend/templates/base.html` — master template; all JS (lightbox, sliders, copy-to-clipboard); dynamic nav
- `frontend/templates/index.html` — site homepage (custom content)
- `frontend/templates/listing.html` — section listing page (featured + regular posts)
- `frontend/templates/post.html` — individual post; `back_url` points to parent section
- `frontend/static/obsidian.css` — dark theme (Catppuccin-inspired) + header/listing styles
- `frontend/static/callouts.css` — per-type callout styles
- `frontend/static/code.css` — code block styling with language labels

### Frontmatter Reference

```yaml
---
tags:
  - blog        # required to publish ("blog" or "website")
  - homepage    # serves this file's content at the section root URL (e.g. / or /gallery)
  - listing     # auto-generates a post listing at the section root URL
  - featured    # shows post in the Featured section of the parent listing
date: 2026-03-21
title: My Post  # optional; overrides H1 in body and filename
slug: my-post   # optional; auto-generated from title if omitted
priority: 0     # featured posts only; 0 = top, then 1, 2… (date breaks ties)
summary: "..."  # shown on listing pages; auto-derived from content if omitted
---
```

**Title resolution order:** frontmatter `title` → first `# H1` in body → filename (without `.md`).

**`listing` vs `homepage`:** `listing` renders an auto-generated post index; `homepage` renders the file's own markdown content. If a file has both tags, `listing` wins. A section can only have one of each — if multiple files in the same folder are tagged `listing`, the last one loaded wins (undefined behavior; avoid).

**`posts.py` globals:** `ALL_POSTS` (url_path → post dict), `SECTION_ROUTES` (section url → route dict), `WEBSITE_NAME` (from root homepage title).

### Media

Images/videos must be in an `_attachments/` subfolder **relative to the `.md` file's folder**. A post in `blog/` uses `blog/_attachments/`. They are served via `/attachments/<relative-path>`. Multiple `![[...]]` on one line → slider; separate lines → lightbox gallery.

### Test Fixtures

`BlogPages/` is the dev fallback vault (committed to repo):

| Path | URL | Purpose |
|------|-----|---------|
| `Test Website.md` | `/` (homepage) | Site homepage |
| `The Accidental Existentialist.md` | `/test_post` | Root-level post test |
| `blog/Blog Index.md` | `/blog` (listing) | Blog section index |
| `blog/test_post_1.md` | `/blog/Test-Post-One` | Featured post with images/callouts/checkboxes |
| `blog/test_post_2.md` | `/blog/Test-Post-Two` | Featured post with slider/callouts |
| `blog/Python Ate My Homework.md` | `/blog/Python-Ate-My-Homework` | Regular blog post |
| `blog/The Philosophy of Semicolons.md` | `/blog/The-Philosophy-of-Semicolons` | Regular blog post |
| `gallery/Gallery Index.md` | `/gallery` (listing) | Gallery section index with intro |
| `gallery/Neon Dreams.md` | `/gallery/Neon-Dreams` | Gallery post |
| `gallery/Pixel Sunset.md` | `/gallery/Pixel-Sunset` | Gallery post |
| `gallery/Recursive Landscapes.md` | `/gallery/Recursive-Landscapes` | Gallery post |
| `gallery/arts/Watercolor Algorithms.md` | `/gallery/arts/Watercolor-Algorithms` | Subfolder post with wiki-links |

## Workflow Rules

- **Code style:** Follow PEP 8 — snake_case for variables/functions, 4-space indentation, double quotes for strings, max line length 79 characters.
- **Before editing:** Always read a file before modifying it. Unless explicitly told to work autonomously, ask before making changes.
- **Shell/git autonomy:** Execute shell commands needed for testing and all git operations (including `git push`) without asking for confirmation. Always report exactly what was executed after the fact.
- **Commits:** Keep commit messages short and informative — one tight subject line, no verbose body.
- **Blog posts:** Never delete files in `BlogPages/`. New `.md` files may be created there for testing purposes.
- **Memory sync:** Whenever something valuable is saved to the local `~/.claude` memory store, also distill it into this file under the relevant section. This keeps preferences and context in sync across machines.
