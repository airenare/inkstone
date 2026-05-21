---
website: true
title: Search and Tags
date: 2026-01-01
summary: "Full-text search, tag pages, tags index, and inline hashtags."
---

## Full-text search

Available at `/search`. Searches across all published posts — titles, summaries, and body content. Results are highlighted.

Enable the search link in the top nav by adding `show_search: true` to the root homepage:

```yaml
---
website: true
type: homepage
show_search: true
---
```

The search input is auto-focused when the page loads. Results can be filtered by tag.

## Tag pages

Every tag automatically gets an archive page at `/tag/<name>` listing all posts with that tag.

Tags come from two sources, merged automatically:

1. `tags:` list in frontmatter: `tags: [python, philosophy]`
2. Inline `#hashtags` in the note body: `This uses #python and #flask.`

## Tags index

A full tags index with post counts is available at `/tags`.

Enable the link in the top nav:

```yaml
---
website: true
type: homepage
show_tags: true
---
```

## Related posts

Post pages include an automatic "See also" section. Related posts are scored by:

- Shared tags (each shared tag counts ×2)
- Same section (a smaller bonus)

The top 3–5 most related posts are shown.
