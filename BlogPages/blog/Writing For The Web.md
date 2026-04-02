---
tags:
  - blog
  - featured
labels:
  - obsidian
  - workflow
  - writing
date: 2026-01-15
title: Writing for the Web Without Leaving Obsidian
slug: writing-for-the-web
priority: 0
summary: The full authoring workflow — from blank note to published post — without ever touching a CMS, an export tool, or a terminal.
banner: https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1400&auto=format&fit=crop
banner_x: 0.5
banner_y: 0.4
---

The pitch is simple: write in Obsidian, save the file, refresh the browser. That is the entire publishing workflow. No build step, no CMS login, no export. This post walks through what that actually looks like in practice — and shows off a few things the engine can do along the way.

> [!abstract] What You Will See Here
> A full tour of the authoring experience: frontmatter, images (slider + lightbox), callouts, nested checklists, and the live-reload cycle. All rendered from a single `.md` file in a vault folder.

---

## The Frontmatter Contract

Everything about how a note behaves on the site is declared in the YAML frontmatter at the top of the file. You write it once; the engine does the rest.

```yaml
---
tags:
  - blog        # publishes the note; "website" also works
  - featured    # promotes it to the Featured section of the listing
date: 2026-01-15
title: Writing for the Web Without Leaving Obsidian
slug: writing-for-the-web   # optional; derived from title if omitted
priority: 1                 # featured sort order (0 = first)
summary: "Shown on the listing page. Auto-derived from content if omitted."
banner: "https://images.unsplash.com/..."
labels:
  - obsidian
  - workflow
  - writing
---
```

`tags` controls engine behaviour — reserved words the server acts on. `labels` are for readers — they appear as clickable badges on the post and power the label filter on the search page.

---

## Images: Slider vs Lightbox

How images are arranged on the page is controlled entirely by how they sit in the source markdown.

**Same line → slider.** Three images on one line become a swipeable gallery:

![[test_image_1.jpg]] ![[test_image_2.jpg]] ![[test_image_3.jpg]]

**Separate lines → lightbox.** Each image on its own line becomes a standalone lightbox:

![[test_image_1.jpg]]
![[test_image_2.jpg]]

Click any image above to open the lightbox. Images live in a `_attachments/` folder alongside the `.md` file — the engine resolves the path automatically.

---

## Callouts

Obsidian's callout syntax (`> [!type] Title`) is rendered into styled blocks. All standard Obsidian callout types are supported.

> [!info] Context
> Use `info` for neutral background or explanatory notes that sit outside the main narrative.

> [!tip] Shortcut
> If you omit the `summary` field, the engine auto-derives it from the first paragraph of content. You only need to write it explicitly when you want something different on the listing page.

> [!warning] Watch Out
> Filenames and `slug` values both feed into URL generation. If you rename a note after it has been live, its URL changes. Update any wiki-links that point to it.

> [!danger] Do Not Do This
> Do not put `listing` and `homepage` on the same file. `listing` wins, and your hand-written content will never be shown. Pick one.

---

## Wiki-Links Across Sections

Standard Obsidian `[[Note Title]]` syntax works across the entire vault. The engine builds a slug-to-URL index in a first pass before rendering any markdown, so links resolve correctly regardless of where the target file lives.

A post in `/blog` can link to a post in `/gallery` — [[Watercolor Algorithms]], for instance — and the URL will be correct. No path prefixes needed.

You can also link directly to a heading within a note: `[[Note Title#Heading]]` resolves to the page URL plus a `#heading-slug` anchor. And if a note has `aliases` in its frontmatter, any of those alternate names work as link targets too.

---

## Math and Diagrams

Write LaTeX math directly in your notes. Inline: $f(x) = x^2 + 2x + 1$. Or as a centred block:

$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$

For diagrams, a fenced `mermaid` block renders a live diagram:

```mermaid
flowchart LR
    Write[Write in Obsidian] --> Save[Save file]
    Save --> Reload[Server hot-reloads]
    Reload --> View[Refresh browser]
    View --> Write
```

Both are rendered without any special Obsidian plugin — just standard note syntax.

---

## The Publishing Checklist

The engine renders Obsidian-style checkboxes, including nested lists. Here is what a typical publish workflow looks like:

- [x] Write the post in Obsidian
    - [x] Add frontmatter (`tags`, `title`, `date`, `labels`)
    - [x] Add a `summary` if the auto-derived one is wrong
    - [x] Place images in `_attachments/` subfolder
- [x] Check the live preview
    - [x] Refresh the browser — no restart needed
    - [x] Verify wiki-links resolve (hover shows the URL)
    - [x] Confirm the post appears in the section listing
- [ ] Optional polish
    - [ ] Add a `banner` image URL with focal point (`banner_x`, `banner_y`)
    - [ ] Set `priority` if it should rank in Featured
    - [ ] Add `menu_order` if it should appear in the top nav

---

## The Live-Reload Cycle

On every request, the server checks whether any file in the vault has changed. If it has, the entire vault is rescanned before the response is sent. Edit a note, hit save, refresh the page — the change is there.

This makes the authoring cycle genuinely tight. You are not context-switching between a writing tool and a publish interface. Obsidian *is* the publish interface.

---

For a deeper look at how the server actually processes these files under the hood, see [From Vault to Web: How This Blog Works](/blog/how-this-blog-works).
