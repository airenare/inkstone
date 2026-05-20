# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

InkStone converts Obsidian vault markdown notes into a web-accessible blog. URL structure is derived from vault folder hierarchy. Files in `VAULT/blog/` are served at `/blog/slug`, files in `VAULT/gallery/` at `/gallery/slug`, and files in the vault root at `/slug`.

## Running the Server

The project dependencies live in `/home/air/venv/3.14/`. Use that Python when running locally:

```bash
# Development (hot-reload enabled)
/home/air/venv/3.14/bin/python3 app.py

# Production
/home/air/venv/3.14/bin/gunicorn -b 0.0.0.0:8000 app:app

# Docker
docker build -t inkstone .
docker run -p 8000:8000 -e VAULT_PATH=/vault -v /path/to/vault:/vault inkstone
```

Configuration: set `VAULT_PATH` in `.env` to point at the Obsidian vault directory. If `VAULT_PATH` is unset or missing, the app falls back to `./BlogPages` automatically.

**Optional env vars:**
- `ACCESS_TOKEN` — master key that unlocks ALL private notes. Per-note access is controlled by `access_token:` frontmatter instead (each note has its own token, session tracks unlocked URLs individually). Both can coexist.
- `SECRET_KEY` — Flask session signing key. Set to a long random string in production. Defaults to `"inkstone-dev-secret"` (sessions invalidated on restart if not set).
- `HIDE_ATTRIBUTION` — set to `"1"` or `"true"` to remove the "built with InkStone" footer line.
- `GISCUS_REPO`, `GISCUS_REPO_ID`, `GISCUS_CATEGORY_ID` — all three required to enable Giscus comments.
- `VAULT_REPO` — Git URL to clone a private vault at Docker build time.
- `WEBHOOK_SECRET` — secret for validating GitHub webhook payloads on `/webhook`.
- `URL_PATH_PREFIX` or `APPLICATION_ROOT` — when the site is served under a subpath (e.g. `https://example.com/inkstone/`), set to that prefix without trailing slash (e.g. `/inkstone`). All generated `/attachments/…` URLs in note HTML, canvas cards, and header icons include this prefix.

## Architecture

The app is split across eight modules with a strict one-way import chain:

```
config.py  ←  obsidian_syntax.py  ←  converters.py  ←  posts.py  ←  app.py
                   dataview.py    ↗          bases.py  ↗    view_helpers.py ↗
```

| File | Responsibility |
|------|---------------|
| `config.py` | Loads `.env`, sets `VAULT_PATH`, `ATTACHMENTS_PATH`, `ACCESS_TOKEN`, `SECRET_KEY` |
| `obsidian_syntax.py` | Obsidian-specific converters: wiki-links, embeds, callouts, checkboxes, highlights, math, block IDs, transclusion, `slugify` |
| `dataview.py` | Server-side Dataview query engine: TABLE/LIST/GROUP BY/WHERE/SORT/LIMIT |
| `bases.py` | Obsidian Bases renderer: parses `.base` YAML, evaluates filters, renders `type:table` views as HTML |
| `converters.py` | Pipeline coordinator: imports from `obsidian_syntax` + `dataview`, wires `render_markdown()` |
| `posts.py` | `load_posts()` (markdown + `.base` + `.canvas`), Pass 4 canvas HTML, `maybe_reload()`, `ALL_POSTS`, `SECTION_ROUTES` |
| `view_helpers.py` | Pure view utilities (no Flask): `_build_breadcrumbs`, `_get_adjacent_posts`, `_get_related`, `_highlight` |
| `app.py` | Flask app init, context processor, routes |

New features should follow this chain — `app.py` imports from `posts.py` and `view_helpers.py`, never the reverse.

### Data Flow

