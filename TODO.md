# TODO / Backlog


## High Priority

## Medium Priority

## Ideas & Features

## Bugs & Findings

- **Mermaid inner background** — Mermaid v11 injects an inline `style` background on the SVG that can't be reliably overridden via CSS or `themeVariables`. Needs investigation into the correct Mermaid v11 API to suppress it.

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
