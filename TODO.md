# TODO / Backlog


## High Priority

- **Fix `requirements.txt` malformed gunicorn version** — `gunicorn==20.1.01.8.0` is two version strings merged (should be `gunicorn==21.2.0` or whichever is current). This breaks `pip install -r requirements.txt`.
- **Invalid HTML in `base.html`** — The first `<script>` block (hljs DOMContentLoaded) sits between `</head>` and `<body>` tags, which is invalid HTML. Move it into `<head>` or the top of `<body>`.
- **`hljs.initLineNumbersOnLoad()` called without the extension** — `highlight.js-line-numbers.js` is never loaded, so this call silently fails on every page. Remove it or load the extension.
- **Search searches raw HTML markup** — `p["content"]` in `posts.py` stores lowercased HTML. Searching for a word can match HTML attribute names or tag substrings. Strip tags before storing the content field (as a plain-text copy) to search against.
- **`slugify()` is case-sensitive** — `[[My Note]]` and `[[my note]]` produce different lookup keys. The `url_index` lookup in `convert_links` should normalise to lowercase before lookup so wiki-links resolve regardless of capitalisation.
- **Image width hint ignored** — `![[image.png|200]]` captures the `200` as `caption` but never applies it to the `<img>` tag as a `width` style or attribute. Treat a purely numeric pipe value as a pixel-width hint.
- **`_eval_dv_condition` silent pass-through** — Unrecognised WHERE conditions always return `True`, silently including all rows. Add a fallback that logs a warning and returns `False` (or raises) instead of invisibly matching everything.
- **Auto-listing post dicts are incomplete** — The synthetic dicts generated for sections with no explicit index file (in `posts.py`) are missing `reading_time`, `toc`, `labels`, `metadata`, `banner`, and other keys that templates may reference, which can cause `AttributeError` / `UndefinedError` in edge cases. Populate all keys with safe defaults.

## Medium Priority

- **Next / previous post navigation** — Add "← Older" / "Newer →" links at the bottom of individual post pages, ordered by date within the same section.
- **Collapsible callouts** — Obsidian supports `> [!type]- Title` (collapsed by default) and `> [!type]+ Title` (expanded). `convert_callouts()` currently ignores the `+`/`-` modifier. Render collapsed ones as `<details>`.
- **Visible image captions** — Single-image embeds with a pipe label (`![[photo.png|A sunset]]`) already store the caption in `data-caption`, but no `<figcaption>` is rendered below the image. Wrap in `<figure>` and emit `<figcaption>` when the caption is non-numeric.
- **`![[Note#Heading]]` partial transclusion** — Currently `convert_transclusion` embeds the entire target note. Add support for transcluding only the content under a specific heading (already partially handled by ignoring the `#...` fragment).
- **Dataview LIMIT clause** — The parser recognises `LIMIT` in the keyword list but `_execute_dv_query` never reads it. Apply it as a post-sort slice.
- **Section RSS feeds** — Expose `/blog/feed.xml`, `/gallery/feed.xml`, etc. per top-level section so readers can subscribe to individual sections independently.
- **Labels index page** — Add a `/labels` route that lists all labels alphabetically with post counts, and link to it from the nav (opt-in via a frontmatter tag, similar to `search`).
- **`lstrip("> ")` over-strips callout titles** — In `convert_callouts`, `line.lstrip("> ")` removes any leading `>`, space, or `"` characters from the start of the title text as well, not just the blockquote prefix. Use a fixed-width strip (`line[2:]` or a regex) instead.
- **`og:image` missing on listing pages** — `listing.html` never sets `og:image`. If the section has a banner or a featured post with a banner, use it.
- **`book.html` missing breadcrumbs and related posts** — Parity with `post.html`; the book template only has a bare `← Back` link.
- **Vault-wide attachments folder** — Obsidian lets users configure a single `_attachments/` at vault root rather than per-folder. Support a `ATTACHMENTS_PATH` env var (or auto-detect) to allow vault-root media resolution as a fallback.

## Ideas & Features

