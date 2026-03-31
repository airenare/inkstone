# TODO / Backlog

Items are grouped by priority. Tell Claude "do the TODOs" or name specific items to implement them.

## High Priority


## Medium Priority


## Ideas & Features

- **Related posts** — "See also" section at post bottom based on shared tags or section
- **Breadcrumb navigation** — for nested posts like `/gallery/arts/post`
- **JSON-LD structured data** — rich Google results; especially useful for book pages (Book schema)
- **Dark/light mode toggle** — CSS variable swap; remember preference in localStorage
- **Tag filter on search** — add tag facets or a dropdown to the `/search` page

## Bugs & Findings

- **No error handling in `serve()`** (`app.py`) — hard crash if post_store functions fail mid-request
- **Unchecked file reads** (`posts.py`) — no try/except around file open; missing files cause silent failures
- **`VAULT_PATH` not validated at startup** (`config.py`) — silently falls back to `./BlogPages` if path is invalid/missing; should warn loudly
- **Hot reload race condition** (`posts.py`) — `os.walk()` + `getmtime()` can miss rapid-fire changes; no locking
- **Regex fragility in wiki-link parser** (`converters.py`) — doesn't handle escaped brackets or pipes in link text

## Done

- Write a README.md
- RSS feed (`/feed.xml`)
- OpenGraph / Twitter Card meta tags
- Custom 404 page
- Sitemap (`/sitemap.xml`)
- `menu_order` frontmatter for pinning pages to the top nav
- MIT license
- Canonical URL tags (`<link rel="canonical">`)
- Table of contents (collapsible block at top of post)
- Reading time estimate (on post pages and listing cards)
- Pagination on listing pages (20 posts per page)
- Search result highlighting (matches highlighted in title + summary)
- Tag archive pages (`/tag/<tag>`) with links from post pages
