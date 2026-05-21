---
website: true
title: Frontmatter Reference
date: 2026-01-01
summary: Every frontmatter field InkStone recognises, with type and example.
featured: true
priority: 1
---

| Field | Type | Description | Example |
|---|---|---|---|
| `website` | boolean | **Required to publish.** Set to `true`. | `website: true` |
| `type` | string | Page type. One of: `homepage`, `listing`, `book`, `translations`. Omit for regular posts. | `type: listing` |
| `title` | string | Overrides H1 and filename as the display title. Quote if it contains a colon. | `title: "From Vault to Web: A Guide"` |
| `slug` | string | Manual URL slug. Overrides auto-generated slug. Used as-is, bypassing transliteration. | `slug: my-custom-url` |
| `date` | date | Publication date. Used for listing sort order and RSS. | `date: 2026-03-21` |
| `updated` | date | Last-updated date. Shown as "Updated …" in post meta; used in JSON-LD `dateModified`. | `updated: 2026-04-01` |
| `summary` | string | Shown on listing cards. Auto-derived from content if omitted. Quote if it contains a colon. | `summary: "A short description."` |
| `featured` | boolean | Shows post in the Featured section of its parent listing page. | `featured: true` |
| `priority` | integer | Sort order for featured posts. `0` = top, then `1`, `2`… Date breaks ties. | `priority: 0` |
| `author` | string or list | Shown in post meta and JSON-LD. | `author: "Jane Doe"` |
| `tags` | list | Content tags. Creates `/tag/<name>` archive pages. Merged with inline `#hashtags`. | `tags: [python, philosophy]` |
| `menu_order` | integer | Pins this post to the top nav. Lower value = further left. Appended after section links. | `menu_order: 1` |
| `access_token` | string | Per-note private access token. Share URL as `/slug?token=secret`. | `access_token: mysecret` |
| `lang` | string | Language code for this note variant. Serves at `/{slug}/{lang}` and adds language toggle. | `lang: ru` |
| `language` | string | Root homepage only. Sets site default language for `<html lang="">`. | `language: en` |
| `default_theme` | string | Root homepage only. Initial theme for new visitors: `dark`, `light`, or `system`. | `default_theme: dark` |
| `show_search` | boolean | Root homepage only. Adds a Search link to the top nav. | `show_search: true` |
| `show_tags` | boolean | Root homepage only. Adds a Tags link to the top nav. | `show_tags: true` |
| `banner` | string | Filename of the banner image (from `_attachments/`). Shown as a wide header image. | `banner: cover.jpg` |
| `banner_y` | float | Vertical focal point of the banner image. `0.0` = top, `1.0` = bottom. Default `0.5`. | `banner_y: 0.3` |
| `icon` | string | Path to a small icon shown in the site header. | `icon: /static/logo.png` |
| `aliases` | list | Alternate slugs that redirect to this note. | `aliases: [old-slug, another-name]` |
| `site_title` | string | Overrides the displayed header title for this page and all its children (does not affect the URL or `<title>` tag). Cascades down the URL tree. | `site_title: "InkStone"` |
| `banner_x` | float | Horizontal focal point of the banner image. `0.0` = left, `1.0` = right. Default `0.5`. | `banner_x: 0.3` |
