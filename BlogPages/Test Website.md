---
tags:
  - blog
  - homepage
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

- **Markdown-native** — callouts, checkboxes, wiki-links, image embeds, sliders, all rendered from standard Obsidian syntax
- **Syntax highlighting** — fenced code blocks with language labels and a copy button
- **Dataview queries** — `TABLE` queries rendered as live HTML tables, pulling from any notes in your vault
- **Lightbox gallery** — single or multi-image embeds become a full-screen gallery
- **Banner images** — set `banner:` in frontmatter for a hero image at the top of any page
- **Private notes** — notes in your vault without a `website` tag are queryable by Dataview but show a placeholder instead of their content
- **Hot-reload** — the server detects file changes and reloads without a restart
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

---

> [!note] This is the demo vault
> The content in `BlogPages/` ships with the engine as a working example. Point `VAULT_PATH` at your own Obsidian vault to serve your real content.
