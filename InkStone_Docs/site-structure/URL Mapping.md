---
website: true
title: URL Mapping
date: 2026-01-01
summary: "How vault folder paths become website URLs."
featured: true
priority: 0
---

## Vault path → URL

| Vault path | URL | Notes |
|---|---|---|
| `Home.md` with `type: homepage` | `/` | Site root |
| `blog/Blog.md` with `type: listing` | `/blog` | Section index |
| `blog/My Post.md` | `/blog/my-post` | Regular post |
| `gallery/arts/Photo.md` | `/gallery/arts/photo` | Nested subfolder |
| `About.md` (vault root, no type) | `/about` | Root-level standalone |
| `blog/My Board__website.canvas` | `/blog/my-board` | Canvas |
| `blog/Posts__website.base` | `/blog/posts` | Base table |

The section is determined by the folder. Notes in the vault root have no section prefix.

## Slug generation rules

Starting from the resolved title (see [[Publishing Notes#Title resolution order]]):

1. Lowercase the string
2. Transliterate non-ASCII characters to ASCII (Cyrillic → Latin, Greek → Latin, etc.)
3. Replace spaces with hyphens
4. Strip characters that are not alphanumeric or hyphens
5. Collapse consecutive hyphens

**Manual override:** set `slug:` in frontmatter to bypass all of the above. The value is used exactly as written.

```yaml
---
website: true
title: "Привет мир"
slug: hello-world
---
```

→ URL: `/hello-world`

## Root-level standalone pages

Files in the vault root without `type: homepage` or `type: listing` are intentionally unlisted. They don't appear in auto-generated section listings. Intended usage:

- Link to them via `[[wiki-links]]` from other content
- Pin them to the nav via `menu_order:` frontmatter

See [[Navigation]] for the `menu_order` mechanism.