1. **Pass 1** — `load_posts()` scans all `.md` files, parses frontmatter, computes `url_path` and `section` from folder location, builds `url_index` for wiki-link resolution. Also scans `.base` files: publish if the filename ends with `__website` before `.base` (optionally `__featured`; title = name with suffixes stripped) or if legacy YAML has `website: true`; adds them to `url_index` + `candidates_base`. Scans `.canvas` files: publish if the filename ends with `__website` before `.canvas` (title = name with that suffix stripped; survives Obsidian re-saves) or if legacy JSON has `"website": true`. Each `.md` post is indexed three ways: `slugify(title)`, `slugify(filename without .md)`, and frontmatter `slug`.
2. **Pass 2** — renders markdown for each `.md` file using `url_index` so `[[Wiki Links]]` resolve to the correct cross-section URLs.
3. **Pass 3** — renders each `.base` candidate by executing its filters against the completed `dataview_index` and generating an HTML table; adds result to `ALL_POSTS` with `post_type: "base"`.
4. **Pass 4** — renders each published `.canvas` via `render_canvas()` into `ALL_POSTS` (`post_type: "canvas"`): SVG edges use arrow markers toward the target node; file nodes embed scrollable HTML previews when the vault file path resolves to an existing published post (body HTML and titles passed from `all_posts` built in earlier passes).
5. Files with `type: listing` → registered in `SECTION_ROUTES[section_url]`; files with `type: homepage` → same. Neither appears in `ALL_POSTS`.
6. `maybe_reload()` checks modification times on each request and reloads if anything changed.
7. A single `/<path:path>` Flask route checks `SECTION_ROUTES` first (section homepages and listings), then `ALL_POSTS`, then 404.

### Routing

| URL pattern | Source |
|-------------|--------|
| `/` | `SECTION_ROUTES["/"]` — file with `type: homepage` in vault root |
| `/blog` | `SECTION_ROUTES["/blog"]` — file with `type: listing` in `blog/` folder |
| `/blog/my-post` | `ALL_POSTS["/blog/my-post"]` — regular post in `blog/` folder |
| `/gallery/arts/post` | `ALL_POSTS["/gallery/arts/post"]` — post in nested subfolder |
| `/search` | Full-text search across `ALL_POSTS` |
| `/feed.xml` | RSS feed — latest 20 posts sorted by date |
| `/sitemap.xml` | Auto-generated sitemap of all routes |
| `/attachments/<path>` | Media served directly from vault |

Nav links are auto-generated from top-level `SECTION_ROUTES` keys (direct children of `/`). Posts with `menu_order` in frontmatter are additionally pinned to the nav (sorted by value, appended after section links). This is the intended mechanism for standalone pages like About or Contact.

**Root-level standalone pages:** Files in the vault root that do not have `type: homepage` or `type: listing` are served at `/slug` with no section prefix. They are intentionally unlisted — they don't appear in any auto-generated listing. The expected usage is to link to them via wiki-links from other content, or pin them to the nav via `menu_order`. Do not add special logic to surface them automatically in listings.

### Markdown Pipeline (order matters)

`render_markdown(md, path, url_index)` in `converters.py` (functions live in `obsidian_syntax.py` and `dataview.py`):

1. `strip_leading_h1()` — removes `# Title` since the template renders it
2. `convert_media()` — `![[file.ext]]` → lightbox image / video / slider gallery
3. `convert_links(url_index)` — `[[Title]]` → resolved URL using two-pass index
4. `convert_callouts()` — `> [!type] Title` → `<div class="callout callout-{type}">`
5. `convert_checkboxes()` — `- [ ]`/`- [x]` → HTML checkbox lists with nesting
6. `convert_dataview()` — ` ```dataview ``` ` blocks executed server-side by `dataview.py`
7. `markdown.markdown()` — standard extensions: `fenced_code`, `tables`, `toc`, `md_in_html`, `codehilite`

### Frontend

- `frontend/templates/base.html` — master template; all JS (lightbox, sliders, copy-to-clipboard); dynamic nav; `{% block meta %}` for per-page OG/Twitter tags
- `frontend/templates/index.html` — site homepage (custom content)
- `frontend/templates/listing.html` — section listing page (featured + regular posts)
- `frontend/templates/post.html` — individual post; `back_url` points to parent section
- `frontend/templates/404.html` — custom 404 page
- `frontend/static/obsidian.css` — dark theme (Catppuccin-inspired) + header/listing styles
- `frontend/static/omarchy.css` — alternative Omarchy-native theme
- `frontend/static/callouts.css` — per-type callout styles
- `frontend/static/omarchy-callouts.css` — callout styles for the Omarchy theme
- `frontend/static/code.css` — code block styling with language labels

### Frontmatter Reference

