---
tags:
  - blog
labels:
  - obsidian
  - features
  - demo
date: 2026-04-02
title: Five More Engine Features
slug: engine-features
summary: Related posts, dark/light mode, inline hashtags, Dataview inline queries, and block references — all demonstrated in one post.
---

This post demonstrates five features added in v1.8.0. It exists to give each one something live to point at.

---

## Related Posts

Scroll to the bottom of this page. You should see a **See also** section with links to posts that share labels with this one. The engine scores candidates by shared label count (×2) plus a point for being in the same section, then takes the top four.

No frontmatter required — it's automatic.

---

## Dark / Light Mode

The ☀ button in the top-right of the header toggles between dark (Catppuccin) and light themes. Your preference is stored in `localStorage` and restored on every page load.

---

## Inline Hashtags

Any `#hashtag` written directly in the note body is automatically collected as a label — no need to list it in frontmatter. This post has `#obsidian`, `#features`, and `#demo` in its frontmatter, but this sentence also mentions #engine and #v1-8-0, which will appear as clickable badges too.

Labels from both sources are merged and deduplicated.

---

## Dataview Inline Queries

`` `= expr` `` evaluates a Dataview expression against the current note's frontmatter. The title of this post is: `= title`. It was published on: `= date`.

This is the same expression language used in `TABLE` blocks, but inline in prose. Useful for auto-populating recurring metadata without copy-pasting.

---

## Block References

Any paragraph can be given a stable ID by appending `^block-id` at the end. Then `[[Note^block-id]]` links directly to that paragraph. ^demo-block

The paragraph above has the ID `demo-block`. A link like `[[Engine Features^demo-block]]` resolves to `/blog/engine-features#demo-block` and scrolls to that exact paragraph.

---

For the full technical picture of how the engine works, see [From Vault to Web: How This Blog Works](/blog/how-this-blog-works).
