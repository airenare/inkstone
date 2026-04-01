# TODO / Backlog

Items are grouped by priority. Tell Claude "do the TODOs" or name specific items to implement them.

## High Priority

- **`==highlight==` syntax** — convert `==text==` to `<mark>` tags; one regex in `converters.py`
- **Footnotes** — `[^1]` / `[^note]` syntax; just enable the `footnotes` extension in `markdown.Markdown()`
- **Mermaid diagrams** — render ` ```mermaid ``` ` blocks via client-side mermaid.js

## Medium Priority

- **Math / LaTeX** — `$inline$` and `$$block$$` via KaTeX (client-side) or python-markdown-math
- **Note transclusion** — `![[Note Title]]` embeds another note's full markdown content inline (distinct from media)
- **`[[Link#Heading]]` anchor links** — resolve to `/path/to/note#heading-slug` instead of just the page root
- **Embedded audio** — `![[audio.mp3]]` → `<audio>` tag; images and video already handled
- **`aliases` frontmatter** — add alias slugs to `url_index` so wiki-links using alternate names resolve correctly

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
