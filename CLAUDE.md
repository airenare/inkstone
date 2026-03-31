# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Obsidian Blog Engine converts Obsidian vault markdown notes into a web-accessible blog. It filters posts by tag (`blog` or `website`), converts Obsidian-specific syntax to HTML, and serves them via Flask.

## Running the Server

```bash
# Development (hot-reload enabled)
python app.py

# Production
gunicorn -b 0.0.0.0:8000 app:app

# Docker
docker build -t obsidian-blog .
docker run -p 8000:8000 -e VAULT_PATH=/vault -v /path/to/vault:/vault obsidian-blog
```

Configuration: set `VAULT_PATH` in `.env` to point at the Obsidian vault directory.

## Architecture

The app is split across four modules:

| File | Responsibility |
|------|---------------|
| `config.py` | Loads `.env`, sets `VAULT_PATH` and `BLOG_TAGS` |
| `converters.py` | All markdown conversion functions + `render_markdown()` pipeline |
| `posts.py` | `load_posts()`, `maybe_reload()`, `parse_frontmatter()`, `POSTS` dict |
| `app.py` | Flask app init and routes only |

Data flow:

1. `posts.load_posts()` scans `VAULT_PATH` for `.md` files, parses YAML frontmatter, filters by `BLOG_TAGS = {"blog", "website"}`, runs the markdown pipeline, and stores results in `posts.POSTS` keyed by slug.
2. `posts.maybe_reload()` checks file modification times on each request and reloads if anything changed.
3. Flask routes (`/`, `/post/<slug>`, `/search`, `/attachments/<path>`) render Jinja2 templates from `frontend/templates/` using `post_store.POSTS`.

### Markdown Pipeline (order matters)

`render_markdown()` in `converters.py` applies converters in sequence before handing off to the Python `markdown` library:

1. `convert_media()` — `![[file.ext]]` → `<img>`/`<video>` with lightbox or slider gallery
2. `convert_links()` — `[[Title]]` → `<a href="/post/slug">`
3. `convert_callouts()` — `> [!type] Title` blocks → `<div class="callout callout-{type}">`
4. `convert_checkboxes()` — `- [ ]`/`- [x]` task lists → HTML `<ul>` with disabled checkboxes
5. `markdown.markdown()` — standard extensions: `fenced_code`, `tables`, `toc`, `md_in_html`, `codehilite`

### Frontend

- `frontend/templates/base.html` — master template; contains all JS for lightbox, image sliders, and copy-to-clipboard
- `frontend/static/obsidian.css` — dark theme (Catppuccin-inspired)
- `frontend/static/callouts.css` — per-type callout styles (note, warning, danger, info, etc.)
- `frontend/static/code.css` — code block styling with language labels

### Frontmatter Format

```yaml
---
tags:
  - blog       # "blog" or "website" required to publish
date: 2026-03-21
title: My Post
slug: my-post  # auto-generated from title if omitted
---
```

### Media

Images/videos must be in an `_attachments/` subfolder relative to the `.md` file. They are served via `/attachments/<relative-path>`. Multiple `![[...]]` embeds on the same line become a slider gallery; separate lines produce individual lightbox images.

## Workflow Rules

- **Code style:** Follow PEP 8 — snake_case for variables/functions, 4-space indentation, double quotes for strings, max line length 79 characters.
- **Before editing:** Always read a file before modifying it. Unless explicitly told to work autonomously, ask before making changes.
- **Commits:** Always ask the user before committing. Never commit automatically.
- **Blog posts:** Never delete files in `BlogPages/`. New `.md` files may be created there for testing purposes.