- **Dataview LIST type** — `LIST` queries are common in Obsidian vaults; add support alongside TABLE so that `LIST field FROM #tag` renders a `<ul>`.
- **Next/prev within label** — Label archive pages could also show prev/next post navigation scoped to that label.
- **Author field on post pages** — If frontmatter contains `author`, display it below the title in `post.html` (similar to how `book.html` shows author). Useful for multi-author blogs.
- **Date last modified** — Track `updated` or `modified` frontmatter and show "Last updated …" on post pages when it differs from `date`. Also include it in the sitemap as `<lastmod>`.
- **Social / `rel="me"` links** — Add optional `social_links` config (env var or homepage frontmatter) that renders `rel="me"` links in the footer/header for Mastodon verification and social profiles.
- **Comment system integration** — Add opt-in Giscus (GitHub Discussions) or utterances embed block at the bottom of `post.html`, configurable via env vars.
- **Dataview GROUP BY flattened display** — Currently GROUP BY produces grouped contexts but there is no way to render them as collapsible sections. A grouped list view would be a natural extension.
- **Responsive / mobile nav** — The current `<nav>` is a flat horizontal list with no hamburger menu; on narrow viewports it wraps awkwardly. Add a collapsible mobile menu.
- **Print stylesheet** — Add `@media print` rules to hide nav, sidebar, and interactive elements and format the post body for clean printing / PDF export.
- **Inline Dataview: `dv.pages()` expression** — Extend `convert_dataview_inline` beyond `this.*` fields to support simple cross-note expressions like `` `= dv.pages("#tag").length` ``.
- **Canvas file rendering** — Obsidian `.canvas` files are JSON; render them as a read-only visual board (SVG or simple positioned-div layout) so they can be included in the blog.

## Bugs & Findings

- **Mermaid inner background** — Mermaid v11 injects an inline `style` background on the SVG that can't be reliably overridden via CSS or `themeVariables`. The current post-render JS strip in `base.html` is a workaround; needs investigation into the correct Mermaid v11 API to suppress it at initialisation time.

## Done

- Write a README.md
- RSS feed (`/feed.xml`)
- OpenGraph / Twitter Card meta tags
- Custom 404 page
- Sitemap (`/sitemap.xml`)
- `menu_order` frontmatter for pinning pages to the top nav
- PolyForm Noncommercial 1.0.0 license
- Canonical URL tags (`<link rel="canonical">`)
- Table of contents (collapsible block at top of post)
- Reading time estimate (on post pages and listing cards)
- Pagination on listing pages (20 posts per page)
- Search result highlighting (matches highlighted in title + summary)
- Tag archive pages (`/tag/<tag>`) with links from post pages
- Search link in top nav (opt-in via `search` tag on root homepage)
- Tag filter dropdown on search page
- Breadcrumb navigation on post pages
- Bug fixes: reload lock, unchecked file reads, VAULT_PATH stderr warning, wiki-link pipe aliases
- JSON-LD structured data (Article, Book, WebSite schemas)
- `==highlight==` syntax → `<mark>` tags
- Footnotes — `[^1]` / `[^note]` syntax via Python-Markdown `footnotes` extension
- Mermaid diagrams — ` ```mermaid ``` ` blocks rendered via client-side Mermaid.js
- Math / LaTeX — `$inline$` and `$$block$$` via KaTeX
- Note transclusion — `![[Note Title]]` embeds note content inline
- `[[Link#Heading]]` anchor links
- Audio embeds — `![[audio.mp3]]` → `<audio>` element
- `aliases` frontmatter — alternate wiki-link names
- Related posts — "See also" section scored by shared labels and section
- Dark / light mode toggle — CSS variables, localStorage persistence
- Inline body labels — `#hashtag` in note body collected as labels
- Dataview inline queries — `` `= this.field` `` in prose
- Block references — `^block-id` anchor targets; `[[Note^id]]` links
- Private note placeholder pages — vault notes that exist but aren't published show a friendly "not published" page
- Book template — `📚book` tag renders a dedicated book-review layout with cover, metadata, and JSON-LD Book schema
- Banner images — `banner`/`banner_x`/`banner_y` frontmatter renders a full-width hero on post pages
- Dataview TABLE queries — `dataview` fenced blocks execute against the vault index
- Label archive pages (`/label/<name>`) with links from post pages
- Auto-generated section listing routes for folders with no explicit index file
