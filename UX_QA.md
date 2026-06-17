# UX QA Checklist

Manual testing checklist to run before merging `ux-improvements` into `main`.
Check each item in both **dark** and **light** theme, and on **mobile** (≤ 600px) unless noted.

**Test server:**
```bash
VAULT_PATH=Documentation_Website /home/air/venv/3.14/bin/python3 app.py
```

---

## Group D — i18n

- [ ] On a multilingual site, paginate through a listing page (`?page=2`) — "Previous" and "Next" labels appear in the correct language, not English
- [ ] On a non-English post with Giscus comments enabled, the comment widget language matches the page language (not always English)

---

## Group B — Accessibility

- [ ] Tab to the page with keyboard only — a "Skip to content" link appears at the top on first Tab press, disappears again after Tab moves past it
- [ ] "Skip to content" click / Enter jumps focus to the main content area, bypassing the nav
- [ ] Tab through the page — every interactive element (nav links, tag badges, related cards, buttons, social links, TOC links, lightbox buttons) shows a visible accent-colored focus ring
- [ ] On the Search page, a screen reader (or browser inspector) reads the tag filter dropdown with a label ("Tags" or locale equivalent)
- [ ] Focus ring does NOT appear when using a mouse (only on keyboard navigation)

---

## Group M — Semantic `<time>`

- [ ] Inspect any post page in DevTools — date text is wrapped in `<time datetime="YYYY-MM-DD">` in the post meta
- [ ] Same for "Updated" date when present
- [ ] Check feed page — each entry date has `datetime` attribute
- [ ] Check listing page (featured and card meta) — dates have `datetime`
- [ ] Check search results — date has `datetime`
- [ ] Check tag archive page — date has `datetime`

---

## Group A — Lightbox

- [ ] Click a single standalone image — lightbox opens, **no** prev/next arrows shown (single image = no navigation)
- [ ] Click an image in a multi-image gallery block — lightbox opens **with** ‹ › arrows
- [ ] ‹ › arrows navigate correctly through the gallery images only (not across the whole page)
- [ ] Two separate image blocks on the same page — clicking an image in block 1 only navigates within block 1; clicking an image in block 2 only navigates within block 2
- [ ] × close button is visible in top-right corner and closes the lightbox
- [ ] Clicking the dark backdrop closes the lightbox
- [ ] Clicking the image itself does **not** close the lightbox
- [ ] Escape key closes the lightbox
- [ ] Arrow keys (←/→) navigate between images in a gallery
- [ ] On mobile: tap backdrop closes; tap × closes; swipe or tap arrows navigates

---

## Group C — Search UX *(implement before checking)*

- [ ] Search with no results — empty state shows top tags as badges + link to Tags page
- [ ] Search input focused and empty — helper hint visible
- [ ] Submit button is disabled when input is empty
- [ ] Tag filter dropdown has a visible label for screen readers

---

## Group L — Mobile / Responsive

- [ ] At 650px viewport width — feed entry dates appear inline (not overlapping or in wrong margin)
- [ ] At 320px viewport width — breadcrumb current page truncates gracefully without cutting off at a very short width

---

## Standalone — 404 Page

- [ ] Visit a non-existent URL — 404 page renders correctly with no visual artifacts from `.private-note` styles

---

## Standalone — Private Page

- [ ] Visit a private (unpublished) note URL as a regular visitor — message is visitor-appropriate, no vault frontmatter instructions visible

---

## Group J — Reading Experience *(implement before checking)*

- [ ] On a long post, a "Back to top" button appears after scrolling ~400px and smoothly scrolls to top on click
- [ ] Post prev/next nav shows "Previous post" / "Next post" directional labels above the title
- [ ] Reading progress bar appears on long posts, tracks scroll position, respects theme color

---

## General Regression Checks

Run these regardless of which group was just implemented:

- [ ] Homepage loads without errors
- [ ] A listing page with pagination renders correctly
- [ ] A feed page renders correctly
- [ ] A post with a banner image renders correctly
- [ ] A post without a banner renders correctly
- [ ] TOC block opens and closes
- [ ] Code block copy button works ("copy" → "copied")
- [ ] Theme toggle cycles: Auto → Light → Dark → Auto
- [ ] Language toggle (if multilingual site) switches language and persists across pages
- [ ] Canvas page renders and pan/zoom works
- [ ] Giscus comment section loads on a post (if configured)
- [ ] RSS feed (`/feed.xml`) and sitemap (`/sitemap.xml`) load without errors
- [ ] Search returns results and highlights match text
- [ ] Tags page loads and tag links work
- [ ] Private note page (`?token=` flow) still works
