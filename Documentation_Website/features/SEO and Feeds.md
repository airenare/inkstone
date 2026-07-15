---
website: true
title: SEO and Feeds
date: 2026-05-21
summary: RSS feeds, sitemap, OpenGraph meta tags, JSON-LD structured data, and print styles.
featured: true
priority: 7
tags:
  - features
---

## RSS

A global RSS feed is available at `/feed.xml`, covering the latest 20 posts across all sections, sorted by date.

Per-section feeds are available at `/{section}/feed.xml`:

- `/blog/feed.xml`
- `/gallery/feed.xml`

Feeds include title, date, summary, and full post URL.

Every page's `<head>` includes a `<link rel="alternate" type="application/rss+xml">` tag, so browsers and feed readers can find the feed automatically.

## Sitemap

An XML sitemap is auto-generated at `/sitemap.xml`. It includes all published posts, listing pages, and the homepage, and updates whenever notes change.

## OpenGraph and Twitter Card

Every post page includes `<meta>` tags for social sharing:

- `og:title`, `og:description`, `og:url`
- `og:image`: the post's banner image, or the first embedded image in the body
- `twitter:card`, `twitter:title`, `twitter:description`
- `<meta name="description">`: standard HTML description, mirrors `og:description`

All of these come from `title:`, `summary:`, `banner:`, and the post URL. Nothing to configure.

## JSON-LD structured data

InkStone injects JSON-LD `<script>` blocks for search engines:

| Page type | JSON-LD type |
|---|---|
| Regular post | `Article` |
| `type: book` note | `Book` |
| Root homepage | `WebSite` |

`datePublished` comes from `date:`. `dateModified` comes from `updated:` (falls back to `date:` if absent). `author` comes from the `author:` frontmatter field.

## AI discoverability

AI search engines cite content they can crawl and parse. InkStone generates the right files for both.

### robots.txt

`/robots.txt` is auto-generated and allows the major AI crawlers by name:

- `GPTBot` (OpenAI)
- `ClaudeBot` (Anthropic)
- `PerplexityBot` (Perplexity)
- `Google-Extended` (Gemini / AI Overviews)
- `CCBot` (Common Crawl)

All receive `Allow: /`. The file also points to `/sitemap.xml`.

### llms.txt

`/llms.txt` is auto-generated following the [llmstxt.org](https://llmstxt.org) standard. It gives AI systems a structured summary of the site: name, description, top-level sections with links, up to 20 recent posts with summaries, and the RSS feed URL. Built from published posts and section routes; nothing to configure.

## Print stylesheet

InkStone includes a `@media print` stylesheet. Navigation, sidebars, and interactive elements are hidden; prose is formatted for paper.

## Reading time

Post pages and listing cards show an estimated reading time, calculated from the rendered word count at roughly 200 wpm.
