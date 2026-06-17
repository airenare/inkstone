# UX Improvements — Execution Order

Branch: `ux-improvements`
Tracked in: `TODO.md` (UX sections)

---

## Group D — i18n Bug Fixes
**Files:** `listing.html`, `post.html`
**Why first:** Two one-liner template fixes correcting actual regressions. Fastest P0 wins.
- [x] Fix hardcoded "← Previous" / "Next →" in listing pagination
- [x] Fix Giscus `data-lang` hardcoded to `"en"`

## Group B — Accessibility Baseline
**Files:** `base.html`, `base.css`
**Why second:** Three items in two files. The focus-visible rule alone fixes every interactive element site-wide — highest return on effort.
- [x] Skip-to-content link
- [x] `:focus-visible` outlines on all interactive elements
- [x] `<label>` for tag filter `<select>` on search page

## Group M — Semantic `<time>` Markup
**Files:** `feed.html`, `post.html`, and any note-embed templates
**Why third:** Mechanical sweep, no logic changes. Clears the last P0 item.
- [x] Add `datetime="YYYY-MM-DD"` attribute to all `<time>` elements

## Group A — Lightbox Polish
**Files:** `base.html` (JS)
**Why fourth:** Both items live in the same ~90-line JS function block. Natural to tackle together.
- [x] Add visible × close button and ‹ › navigation arrows
- [x] Fix lightbox closing when clicking the image itself

## Group C — Search UX
**Files:** `search.html`, `app.py`
**Why fifth:** Small backend change (top tags for empty-state suggestions) plus template work. `<select>` label is trivially added in the same pass.
- [x] Empty state: suggest top tags + link to Tags page
- [x] Input hint ("type at least 2 characters") + disable submit when empty
- [x] Add `<label>` to tag filter `<select>`

## Group L — Mobile / Responsive CSS
**Files:** `base.css`
**Why sixth:** Two pure CSS tweaks. Quick and a good context-switch between heavier JS work.
- [x] Align feed date breakpoint with body padding breakpoint (600–700px gap)
- [x] Replace hard `max-width: 240px` on breadcrumb with `clamp`/`50vw`

## Standalone — 404 Template Fix
**Files:** `404.html`, `base.css`
**Why here:** One-liner class rename. Drop in between any of the above.
- [x] Replace `.private-note` class with `.error-page` on 404 page

## Standalone — Private Page Messaging
**Files:** `private.html`
**Why here:** Requires judgment call on owner-detection. Worth its own focused moment.
- [x] Rewrite messaging for public visitors; keep author hint conditional

## Group J — Reading Experience
**Files:** `base.html` (JS), `base.css`, `post.html`
**Why ninth:** Largest JS/CSS batch. Tackle after P0/P1 fixes are solid.
- [x] Back to top button (appears after 400px scroll)
- [x] Directional labels on post prev/next nav
- [x] Thin reading progress bar (scoped to long posts)

## Tags Page Sort
**Files:** `app.py`, `labels.html`
**Why tenth:** Small backend sort + optional UI toggle. Better after nav/accessibility work is done.
- [x] Sort tags alphabetically (case-insensitive) in `app.py`
- [x] Make count badge more visually prominent

## Group F — Slider Keyboard Support
**Files:** `base.html` (JS)
- [x] `ArrowLeft`/`ArrowRight` keydown handler on focused slider
- [x] Add `tabindex="0"` to slider container

## Polish Sprint (G + H + K — batch into one commit)
**Files:** `base.html` (JS), `base.css`
**Why last:** Each is a ~5-minute change. One tidy "polish" commit at the end.
- [x] Theme toggle: set `title` attribute to describe next state (G)
- [x] Canvas view: fading "drag to pan · scroll to zoom" hint on load (H)
- [x] Copy button: opacity dip + "✓ copied" checkmark on state change (K)
