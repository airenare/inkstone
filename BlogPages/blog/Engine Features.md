---
website: true
tags:
  - blog
  - obsidian
  - features
  - demo
date: 2026-04-02
updated: 2026-04-02
author: The Engine
title: Engine Features Showcase
slug: engine-features
summary: Related posts, dark/light mode, inline hashtags, Dataview queries, block references, Dataview LIST, GROUP BY, author field, and more — all demonstrated in one post.
---

This post demonstrates features from v1.8.0–v1.11.0. It exists to give each feature something live to point at.

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

---

## Author Field

This post has `author: The Engine` in its frontmatter. You should see it in the meta line below the title. It can also be a list:

```yaml
author:
  - Alice
  - Bob
```

---

## Date Last Modified

The `updated:` frontmatter field shows an "Updated" date in the post meta when it differs from `date`. This post has both set to the same date, so nothing extra appears here — but try setting `updated: 2027-01-01` to see it in action.

---

## Dataview LIST

A simple `LIST` query renders a `<ul>` instead of a table:

```dataview
LIST
FROM #generative-art
SORT file.name ASC
```

---

## Dataview GROUP BY

A `TABLE` with `GROUP BY` renders a heading per group with a sub-table of its rows:

```dataview
TABLE date, summary
FROM #demo 
GROUP BY section
SORT date DESC
LIMIT 6
```

---

## Mobile Nav

Shrink this window below 600 px. The nav links collapse into a hamburger ☰ menu that toggles open on tap. The site name and theme toggle always stay visible.

---

For the full technical picture of how the engine works, see [From Vault to Web: How This Blog Works](/blog/how-this-blog-works).
