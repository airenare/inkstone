---
website: true
title: SEO and Feeds
date: 2026-01-01
summary: RSS feeds, sitemap, OpenGraph meta tags, JSON-LD structured data, and print styles.
featured: true
priority: 7
---

## RSS

A global RSS feed is available at `/feed.xml` — the latest 20 posts across all sections, sorted by date.

Per-section feeds are available at `/{section}/feed.xml`:

- `/blog/feed.xml`
- `/gallery/feed.xml`

Feeds include title, date, summary, and full post URL.

## Sitemap

An XML sitemap is auto-generated at `/sitemap.xml`. It includes all published posts, listing pages, and the homepage. Updated automatically when notes change.

## OpenGraph and Twitter Card

Every post page includes `<meta>` tags for social sharing:

- `og:title`, `og:description`, `og:url`
- `og:image` — the post's banner image, or the first embedded image found in the body
- `twitter:card`, `twitter:title`, `twitter:description`

These are generated from `title:`, `summary:`, `banner:`, and the post URL. No manual configuration required.

## JSON-LD structured data

InkStone injects JSON-LD `<script>` blocks for search engine understanding:

| Page type | JSON-LD type |
|---|---|
| Regular post | `Article` |
| `type: book` note | `Book` |
| Root homepage | `WebSite` |

`datePublished` comes from `date:`. `dateModified` comes from `updated:` (falls back to `date:` if absent). `author` comes from the `author:` frontmatter field.

## Print stylesheet

InkStone includes a `@media print` stylesheet for clean PDF output and printing. Navigation, sidebars, and interactive elements are hidden; prose content is formatted for paper.

## Reading time

An estimated reading time is calculated and shown on post pages and listing cards. Based on average reading speed (~200 wpm) applied to the word count of the rendered body.
