# TODO / Backlog


## High Priority

_(all done — see Done section)_

## Medium Priority

- **Use only lowercase URLs**

## Ideas & Features

- **Social / `rel="me"` links** — Add optional `social_links` config (env var or homepage frontmatter) that renders `rel="me"` links in the footer/header for Mastodon verification and social profiles.
- **Comment system integration** — Add opt-in Giscus (GitHub Discussions) or utterances embed block at the bottom of `post.html`, configurable via env vars.
- **Inline Dataview: `dv.pages()` expression** — Extend `convert_dataview_inline` beyond `this.*` fields to support simple cross-note expressions like `` `= dv.pages("#tag").length` ``.
- **Canvas file rendering** — Obsidian `.canvas` files are JSON; render them as a read-only visual board (SVG or simple positioned-div layout) so they can be included in the blog.

## Bugs & Findings

- **Mermaid inner background** — Mermaid v11 injects an inline `style` background on the SVG that can't be reliably overridden via CSS or `themeVariables`. The current post-render JS strip in `base.html` is a workaround; needs investigation into the correct Mermaid v11 API to suppress it at initialisation time.

## Done

- Security: path traversal guard — `os.path.realpath()` containment check in `convert_media` (slider + single-embed) and `convert_transclusion`
- Performance: `maybe_reload` debounce — 2 s `_last_check_time` guard skips vault walk on rapid requests

- Dataview LIST type — `LIST [field] FROM #tag` renders a `<ul>` with optional field annotation
- Dataview GROUP BY flattened display — grouped TABLE/LIST renders a heading per group + sub-table/sub-list
- Author field on post pages — `author:` frontmatter shown in post meta + JSON-LD (single or list)
- Date last modified — `updated:`/`modified:` frontmatter shown in post meta and JSON-LD `dateModified`
- Next/prev within label — label archive pages show inline older/newer links per post entry
- Responsive mobile nav — hamburger button, slide-down menu, single-column layout under 600 px
- Print stylesheet — `@media print` hides nav/chrome, resets colours, appends link URLs
- Next / previous post navigation ("← Older" / "Newer →") on post and book pages
- Collapsible callouts: `> [!type]-` collapses, `> [!type]+` expands; rendered as `<details>`
- Fixed `lstrip("> ")` over-stripping callout titles — now uses regex to strip only the blockquote prefix
- Visible image captions: `![[photo.jpg|Caption]]` renders `<figure>` + `<figcaption>`
- `![[Note#Heading]]` partial transclusion — only embeds content under the specified heading
- Dataview `LIMIT N` clause now applied as a post-sort slice
- Section RSS feeds: `/blog/feed.xml`, `/gallery/feed.xml`, etc.
- Labels index page at `/labels` with post counts; opt-in via `labels` tag on root homepage
- `og:image` on listing pages: uses section banner or first featured post banner
- `book.html` now has breadcrumbs and "See also" related posts (parity with `post.html`)
- Vault-wide attachments: falls back to vault root `_attachments/` then `ATTACHMENTS_PATH` from `.env`
- Fix `requirements.txt`: removed duplicate PyYAML entry, bumped gunicorn to 21.2.0
- Fix invalid HTML: removed stray `<script>` block between `</head>` and `<body>`
- Remove `hljs.initLineNumbersOnLoad()` call (extension was never loaded)
- Search now strips HTML tags before storing `content` field — no more false matches on tag attributes
- Wiki-link lookup is now case-insensitive (`url_index` keys stored lowercase; `convert_links` looks up lowercase)
- Image width hint: `![[image.png|200]]` now applies `style="max-width:200px"` to the `<img>` tag
- `_eval_dv_condition` logs a warning and returns `False` for unrecognised WHERE conditions instead of silently returning `True`
- Auto-listing post dicts now populated with all safe defaults (`toc`, `reading_time`, `labels`, `metadata`, `banner`, etc.)

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
