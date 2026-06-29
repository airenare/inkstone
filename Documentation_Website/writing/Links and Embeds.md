---
website: true
title: Links and Embeds
date: 2026-05-21
summary: Wiki-links, aliases, anchors, block references, note transclusion, and note block embeds.
featured: true
priority: 3
tags:
  - writing
  - links
  - embeds
---

## Wiki-links

`[[Note Title]]` resolves to the published URL of the matching note:

```markdown
Read more in [[Frontmatter Reference]].
```
Read more in [[Frontmatter Reference]].

> InkStone matches by slugified title, slugified filename, or the note's explicit `slug:` frontmatter, whichever matches first.

---

## Aliases

`[[Note Title|Display Text]]` shows custom link text while linking to the note:

```markdown
See the [[Configuration Reference|config docs]] for all options.
```
See the [[Configuration Reference|config docs]] for all options.

---

## Heading anchors

Link to a specific heading within a note by appending `#Heading`:

```markdown
[[Markdown Features#Callouts]]
```
[[Markdown Features#Callouts]]

Renders as a link that scrolls directly to the Callouts section.

---

## Block references

Append `^block-id` at the end of any paragraph to give it a referenceable ID:

```markdown
This is an important paragraph. ^important-para
```

Link to it from another note:

```markdown
See [[Publishing Notes^important-para]] for details.
```
See [[Publishing Notes^important-para]] for details. 
> ↑ This will send you to the **Title resolution order** paragraph of **Publishing Notes** page.

---

## Note transclusion

`![[Note Title]]` embeds the full content of another published note inline:

```markdown
![[Transcluded Note]]
```

![[Transcluded Note]]

Embed a single section by adding a heading anchor:

```markdown
![[Transcluded Note#Why?]]
```

![[Transcluded Note#Why?]]

> [!warning] Published notes only
> Transclusion only works for notes that have `website: true` and exist in the same vault. References to unpublished or missing notes render as a broken-link placeholder.
---

## Note block embeds

The `note` fenced block embeds a specific published post inline, as a styled preview card or with its full content. Unlike transclusion (`![[]]`), it includes the post's title, date, and reading time as a header.

**Preview card** (excerpt + "Read more" link):

````markdown
```note /blog/my-post
```
````

**Full content** (entire post body, still with title and meta):

````markdown
```note /blog/my-post full
```
````

**Without date and reading time:** add `nodate` to suppress the meta line:

````markdown
```note /blog/my-post nodate
```
````

````markdown
```note /blog/my-post full nodate
```
````

Flags can be combined in any order. The path is the post's URL path, not its filename. It's the same URL you'd visit in a browser (e.g. `/blog/my-post`, not `My Post.md`). Works in any published note, including the homepage.

If the path doesn't resolve to a published note, InkStone renders a "Note not found" message in place of the block.

> [!tip] Choosing between `![[]]` and `note` block
> Use `![[Note Title]]` when you want raw content merged directly into the page with no visual break. Use ` ```note ``` ` when you want the embedded post to stand out as its own card, with its title, date, and a link back to the original.

---

## Canvas and base embeds

`![[BoardName.canvas]]` and `![[QueryName.base]]` embed interactive canvas boards and base table views inline. See [[Canvas Boards]] and [[Obsidian Bases]] for details.

InkStone also handles path-prefixed links that Obsidian's link picker generates, and strips `__website` / `__featured` markers and file extensions from both URLs and display text automatically, so `[[blog/My Board__website.canvas|My Board__website]]` renders as a clean link titled "My Board".
