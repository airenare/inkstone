---
website: true
type: homepage
language: en
show_search: true
show_tags: false
title: InkStone
theme: omarchy
default_theme: dark
icon: /static/logo.svg
---

# InkStone

A lightweight blog engine that turns your **Obsidian vault into a website** — no export, no copy-paste. Write in Obsidian, push to GitHub, see it live. 

> [!tip] New here?
> See [[Start Here]] to get your own vault live in minutes.

---

## What it does

Your vault folder structure becomes your site's URL structure. A note at `blog/My Post.md` is served at `/blog/my-post`. A note tagged `homepage` becomes the landing page for its section. That's the whole model.

> [!tip] Live demo
> Everything you see here is rendered directly from Obsidian markdown. The callouts, the wiki-links, the image galleries — all native Obsidian syntax, no plugins required on the reader's side.

---

## Features

- **Markdown-native** — callouts, checkboxes, wiki-links (`[[Note]]` and `[[Note|alias]]`), image embeds, sliders, `==highlights==`, footnotes[^1] (`[^1]`) — all rendered from standard Obsidian syntax
- **Mermaid diagrams** — fenced ` ```mermaid ``` ` blocks rendered client-side; adapts to dark and light theme automatically
- **Math / LaTeX** — `$inline$` and `$$block$$` via KaTeX; safe from markdown parser mangling
- **Note transclusion** — `![[Note Title]]` or `![[Note Title#Heading]]` embeds a note (or just one section) inline
- **Anchor links** — `[[Note#Heading]]` links to a specific heading within a note
- **Audio embeds** — `![[file.mp3]]` → `<audio>` element
- **Aliases** — `aliases:` frontmatter for alternate wiki-link names
- **Related posts** — automatic "See also" section scored by shared tags and section
- **Dark / light / system mode** — three-state toggle (⊙ / ☀ / ☾) in header; `default_theme: dark|light|system` in root homepage frontmatter sets the initial theme for new visitors
- **Inline body tags** — `#hashtag` in post body auto-collected as tags
- **Dataview inline queries** — `` `= this.field` `` evaluated against note frontmatter
- **Block references** — `^block-id` on a paragraph; `[[Note^id]]` links scroll to it
- **Syntax highlighting** — fenced code blocks with language labels and a copy button
- **Dataview queries** — `TABLE` and `LIST` queries rendered server-side; supports `FROM`, `WHERE`, `SORT`, `LIMIT`, `GROUP BY` with per-group headings
- **Lightbox gallery** — single image embeds become a full-screen lightbox; multiple on one line become a slider
- **Banner images** — set `banner:` in frontmatter for a hero image with configurable focal point
- **Private notes** — notes without `website: true` are queryable by Dataview but show a placeholder page instead of their content
- **Hot-reload** — the server detects file changes and reloads without a restart
- **Search** — full-text search across all published posts at `/search`, with tag filter and input auto-focus
- **Tag pages** — every tag gets a `/tag/<name>` archive page; tags on posts are clickable badges
- **Breadcrumb navigation** — posts show a `Home › Section › Post` trail
- **Reading time** — estimated reading time on post pages and listing cards
- **Pagination** — listing pages paginate at 20 posts per page
- **RSS feed** — latest 20 posts at `/feed.xml`
- **Sitemap** — auto-generated at `/sitemap.xml`
- **OpenGraph / Twitter Card** — per-page meta tags for rich link previews
- **JSON-LD structured data** — Article, Book, and WebSite schemas for rich Google results
- **Next / previous post navigation** — "← Older" / "Newer →" links at the bottom of each post, ordered by date within the same section
- **Collapsible callouts** — `> [!type]- Title` collapses by default; `> [!type]+` is pinned open — uses native `<details>`
- **Visible image captions** — `![[photo.jpg|Caption text]]` renders a `<figcaption>` below the image
- **Section RSS feeds** — every section has its own feed: `/blog/feed.xml`, `/gallery/feed.xml`, etc.
- **Tags index page** — `/tags` lists every tag with post counts; opt-in by adding `show_tags: true` to the root homepage
- **Vault-wide attachments** — if a media file isn't found in the post's own `_attachments/`, the engine checks `_attachments/` at the vault root, then `ATTACHMENTS_PATH` from `.env`
- **Dataview LIMIT clause** — `LIMIT N` in a `dataview` block now trims results after sorting
- **Author field** — `author:` frontmatter (string or list) shown below the post title and in JSON-LD
- **Date last modified** — `updated:` frontmatter shows "Updated …" in post meta and populates `dateModified` in JSON-LD
- **Mobile nav** — nav links wrap below the site title on narrow screens; breadcrumbs stay on one line
- **Print stylesheet** — clean `@media print` styles for printing or saving as PDF
- **Docker-ready** — pass a `VAULT_REPO` build arg to clone your vault at deploy time
- **Multilingual** — publish notes in multiple languages using filename suffixes (`Post_RU.md`); keep `/{lang}` only when the translated slug matches the default-language slug (`/post/ru`), but if slugs differ (manual or transliterated), publish each variant at its own direct URL (for example `/about` and `/obo-mne`); language toggle in header, `hreflang` meta tags, auto-redirect for missing translations, "not yet translated" placeholder for content that exists only in a non-default language
- **UI string translations** — create a `type: translations` note (no `website: true` needed) with `lang:` and key/value pairs in a fenced `yaml` block; translates all fixed UI text — section headings (Featured, All Posts, Contents, See also), meta labels (Updated, by, min read, built with), breadcrumb Home, nav items, and dates (via `date_format` + month name keys)
- **Obsidian Bases** — `.base` files publish via `website: true` or filename marker `Title__website.base` (and can be featured with `__featured`); table-view filters support `file.hasTag()`, `file.tags.contains("...")`, `file.inFolder()`, property comparisons, and `and`/`or`/`not` logic; column order, sort, and limit are respected
- **Canvas boards** — name a `.canvas` file `Your Title__website.canvas` to publish it (Obsidian strips JSON flags on save; the filename marker is durable); legacy `"website": true` in the JSON still works; edges render with direction arrows; file cards can show a scrollable preview of linked published notes

