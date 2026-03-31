---
tags:
  - blog
date: 2026-01-16
title: Test Post Two
---

# Test Post Two

This post covers image sliders, additional callout types, and nested checkboxes. See also [[Test Post One]] for text formatting, tables, and code examples.

---

## Image Slider

Three images on one line become a slider gallery. Use the arrows or swipe to navigate.

![[test_image_1.png]] ![[test_image_2.png]] ![[test_image_3.png]]

---

## More Callout Types

> [!info] Information
> This is an info callout. Good for neutral context or background explanation.

> [!abstract] Summary
> Use the abstract callout to provide a TL;DR or summary at the top of a long post.

> [!danger] Danger
> This is a danger callout. Reserve it for critical errors or destructive actions.

> [!tip] Tip
> A quick tip callout for helpful suggestions or shortcuts.

---

## Nested Checkboxes

- [ ] Backend tasks
    - [x] Parse frontmatter
    - [x] Convert wiki-links
    - [x] Render callouts
    - [ ] Add tag index page
        - [ ] Design template
        - [ ] Add route `/tag/<name>`
- [x] Frontend tasks
    - [x] Dark theme
    - [x] Lightbox gallery
    - [x] Image slider
    - [x] Code copy button

---

## Mixed Formatting in a Table

| Callout Type | Icon | Use Case              |
|--------------|------|-----------------------|
| `note`       | 📝   | General information   |
| `warning`    | ⚠️   | Potential issues      |
| `danger`     | 🔥   | Critical errors       |
| `info`       | ℹ️   | Background context    |
| `tip`        | 💡   | Helpful suggestions   |
| `abstract`   | 📋   | Summaries / TL;DR     |

---

## Code Block

```javascript
// Client-side slider navigation
document.querySelectorAll(".slider-gallery").forEach(gallery => {
    const slides = gallery.querySelector(".slides")
    const left = gallery.querySelector(".left")
    const right = gallery.querySelector(".right")
    let index = 0

    right.onclick = () => {
        index = Math.min(index + 1, slides.children.length - 1)
        slides.scrollTo({ left: slides.clientWidth * index, behavior: "smooth" })
    }
})
```