```yaml
---
website: true         # required to publish the note as a web page
type: homepage        # optional: homepage | listing | book | translations
                      #   homepage — serves this note's content at the section root URL
                      #   listing  — auto-generates a post index at the section root URL
                      #   book     — uses the book template with cover/metadata header
                      #   translations — UI label overrides for a language (no website: needed)
featured: true        # optional: shows post in the Featured section of the parent listing
show_search: true     # root homepage only: shows a Search link in the top nav
show_tags: true       # root homepage only: shows a Tags link in the top nav
date: 2026-03-21
updated: 2026-04-01   # optional; shown as "Updated …" in post meta and JSON-LD dateModified
title: My Post        # optional; overrides H1 in body and filename
slug: my-post         # optional; auto-generated from title if omitted; non-ASCII titles are
                      #   transliterated via unidecode (Cyrillic, Greek, etc. → ASCII Latin);
                      #   manual slug: is used as-is, bypassing transliteration
priority: 0           # featured posts only; 0 = top, then 1, 2… (date breaks ties)
summary: "..."        # shown on listing pages; auto-derived from content if omitted
menu_order: 1         # pin this post to the top nav; lower = further left; appended after section links
author: "Jane Doe"    # optional; shown in post meta and JSON-LD (string or list)
tags:                 # user content tags — shown as clickable badges, used for /tag/<name>
  - python            #   archive pages, search filtering, related posts, and Dataview FROM queries
  - philosophy        #   body #hashtags are collected as tags automatically
access_token: secret  # optional; private notes (no website: true) only; share the URL as
                      #   /slug?token=secret to unlock this specific note for the visitor;
                      #   ACCESS_TOKEN env var acts as a master key that unlocks all notes
language: en          # root homepage only: sets the site default language
default_theme: dark   # root homepage only: initial theme for new visitors — "dark", "light", or
                      #   "system" (follow OS); defaults to "system" if omitted
lang: ru              # per-note or filename suffix (_RU.md): marks note as a language variant
                      #   → served at /{slug}/{lang}; language toggle, hreflang, auto-redirect
---
```

**`type: translations` notes** — frontmatter only needs `type: translations` + `lang:`. String mappings go in a fenced ` ```yaml ` block in the note body (not in frontmatter). No `website: true` needed. Example body:

```yaml
Search: Поиск
Tags: Теги
"All tags": Все теги
"min read": мин чтения
```

**Title resolution order:** frontmatter `title` → first `# H1` in body → filename (without `.md`).

**YAML quoting:** Any string value that contains a colon (`:`) must be wrapped in double quotes, otherwise YAML parses it as a nested mapping and the field silently breaks. This applies to `title`, `summary`, `slug`, and any other string field.
```yaml
title: "From Vault to Web: How This Blog Works"   # correct — quotes are YAML syntax, stripped from value
title: From Vault to Web: How This Blog Works      # broken — YAML parses as a dict
```
The engine will log a `WARNING` to stderr and fall back to the H1/filename when it detects a dict-valued `title`.

**Intentional quotes in a title:** YAML double-quote wrappers are always stripped by the parser — they never appear in the final value. To include literal `"` characters in a title (e.g. `"Hello World" Considered Harmful`), wrap the whole value in single quotes:
```yaml
title: '"Hello World" Considered Harmful'   # value → "Hello World" Considered Harmful
title: "No quotes here: just a colon"       # value → No quotes here: just a colon
```

**`type: listing` vs `type: homepage`:** `listing` renders an auto-generated post index; `homepage` renders the file's own markdown content. A section can only have one of each — if multiple files in the same folder have the same type, the last one loaded wins (undefined behavior; avoid).

**`posts.py` globals:** `ALL_POSTS` (url_path → post dict), `SECTION_ROUTES` (section url → route dict), `WEBSITE_NAME` (from root homepage title).

### Media

Images/videos must be in an `_attachments/` subfolder **relative to the `.md` file's folder**. A post in `blog/` uses `blog/_attachments/`. They are served via `/attachments/<relative-path>`. Multiple `![[...]]` on one line → slider; separate lines → lightbox gallery.

### Test Fixtures

`BlogPages/` is the dev fallback vault (committed to repo):

| Path | URL | Purpose |
|------|-----|---------|
| `Test Website.md` | `/` (homepage) | Site homepage |
| `The Accidental Existentialist.md` | `/the-accidental-existentialist` | Root-level standalone page; pinned to nav via `menu_order: 1` |
| `blog/Blog Index.md` | `/blog` (listing) | Blog section index |
| `blog/test_post_1.md` | `/blog/test-post-one` | Featured post with images/callouts/checkboxes |
| `blog/test_post_2.md` | `/blog/test-post-two` | Featured post with slider/callouts |
| `blog/Python Ate My Homework.md` | `/blog/python-ate-my-homework` | Regular blog post |
| `blog/The Philosophy of Semicolons.md` | `/blog/the-philosophy-of-semicolons` | Regular blog post |
| `gallery/Gallery Index.md` | `/gallery` (listing) | Gallery section index with intro |
| `gallery/Neon Dreams.md` | `/gallery/neon-dreams` | Gallery post |
| `gallery/Pixel Sunset.md` | `/gallery/pixel-sunset` | Gallery post |
| `gallery/Recursive Landscapes.md` | `/gallery/recursive-landscapes` | Gallery post |
| `gallery/arts/Watercolor Algorithms.md` | `/gallery/arts/watercolor-algorithms` | Subfolder post with wiki-links |
| `blog/My Writing Process__website.canvas` | `/blog/my-writing-process` | Published canvas (`__website` filename marker; JSON graph only) |

