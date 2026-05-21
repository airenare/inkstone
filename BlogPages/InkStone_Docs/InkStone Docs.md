---
website: true
type: homepage
title: InkStone Docs
language: en
show_search: true
default_theme: dark
icon: /static/InkStoneLogo.png
---

![[InkStoneLogo.png]]

# Turn your Obsidian vault into a website.

InkStone is a Python/Flask server that reads your Obsidian vault and serves it as a live website. Add `website: true` to any note — it's published. Your folder structure becomes your URL structure. No build step, no export.

---

## Documentation

- [[Getting Started]]
  - [[Quick Start]] — up and running in under 5 minutes
  - [[Installation]] — requirements, deps, first-run checklist
  - [[Configuration Reference]] — every environment variable

- [[Writing]]
  - [[Publishing Notes]] — minimal frontmatter, URL rules, slug overrides
  - [[Frontmatter Reference]] — every field in one table
  - [[Markdown Features]] — callouts, checkboxes, highlights, math, Mermaid
  - [[Links and Embeds]] — wiki-links, aliases, anchors, transclusion
  - [[Images and Media]] — lightbox, sliders, banners, video, audio
  - [[Dataview Queries]] — TABLE, LIST, FROM, WHERE, GROUP BY
  - [[Canvas Boards]] — publish `.canvas` files as interactive boards
  - [[Obsidian Bases]] — publish `.base` table views
  - [[Note Templates]] — QuickAdd templates for each page type

- [[Site Structure]]
  - [[URL Mapping]] — how vault paths become URLs
  - [[Page Types]] — homepage, listing, book, translations
  - [[Navigation]] — nav links, pinning, breadcrumbs

- [[Features]]
  - [[Theming]] — dark/light/system toggle, default theme
  - [[Branding]] — favicon, site icon, header title override
  - [[Search and Tags]] — full-text search, tag pages, inline hashtags
  - [[Multilingual]] — language variants, UI translations
  - [[Private Notes]] — per-note tokens, master key
  - [[Comments]] — Giscus comments via GitHub Discussions
  - [[Social Links]] — footer social profile links
  - [[SEO and Feeds]] — RSS, sitemap, OpenGraph, JSON-LD

- [[Deployment]]
  - [[Local Development]] — hot-reload dev workflow
  - [[Docker]] — container deployment, docker-compose
  - [[Production Deployment]] — Coolify, webhooks, SSL, subpath hosting
