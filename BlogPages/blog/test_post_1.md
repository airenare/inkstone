---
tags:
  - blog
  - featured
labels:
  - obsidian
  - python
  - architecture
date: 2026-01-20
title: From Vault to Web: How This Blog Works
slug: how-this-blog-works
priority: 0
summary: This site is an Obsidian vault served directly by a Python server — no build step, no CMS, no export. Here is how it works under the hood.
banner: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1400&auto=format&fit=crop"
banner_x: 0.5
banner_y: 0.45
---

Every page you read here was written as a plain `.md` file in Obsidian. There is no export step, no CMS, no build pipeline. A small Python server reads the vault directly and serves it as a website. This post explains how.

> [!abstract] TL;DR
> Vault folder structure → URL structure. Frontmatter tags control publishing. A two-pass loader resolves wiki-links across sections. Markdown is converted server-side, including Obsidian-native syntax like callouts, image embeds, and checkboxes.

---

## The Core Idea

Your vault's folder structure *is* your URL structure:

| Vault path | URL |
|---|---|
| `blog/My Post.md` | `/blog/My-Post` |
| `gallery/Neon Dreams.md` | `/gallery/Neon-Dreams` |
| `About.md` (vault root) | `/About` |

A note is only published if it has `blog` or `website` in its frontmatter `tags`. Everything else stays private — still queryable by Dataview, but showing a placeholder page if you navigate to its URL directly. No accidental publishing.

---

## The Markdown Pipeline

Raw Obsidian markdown goes through six transformations before it reaches the browser:

| Step | What it does |
|---|---|
| `strip_leading_h1` | Removes `# Title` — the template renders it from frontmatter |
| `convert_media` | `![[file.jpg]]` → lightbox image or slider gallery |
| `convert_links` | `[[Wiki Link]]` → resolved `<a href>` using the URL index |
| `convert_callouts` | `> [!type] Title` → styled callout block |
| `convert_checkboxes` | `- [ ]` / `- [x]` → HTML checkbox lists with nesting |
| `markdown.markdown()` | Tables, fenced code, TOC, syntax highlighting |

> [!tip] Two-pass loading
> Wiki-links are resolved in a *second* pass, after every file in the vault has been scanned. This means a post in `/blog` can correctly link to a post in `/gallery` even if the gallery was loaded after the blog. The slug-to-URL index is built first, then markdown is rendered.

---

## The Frontmatter System

Everything about how a note behaves on the website is controlled by its frontmatter:

```yaml
---
tags:
  - blog        # publishes the note as a web page
  - featured    # promotes it to the featured section of its listing
date: 2026-01-20
title: My Post
labels:
  - python
  - obsidian
summary: "Shown on listing pages. Auto-derived if omitted."
banner: "https://images.unsplash.com/..."
priority: 0     # 0 = top featured post, 1 = second, and so on
---
```

`tags` drive engine behaviour — they are reserved words. `labels` are for readers — they appear as clickable badges on the post page and power the label filter on the search page.

---

## What's Happening on Each Request

```python
def serve(path):
    post_store.maybe_reload()   # re-scan vault if any file changed
    url_path = "/" + path

    if url_path in SECTION_ROUTES:
        # homepage or auto-generated listing
        return render_template("listing.html", ...)

    if url_path in ALL_POSTS:
        # regular post
        return render_template("post.html", post=post)

    abort(404)
```

The server checks file modification times on every request and reloads the vault if anything changed. Edit a note, save it, refresh the browser — done. No restart, no rebuild.

---

## Shipped Features

- [x] Wiki-links (`[[Note Title]]`) resolved across all sections
- [x] Callouts — all Obsidian types rendered with icons and colour
- [x] Image lightbox and slider galleries from `![[embed]]` syntax
- [x] Table of contents — auto-generated from headings, collapsible
- [x] Labels — clickable badges linking to archive pages
- [x] Full-text search with label filtering
- [x] RSS feed at `/feed.xml`
- [x] Sitemap at `/sitemap.xml`
- [x] Dataview `TABLE` queries rendered server-side
- [x] Banner images with focal point control
- [x] Hot-reload — no restart needed while writing
- [ ] Related posts
- [ ] Dark / light mode toggle

---

For the authoring side of things — what it actually feels like to write posts — see [[Writing for the Web Without Leaving Obsidian]].
