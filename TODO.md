# InkStone — Backlog

*Completed items live in [DONE.md](DONE.md).*

---

## UX — P0 (Bugs / Accessibility / i18n Regressions)

These are correctness issues, not polish. Fix before any feature work.

- [x] **[UX][i18n][Group D] Fix hardcoded "← Previous" / "Next →" in listing pagination** — `listing.html` lines 56–58 use raw strings instead of `ui_strings.get('Previous', 'Previous')` / `ui_strings.get('Next', 'Next')`, meaning paginated listing pages are never translated. Fix by replacing with `ui_strings` lookups, matching the pattern already used in `feed.html`. *(Implement together with Giscus lang fix — Group D.)*

- [x] **[UX][i18n][Group D] Fix Giscus comment widget hardcoded to `data-lang="en"`** — `post.html` line 113 always sends `data-lang="en"` to the Giscus iframe. On multilingual sites, comments appear in English even on non-English pages. Fix: inject `current_lang` from Flask context into the `data-lang` attribute so it matches the page language. *(Implement together with listing pagination fix — Group D.)*

- [x] **[UX][a11y][Group B] Add skip-to-content link at top of `<body>`** — Keyboard-only users must tab through the full header/nav on every page load before reaching the main content. Add a visually hidden `<a href="#main-content">Skip to content</a>` as the first element in `<body>`, and add `id="main-content"` to `<main>`. Style it to appear on focus only. *(Implement together with focus rings and form label — Group B.)*

- [x] **[UX][a11y][Group B] Add `:focus-visible` outlines to all interactive elements** — Nav links, tag badges, related-cards, social links, and buttons have hover styles but no visible focus outline. Keyboard users get no visual cue of their position. Add a consistent `:focus-visible` outline rule (e.g., `outline: 2px solid var(--accent); outline-offset: 2px;`) applied globally, then suppress it for mouse clicks via `:focus:not(:focus-visible)`. *(Implement together with skip-to-content and form label — Group B.)*

- [x] **[UX][a11y][Group B] Add `<label>` to the tag filter `<select>` on the search page** — The tag dropdown in `search.html` has no associated `<label>`, violating WCAG 2.1 SC 1.3.1. Screen readers announce it with no name. Add a visually hidden `<label for="tag-filter">Filter by tag</label>` and a matching `id` on the `<select>`. *(Implement together with skip-to-content and focus rings — Group B.)*

- [x] **[UX][a11y][Group M] Add `datetime` attribute to `<time>` elements in feed and feed embeds** — `feed.html` and `base.css`-rendered feed entries use `<time class="feed-entry-date">` with only localized display text and no `datetime="YYYY-MM-DD"` attribute. This makes the date unparseable by assistive technology and structured-data consumers. Fix: pass `post.date.strftime("%Y-%m-%d")` into a `datetime` attribute on every `<time>` element across `feed.html`, `post.html` (post-meta), and any note-embed templates.

- [ ] **[UX][template] Fix `404.html` using `.private-note` CSS class** — The 404 page wraps its content in `<article class="private-note">`, which is a copy-paste artifact from `private.html`. The private-note styles (badge, lock icon, max-width 560px) are not appropriate for a generic 404. Create a `.error-page` class (or reuse a neutral wrapper) and apply it in 404.html, keeping the styles separated.

---

## UX — P1 (Meaningful Improvements)

Noticeable friction for real visitors. Worth a focused sprint.

- [x] **[UX][lightbox][Group A] Add visible close button and prev/next arrows to lightbox** — Currently the only way to close the lightbox is clicking anywhere on the overlay, or pressing Escape. The only way to navigate is keyboard arrow keys. Mouse and touch users have no affordance. In `base.html`, add a `×` button (top-right corner) that calls `close()`, and ‹ / › arrow buttons that call `prev()` / `next()` — only rendered when `galleryItems.length > 1`. Style them with the existing rgba overlay aesthetic. *(Implement together with the click-target fix — Group A.)*

- [x] **[UX][lightbox][Group A] Fix lightbox closing when clicking the image** — The entire overlay element has a click listener that calls `close()`, so clicking the image itself dismisses the lightbox — counterintuitive when users want to inspect an image. Fix: call `e.stopPropagation()` on the `lightbox-inner` (or `lightbox-media`) click handler so only clicks on the dark backdrop close the overlay. *(Implement together with the close/nav buttons — Group A.)*

- [ ] **[UX][a11y][Group F] Add keyboard left/right arrow support to inline image sliders** — The `slider-gallery` JS in `base.html` has no keyboard handler. Sliders only respond to button clicks. Add a `keydown` listener on the focused slider (or on `document` when a slide is focused) for `ArrowLeft` / `ArrowRight` to call `goToSlide(index ± 1)`. Also make the slider itself focusable via `tabindex="0"` so keyboard users can reach it.

- [ ] **[UX][search][Group C] Show suggestions or related links on empty search results** — When a search yields no results, the page shows only "No results for X" and nothing else. Add a fallback section beneath the empty state: show the top 5–8 most-used tags as clickable badges ("Try browsing by tag: ..."), and a link to the Tags page. This gives visitors a clear next step instead of a dead end. *(Implement together with search form improvements — Group C.)*

