---
website: true
title: Links and Embeds
date: 2026-05-21
summary: Wiki-links, aliases, anchors, block references, and note transclusion.
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

> InkStone matches by slugified title, slugified filename, or the note's explicit `slug:` frontmatter — whichever matches first.

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
