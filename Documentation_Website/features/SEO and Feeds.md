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

A `<link rel="alternate" type="application/rss+xml">` tag is included in every page's `<head>`, so browsers and feed readers auto-discover the feed without any manual wiring.

## Sitemap

An XML sitemap is auto-generated at `/sitemap.xml`. It includes all published posts, listing pages, and the homepage. Updated automatically when notes change.

## OpenGraph and Twitter Card

Every post page includes `<meta>` tags for social sharing:

- `og:title`, `og:description`, `og:url`
- `og:image`: the post's banner image, or the first embedded image found in the body
- `twitter:card`, `twitter:title`, `twitter:description`
- `<meta name="description">`: standard HTML description tag, mirrors `og:description`

These are generated from `title:`, `summary:`, `banner:`, and the post URL. No manual configuration required.

## JSON-LD structured data

InkStone injects JSON-LD `<script>` blocks for search engine understanding:

| Page type | JSON-LD type |
|---|---|
| Regular post | `Article` |
| `type: book` note | `Book` |
| Root homepage | `WebSite` |

`datePublished` comes from `date:`. `dateModified` comes from `updated:` (falls back to `date:` if absent). `author` comes from the `author:` frontmatter field.

## AI Discoverability

AI search engines (ChatGPT, Perplexity, Google AIO, Claude) cite content they can crawl and understand. InkStone handles the technical side automatically — no configuration needed.

### robots.txt

A `robots.txt` file is auto-generated at `/robots.txt`. It explicitly allows all major AI crawlers:

- `GPTBot` (OpenAI)
- `ClaudeBot` (Anthropic)
- `PerplexityBot` (Perplexity AI)
- `Google-Extended` (Google Gemini)
- `CCBot` (Common Crawl)

All crawlers receive `Allow: /`. The file also includes a `Sitemap:` reference pointing to `/sitemap.xml`. No configuration required.

### llms.txt

An `llms.txt` file is auto-generated at `/llms.txt` following the [llmstxt.org](https://llmstxt.org) standard. It helps AI systems understand the structure and content of your site.

The file includes:

- Site name and homepage description
- Top-level sections with links
- Up to 20 recent posts with titles, URLs, and summaries
- A link to the RSS feed

No configuration required — the file is built automatically from published posts and section routes.

## Print stylesheet

InkStone includes a `@media print` stylesheet for clean PDF output and printing. Navigation, sidebars, and interactive elements are hidden; prose content is formatted for paper.

## Reading time

An estimated reading time is calculated and shown on post pages and listing cards. Based on average reading speed (~200 wpm) applied to the word count of the rendered body.
