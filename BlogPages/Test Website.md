---
tags:
  - blog
  - homepage
  - search
title: Obsidian Blog Engine
---

# Obsidian Blog Engine

A lightweight blog engine that turns your **Obsidian vault into a website** — no export, no copy-paste. Write in Obsidian, push to GitHub, see it live.

---

## What it does

Your vault folder structure becomes your site's URL structure. A note at `blog/My Post.md` is served at `/blog/My-Post`. A note tagged `homepage` becomes the landing page for its section. That's the whole model.

> [!tip] Live demo
> Everything you see here is rendered directly from Obsidian markdown. The callouts, the wiki-links, the image galleries — all native Obsidian syntax, no plugins required on the reader's side.

---

## Features

- **Markdown-native** — callouts, checkboxes, wiki-links (`[[Note]]` and `[[Note|alias]]`), image embeds, sliders — all rendered from standard Obsidian syntax
- **Syntax highlighting** — fenced code blocks with language labels and a copy button
- **Dataview queries** — `TABLE` queries rendered as live HTML tables, pulling from any notes in your vault
- **Lightbox gallery** — single image embeds become a full-screen lightbox; multiple on one line become a slider
- **Banner images** — set `banner:` in frontmatter for a hero image with configurable focal point
- **Private notes** — notes without a `website` tag are queryable by Dataview but show a placeholder page instead of their content
- **Hot-reload** — the server detects file changes and reloads without a restart
- **Search** — full-text search across all published posts at `/search`, with tag filter
- **Tag pages** — every tag gets a `/tag/<name>` archive page; tags on posts are clickable badges
- **Breadcrumb navigation** — posts show a `Home › Section › Post` trail
- **Reading time** — estimated reading time on post pages and listing cards
- **Pagination** — listing pages paginate at 20 posts per page
- **RSS feed** — latest 20 posts at `/feed.xml`
- **Sitemap** — auto-generated at `/sitemap.xml`
- **OpenGraph / Twitter Card** — per-page meta tags for rich link previews
- **JSON-LD structured data** — Article, Book, and WebSite schemas for rich Google results
- **Docker-ready** — pass a `VAULT_REPO` build arg to clone your vault at deploy time

---

## How publishing works

1. Write notes in Obsidian as usual
2. Tag a note with `website` (or `blog`) to publish it
3. Push your vault to its GitHub repo
4. The site rebuilds automatically

No build step, no static site generator, no CMS. Just markdown files and a Python server.

---

## Explore the demo

- [Blog](/blog) — blog posts with callouts, code, images, and checkboxes
- [Gallery](/gallery) — an image gallery with lightbox and slider
- [Books](/books) — a Dataview-powered bookshelf pulled from individual book notes
- [[The Accidental Existentialist]] — a root-level standalone page pinned to the nav via `menu_order`

---

## Standalone pages

Notes placed directly in the vault root (not in any subfolder) get a URL with no section prefix — `/slug`. They don't appear in any listing, making them ideal for standalone pages like About, Contact, or Uses. Link to them via wiki-links from your content, or pin them to the top nav with `menu_order` in frontmatter:

```yaml
---
tags:
  - website
title: About
menu_order: 1   # lower = further left in the nav
---
```

---

> [!note] This is the demo vault
> The content in `BlogPages/` ships with the engine as a working example. Point `VAULT_PATH` at your own Obsidian vault to serve your real content.