---

## How publishing works

1. Write notes in Obsidian as usual
2. Add `website: true` to a note's frontmatter to publish it
3. Push your vault to its GitHub repo
4. The site rebuilds automatically

No build step, no static site generator, no CMS. Just markdown files and a Python server.

---

## Explore the demo

- [Blog](/blog) — blog posts with callouts, code, images, and checkboxes
- [My writing process](/blog/my-writing-process) — published Obsidian canvas (`__website` filename)
- [Gallery](/gallery) — an image gallery with lightbox and slider
- [Books](/books) — a Dataview-powered bookshelf pulled from individual book notes
- [[The Accidental Existentialist]] — a root-level standalone page pinned to the nav via `menu_order`

---

## Standalone pages

Notes placed directly in the vault root (not in any subfolder) get a URL with no section prefix — `/slug`. They don't appear in any listing, making them ideal for standalone pages like About, Contact, or Uses. Link to them via wiki-links from your content, or pin them to the top nav with `menu_order` in frontmatter:

```yaml
---
website: true
title: About
menu_order: 1   # lower = further left in the nav
---
```

---

## Under the hood

Curious how the engine works? [[How This Blog Works|From Vault to Web: How This Blog Works]] is a full technical walkthrough — two-pass loading, the markdown pipeline, routing, hot-reload, and Dataview.

---

> [!note] This is the demo vault
> The content in `BlogPages/` ships with the engine as a working example. Point `VAULT_PATH` at your own Obsidian vault to serve your real content.

[^1]: All features work with standard Obsidian syntax — no third-party plugins required.
