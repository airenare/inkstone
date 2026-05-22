---
website: true
title: Navigation
date: 2026-05-21
summary: How nav links are generated, how to pin standalone pages, and breadcrumb behaviour.
featured: true
priority: 2
---

## Auto-generated nav

Section listing pages automatically appear as top-level nav links. A vault with these folders:

```
vault/
├── blog/Blog.md      (type: listing)
├── gallery/Gallery.md  (type: listing)
└── projects/Projects.md  (type: listing)
```

Produces nav links: **Blog · Gallery · Projects** (in filesystem order).

No configuration required. Add a `type: listing` file to a folder — it appears in the nav.

## Hiding sections from the nav

A section appears in the nav by default. To hide it, add `nav_hidden: true` to the listing or homepage file for that section:

```yaml
---
website: true
type: listing
title: Archive
nav_hidden: true
---
```

The section is still fully routable — visitors can reach it via direct links or wiki-links. It simply won't appear as a nav item.

## Pinning pages with menu_order

Any note can be pinned to the nav by adding `menu_order:` to its frontmatter:

```yaml
---
website: true
title: About
menu_order: 1
---
```

- Lower value = further left in the nav
- Pinned pages are appended **after** the auto-generated section links
- Multiple pages with `menu_order:` are sorted by value

Example: an About page pinned after all section links:

```yaml
---
website: true
title: About
menu_order: 10
---
```

This is the intended mechanism for root-level standalone pages that should be discoverable. See [[URL Mapping#Root-level standalone pages]].

## Breadcrumbs

Every post page shows a breadcrumb trail:

```
Home › Blog › My Post Title
```

Each segment is a clickable link. The breadcrumb reflects the URL structure — nesting matches folder depth.

## Next / Previous navigation

Within a section, posts show previous/next links at the bottom:

```
← Older post title          Newer post title →
```

Ordering is by `date:` frontmatter descending (newest first on listing pages, so "newer" = more recent date).