- [ ] **[UX][search][Group C] Add character-count minimum hint and subtle loading state to search form** — The form requires full submission with no inline feedback. At minimum: (1) add a hint beneath the input like "Type at least 2 characters" that appears when the field is focused and empty, (2) disable the submit button when the field is empty. *(Implement together with empty state suggestions — Group C.)*

- [ ] **[UX][messaging] Rewrite `private.html` messaging for public visitors** — The private note page currently shows "How to publish this note" with vault frontmatter instructions. This is only useful to the vault owner but is shown to all visitors who reach a private URL. Rework: replace the expandable "How to publish" hint with a visitor-appropriate message (e.g., "This content is not publicly available. Contact the author if you believe you should have access."). Optionally keep the author hint but only if an `ACCESS_TOKEN` or `?token=` is present in the session, indicating it's likely the owner.

- [ ] **[UX][tags] Make the Tags page sort alphabetically with post counts visible** — The `/tags` page (`labels.html`) currently displays tags in whatever order they are iterated from the backend. Large tag sets become hard to scan. Fix in two parts: (1) in `app.py`, sort the `labels` list alphabetically (case-insensitive) before passing it to the template; (2) make the count bubble more visually prominent — currently it's a small dim badge. Consider also adding a "Sort by count" toggle for power users.

- [ ] **[UX][reading][Group J] Add a "Back to top" button for long posts** — There is no way to return to the top of a long article without scrolling manually, especially painful on mobile. Add a fixed-position button (bottom-right corner) that appears only after scrolling past ~400px, and smoothly scrolls to top on click. Style it consistently with the existing canvas control buttons (`var(--bg)`, `var(--border)`, `var(--text-muted)`). *(Can implement together with post-nav labels and optionally the reading progress bar — Group J.)*

- [ ] **[UX][reading][Group J] Add directional labels to post prev/next navigation** — The `post-nav` block shows only the adjacent post's full title with a ← or → arrow. For long titles this wraps awkwardly and the direction is easy to miss. Add a small label above each title: "← Previous" / "Next →" in `var(--text-dim)` at small font size, with the post title beneath it. This is a small template + CSS change in `post.html` and `base.css`. *(Implement together with Back to Top — Group J.)*

- [ ] **[UX][mobile] Fix feed page date overlap/gap between 600–700px viewport width** — The feed date floats into the left margin at `> 700px` but the body padding drops at `≤ 600px`. Between 600–700px the date reverts to inline but the body still has desktop margin, leaving a misaligned gap. Align the two breakpoints: either raise the body breakpoint to 700px, or lower the date breakpoint to 600px, whichever causes less cascade. *(Implement together with breadcrumb truncation fix — Group L.)*

- [ ] **[UX][mobile][Group L] Ease breadcrumb current-page truncation** — `.breadcrumb-current` has a hard `max-width: 240px` with `text-overflow: ellipsis`. On narrow screens (especially 320–400px) this can truncate very early in the title. Replace the fixed `max-width` with `max-width: 50vw` (or a `clamp`) so it scales proportionally to the viewport and doesn't clip aggressively on small devices. *(Implement together with feed date breakpoint fix — Group L.)*

---

## UX — P2 (Polish)

Nice-to-have, low friction to implement, good for overall quality.

- [ ] **[UX][theme] Add `title` tooltip to theme toggle button reflecting next state** — The theme-toggle button (🖥️/☀/☾) gives no hint of what clicking will do next. In the `update()` function in `base.html`, also set `btn.title` to describe the next state: when showing 🖥️ set `title="Switch to Light mode"`, when ☀ set `title="Switch to Dark mode"`, when ☾ set `title="Switch to Auto (system)"`. One-liner addition per state branch.

- [ ] **[UX][canvas] Add a fading interaction hint to canvas views** — First-time visitors see a static canvas with no indication it is interactive. Add a small, centered overlay label — "drag to pan · scroll to zoom" — that renders for ~2 seconds on load, then fades out via CSS opacity transition. Inject it inside `.canvas-view` in the `initCanvas()` JS function, positioned absolutely with `pointer-events: none` so it doesn't block interaction.

- [ ] **[UX][reading][Group J] Add a thin reading progress bar to long posts** — A 2–4px bar pinned to the top of the viewport (below the fixed header) that fills as the user scrolls through the article. Implement via a `scroll` event listener in `post.html`'s block or in `base.html` scoped to `body.post-page`. Show only when the post body is taller than 2× the viewport. Wire it to `var(--accent)` so it respects the current theme. *(Implement together with Back to Top and post-nav labels — Group J.)*

- [ ] **[UX][copy] Add a smooth transition to the copy button state change** — The copy button switches instantly between "copy" and "copied" with no visual feedback beyond the text change. Add a brief CSS opacity dip (`opacity: 0.6`) on click, restore immediately, and optionally swap "copy" for "✓ copied" with a checkmark. Purely a CSS + one-line JS change in `base.html`.

---

## P2 — Lower Priority

- [ ] **[Business][Domain] Register production domain** — secure `inkstone.dev` or a close alternative.
- [ ] **[Business][Hosting] Choose and set up production hosting** — evaluate and deploy in this order:
  1. **Fly.io** — Docker-native, fast path from repo root.
  2. **Render** — GitHub auto-deploy, easy setup.
  3. **Railway** — minimal config with `gunicorn`.
  4. **Hetzner VPS** — lowest recurring cost, manual infra.
  5. **DigitalOcean App Platform** — managed deployment from GitHub.
