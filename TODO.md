# TODO / Backlog


## High Priority

## Medium Priority

## Ideas & Features

- **Related posts** — "See also" section at post bottom based on shared tags or section
- **Dark/light mode toggle** — CSS variable swap; remember preference in localStorage
- **Inline body tags** — collect `#tag` mentions from note body, not just frontmatter
- **Dataview inline queries** — `` `= this.field` `` expressions inline in text
- **Block references** — `[[Note^block-id]]` links to a specific block within a note

## Bugs & Findings

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