### Documentation Vault

`InkStone_Docs/` is the official documentation site — a self-hosted InkStone vault committed to the repo. Serve it with `VAULT_PATH=InkStone_Docs/ /home/air/venv/3.14/bin/python3 app.py`. It is a standalone vault (no live-site vault locally). 33 files across 6 sections:

| Section | Pages |
|---------|-------|
| `getting-started/` | Getting Started, Quick Start, Installation, Configuration |
| `writing/` | Publishing Notes, Frontmatter Reference, Markdown Features, Links and Embeds, Images and Media, Dataview Queries, Canvas Boards, Obsidian Bases, Note Templates |
| `site-structure/` | URL Mapping, Page Types, Navigation |
| `features/` | Theming, Branding, Search and Tags, Multilingual, Private Notes, Comments, Social Links, SEO and Feeds |
| `deployment/` | Local Development, Docker, Production Deployment |
| root | `InkStone Docs.md` (homepage) |

Keep in sync when features are added, changed, or removed. Update the relevant doc page(s) in the same commit.

## Workflow Rules

- **Context retrieval:** At the start of every session, search the `inkstone` Pinecone index (namespace `codebase`) with a query relevant to the task at hand — e.g. "routing and data flow" or "how does callout rendering work". Pull 3–5 records. This replaces re-reading source files for architectural questions and keeps context usage low.
- **Pinecone index maintenance:** After every feature addition, change, or removal — update the `inkstone` index (namespace `codebase`) as part of the same work session. Upsert modified records with the new information. If something is removed or replaced, upsert the affected record with a note marking the old behaviour as removed/changed and describing the new behaviour. Never leave the index stale.
- **Sync before starting:** At the beginning of every task, run `git fetch` and check both (a) whether the remote is ahead and (b) whether there are any unstaged or uncommitted local changes. Report the findings and, if there is anything to resolve, present numbered options (e.g. 1. stash, 2. commit, 3. discard) before proceeding. If the remote is ahead and local is clean, `git pull --rebase` automatically and summarise what changed.
- **Code style:** Follow PEP 8 — snake_case for variables/functions, 4-space indentation, double quotes for strings, max line length 79 characters.
- **Before editing:** Always read a file before modifying it.
- **Autonomy:** Work autonomously — execute shell commands needed for testing and all git operations (including `git push`) without asking for confirmation. Always report what was executed after the fact. Do not ask for permission before making code changes.
- **Commits:** Keep commit messages short and informative — one tight subject line, no verbose body.
- **VERSIONING — DO THIS EVERY TIME:** After every bug fix or feature, bump the `VERSION` file and create a git tag. This is mandatory, not optional.
  - Bug fix → PATCH bump (e.g. `1.11.0` → `1.11.1`)
  - New feature → MINOR bump (e.g. `1.11.0` → `1.12.0`)
  - Breaking change → MAJOR bump (e.g. `1.11.0` → `2.0.0`)
  - Steps: edit `VERSION`, commit as `chore: bump version to X.Y.Z`, then `git tag vX.Y.Z && git push origin vX.Y.Z`
- **Blog posts:** `BlogPages/` is the demo vault — it should showcase features well and stay clean. Files may be created, modified, reorganized, or deleted when needed to improve the demo (e.g. removing debug content, regrouping pages, adding better examples). Propose the change first and proceed only after the user agrees.
- **Memory sync:** Whenever something valuable is saved to the local `~/.claude` memory store, also distill it into this file under the relevant section. This keeps preferences and context in sync across machines.
- **TODO.md:** Project backlog lives in `TODO.md` at the repo root. Check it when the user asks to implement todos. When an item is done, move it to `DONE.md` (grouped by version) — do not leave ✅ items in TODO.md.
- **Docs sync:** After every feature addition, change, or removal — update both `README.md` and the vault homepage (`BlogPages/Test Website.md`) to reflect the current state. Do this as part of the same commit, not as a separate step.
