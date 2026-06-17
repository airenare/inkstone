# InkStone — Completed Work

---

## v1.54.15–v1.54.30 — UX Sprint (`ux-improvements` branch)

- ✅ **[UX][i18n] Fix hardcoded pagination labels in listing pages** — `listing.html` pagination now uses `ui_strings` for "Previous" / "Next" so multilingual sites translate correctly. (v1.54.15)
- ✅ **[UX][i18n] Fix Giscus `data-lang` hardcoded to `"en"`** — `post.html` now injects `current_lang` into `data-lang` so comment widget language matches the page. (v1.54.15)
- ✅ **[UX][a11y] Skip-to-content link and main landmark** — visually hidden `<a href="#main-content">` added as first body element; `<main id="main-content">` added to `base.html`. (v1.54.16)
- ✅ **[UX][a11y] Global `:focus-visible` outlines** — accent-colored 2px outline on all interactive elements; suppressed for mouse clicks via `:focus:not(:focus-visible)`. (v1.54.16)
- ✅ **[UX][a11y] `<label>` for tag filter `<select>` on search page** — visually hidden label with `for="tag-filter"` added to `search.html`. (v1.54.16)
- ✅ **[UX][a11y] Semantic `<time datetime>` sweep** — all date occurrences across `feed.html`, `post.html`, `blog.html`, `book.html`, `listing.html`, `tag.html` now use `datetime="YYYY-MM-DD"`. (v1.54.17)
- ✅ **[UX][lightbox] Visible close button and prev/next arrows** — × button (top-right) and ‹ › arrows (only when gallery has >1 item) added to lightbox JS in `base.html`. (v1.54.18–19)
- ✅ **[UX][lightbox] Fix lightbox closing on image click** — `stopPropagation()` on inner click so only backdrop clicks close the overlay. (v1.54.18–19)
- ✅ **[UX][lightbox] Fix whole-page gallery bug** — gallery IDs changed from hardcoded `"gallery"` to incremental `g1`, `g2`, … per image group so lightbox navigation is scoped correctly. (v1.54.23)
- ✅ **[UX][search] Empty state tag suggestions** — no-results page shows top 8 tags as badges and a link to `/tags`; backend computes `top_tags` via `Counter.most_common(8)`. (v1.54.20)
- ✅ **[UX][search] Input hint and disabled submit** — hint text appears on focus when field is empty; submit button disabled until a character is typed. (v1.54.20)
- ✅ **[UX][mobile] Feed date breakpoint alignment** — feed separator `left: 0` reset at ≤ 700px so date and separator align correctly between 600–700px viewports. (v1.54.21)
- ✅ **[UX][mobile] Breadcrumb responsive truncation** — replaced hard `max-width: 240px` with `max-width: min(50vw, 280px)` on `.breadcrumb-current`. (v1.54.21)
- ✅ **[UX][mobile] Post-nav mobile layout fix** — removed `flex-direction: column` and redundant `::before`/`::after` pseudo-elements; prev/next now sit side-by-side on mobile. (v1.54.22)
- ✅ **[UX][template] Fix 404 page using `.private-note` CSS class** — 404 now uses `.error-page` / `.error-message`; new CSS block added; no bleed from private-note styles. (v1.54.25)
- ✅ **[UX][messaging] Private page visitor messaging** — `private.html` shows visitor-appropriate "not available" message; vault frontmatter hint gated on `is_owner` (master `ACCESS_TOKEN` session). (v1.54.25)
- ✅ **[UX][reading] Back to top button** — fixed bottom-right button appears after 400px scroll, smooth-scrolls to top; styled with card/border variables. (v1.54.26)
- ✅ **[UX][reading] Post-nav directional labels** — "← Previous post" / "Next post →" labels above each adjacent post title in `post.html`; translatable via `ui_strings`. (v1.54.26)
- ✅ **[UX][reading] Reading progress bar** — 3px accent-colored bar fixed at top of viewport, visible only on post pages (article element present), tracks scroll through article body. (v1.54.26)
- ✅ **[UX][tags] Case-insensitive alphabetical tag sort** — `/tags` route now sorts via `key=lambda x: x[0].lower()`; count badge made more prominent with border and higher-contrast text. (v1.54.28)
- ✅ **[UX][a11y] Slider keyboard navigation** — `tabindex="0"` on `.slider-gallery`; `ArrowLeft`/`ArrowRight` keydown handler calls `goToSlide()`. (v1.54.29)
- ✅ **[UX][theme] Theme toggle `title` tooltip** — button `title` attribute describes next state: "Switch to light" / "Switch to dark" / "Switch to auto". (v1.54.30)
- ✅ **[UX][canvas] Fading pan/zoom hint** — "drag to pan · scroll to zoom" pill injected into `.canvas-view` on init, fades out after 2s via CSS transition. (v1.54.30)
- ✅ **[UX][copy] Copy button checkmark flash** — copy button shows "✓ copied" with a brief opacity-dip animation on click, resets after 1.5s. (v1.54.30)

## v1.40.0

- ✅ **[Design][Branding] Logo polish pass** — refined logo concept for geometry balance, contrast, and small-size legibility; shipped final web SVG plus favicon-ready variants. (v1.40.0)
- ✅ **[Canvas UX] Upgrade canvas toward jsoncanvas-level experience** — canvas rendering moved closer to jsoncanvas.org capabilities with wide mode, curvier edges, pan/zoom, markdown nodes, directed edges, file card previews, and site-matched styling. (v1.40.0)

## v1.39.0

- ✅ **P0: OnyxFolio → InkStone rename cleanup** — created new `inkstone` Pinecone index (namespace `codebase`), migrated all codebase records from `onyxfolio`; removed stale OnyxFolio paths from `.claude/settings.local.json`; created session memory files. Demo canvas already had correct name from prior commit. (v1.39.0)
- ✅ **Canvas wide mode** — added ⛶ button (`canvas-wide-btn`) that toggles `.canvas-wide` CSS class on the viewport, expanding the canvas to `position: fixed; inset: 16px` (near full window); Esc closes it; button icon toggles between ⛶ and ×; `fitToView()` re-runs after toggle. (v1.39.0)
- ✅ **Canvas curvier edges** — raised `_CTRL_MIN` from 50 → 100 and bezier offset multiplier from 0.45 → 0.55, giving more pronounced S-curves especially on closely-spaced nodes. (v1.39.0)

## v1.38.0

- ✅ **Canvas UX upgrade — pan/zoom, markdown, edge direction, polish** — interactive pan/zoom via vanilla JS `initCanvas()`, full `render_markdown()` pipeline for text nodes (`skip_strip_h1=True`), `fromEnd`/`toEnd` edge directionality per jsoncanvas spec, px-based node layout with `.canvas-stage` wrapper, fit-to-view button, link node domain/icon, group color tint. (v1.38.0)

## v1.37.1

- ✅ **Remove Mermaid `fixSvgBg()` workaround** — switched both dark and light modes to `theme: "base"` (Mermaid v11), which fully honours `themeVariables.background: "transparent"`. Dark mode now uses a full set of `base`-theme variables matched to the site's Catppuccin palette (`primaryColor`, `lineColor`, `noteBkgColor`, sequence diagram variables, etc.). The `fixSvgBg()` DOM post-processing function and its call are removed; CSS `rect.background { fill: transparent !important }` remains as a passive safety net. (v1.37.1)

## v1.37.0

- ✅ **Obsidian Bases: view filters + filename publish/feature markers** — `.base` filters now understand Obsidian-style `file.tags.contains("...")` in addition to existing expressions, so table views can use in-app filter trees directly from `views[].filters`. Publishing/featuring no longer depends on editing YAML in Obsidian: `Title__website.base` publishes, `Title__website__featured.base` publishes and features (case-insensitive suffix parsing, any order), with legacy `website:` / `featured:` still supported. Demo base fixture renamed to `blog/All Posts__website__featured.base`. (v1.37.0)

## v1.36.1

- ✅ **Canvas file cards: vault media + prefixed attachment URLs** — File nodes that reference an image/audio/video path under `VAULT_PATH` (e.g. `inkstone/docs/_attachments/media-demo-3.jpg`) now render that media in the card even when there is no matching `.md` post. New `vault_attachment_href()` / `URL_PATH_PREFIX` (`APPLICATION_ROOT`) in `config.py` so all `![]` / `![[…]]` media, canvas embeds, and relative header icons use `{prefix}/attachments/…` when the app is mounted below the domain root (fixes broken images on prefixed deployments). `canvas.py` uses `config.VAULT_PATH` at resolve time. (v1.36.1)

## v1.36.0

- ✅ **Canvas UX — directed edges + file card previews** — SVG edges use `marker-end` arrowheads (per stroke color). File nodes that resolve to a published post render a scrollable in-card body preview (`post_html_by_url` / titles from `posts.py` Pass 4); images, video, audio, and code blocks constrained via `.canvas-file-preview` in `base.css`. Demo canvas adds a sample file card linking `Engine Features.md`. (v1.36.0)

## v1.35.5

- ✅ **Canvas publish via filename (`__website`)** — Obsidian strips custom JSON keys when saving `.canvas` files. Publishing now uses durable filename marker `Title__website.canvas` (case-insensitive suffix): display title is the stem before `__website`; slug from title or optional JSON `slug`. Legacy `"website": true` in JSON still works. `canvas_filename_publish_meta()` in `canvas.py`; Pass 1 logic in `posts.py`. Demo vault file renamed to `blog/My Writing Process__website.canvas`. (v1.35.5)

## v1.35.2

- ✅ **[Bug] See also: fix sibling exclusion for translated-title variants** — v1.35.1's `base_url_path` comparison broke when translated posts have different titles (e.g. "About" → "Обо мне" → slug `obo-mne`). Fix: store `base_stem` (lowercased filename stem with `_XX` stripped) in every post dict; `get_related()` now compares `(section, base_stem)` pairs to identify siblings regardless of translated slugs. (v1.35.2)

## v1.35.1

- ✅ **[Bug] See also excludes language siblings** — `get_related()` now computes `post_base = post.get("base_url_path") or post["url_path"]` and skips any candidate whose `base_url_path` matches, so translations of the same post never appear in See also. (v1.35.1)

## v1.35.0

- ✅ **Inline `dv.pages()` expressions — Stage 1** — `` `= dv.pages("#tag").length` `` and `` `= dv.pages("").length` `` now evaluate server-side against the full vault index. `_filter_dv_pages()` filters by tag or returns all posts; `_eval_dv_pages_expr()` handles the pattern; `convert_dataview_inline()` gains an optional `dataview_index` kwarg and tries `dv.pages()` first. Stage 2 (field access, sorting, limiting) deferred. (v1.35.0)

## v1.32.0

- ✅ **Default theme frontmatter** — `default_theme: dark|light|system` in the root homepage frontmatter sets the initial theme for new visitors (before they interact with the toggle). "dark" and "light" force that theme; "system" (default) follows the OS `prefers-color-scheme`. Visitors can always override with the toggle; their choice is saved in `localStorage`. (v1.32.0)

## v1.31.0

- ✅ **Canvas file rendering** — `.canvas` files with `"website": true` in their JSON are published as read-only visual boards. Nodes (text, file, link, group) are absolutely positioned divs; edges are SVG bezier curves with optional labels. Minimal markdown in text nodes (bold, italic, inline code). File nodes link to published posts via `url_index`. Color-coded borders match Obsidian's 6 preset colors. New module `canvas.py`; Pass 4 in `posts.py`. Demo canvas at `/blog/my-writing-process`. (v1.31.0)

## v1.30.0

- ✅ **Inline image illustrations** — `![[image.jpg|inline]]` renders a plain centered `<figure>` without a lightbox; combine modifiers: `|inline 300` for max-width, `|inline Caption` for figcaption, `|inline 300 Caption` for both. Also fixes a silent bug where text captions (`|Caption text`) were dropped because the regex only matched numeric width hints. (v1.30.0)

## v1.29.0

- ✅ **System theme option** — third toggle state (⊙) follows `prefers-color-scheme`; cycle is System → Light → Dark → System. When System is active: `localStorage.theme` is removed, OS preference applied immediately, `change` event listener tracks further OS changes. (v1.29.0)

## v1.28.0

- ✅ **Private note access control — per-note tokens** — `access_token: secret` frontmatter unlocks a specific note via `?token=secret`; session stores a list of unlocked URL paths so subsequent visits work without the token. Global `ACCESS_TOKEN` env var acts as master key (unlocks all, stores boolean flag). Both can coexist. (v1.28.1)
- ✅ **Private note access control — foundation** — Pass 2b in `posts.py` pre-renders all private notes into `PRIVATE_RENDERED`; `post.html` served to unlocked guests; private placeholder shown otherwise. `SECRET_KEY` env var for Flask session signing. (v1.28.0)

## v1.27.x (continued)

- ✅ **Mermaid token leaking in nested fenced blocks** — `_extract_mermaid` rewritten line-by-line; skips mermaid blocks inside outer fenced blocks (e.g. ` ````markdown ```` ` doc examples), so the token never ends up stranded in a `<pre><code>` block. (v1.27.4)
- ✅ **Transliterated slugs** — `unidecode` applied in `slugify()` before slug generation; Cyrillic/Greek/etc. titles produce ASCII URLs. Manual `slug:` frontmatter bypasses this entirely. (v1.27.3)
- ✅ **Translations note body format** — strings moved from `strings:` frontmatter dict to a fenced ` ```yaml ` block in the note body; frontmatter now only needs `type: translations` + `lang:`. Legacy `strings:` dict still accepted as fallback. Updated demo vault, template, README, CLAUDE.md, How This Blog Works, Multilingual.md, Note Templates.md. (v1.27.2)
- ✅ **Obsidian template workflow** — QuickAdd (already bundled in demo vault) is the recommended approach; core Templates plugin is the simpler fallback. Cleaned up `templates/web page template.md` (removed clutter, added `summary` prompt). New doc page `Note Templates.md` in antonbakulin.com vault; added to Documentation index.

- ✅ **Lowercase URLs audit** — `_section_from_filepath` calls `slugify(p)` on every path segment (line 343); `slugify` lowercases + transliterates via unidecode, so mixed-case vault folders like `Blog/` produce `/blog` URLs. Confirmed; no code change needed.

## Audits & Docs

- ✅ **Capital letters in URLs audit** — grepped all `.md` files in repo and antonbakulin.com vault; all internal URLs already lowercase; only external OpenLibrary URLs use uppercase (required by their API). No changes needed.
- ✅ **Obsidian references audit** — reviewed all "Obsidian" mentions in both repos; all correctly refer to either the Obsidian app or Obsidian-specific syntax (callouts, wiki-links, embeds, Dataview). No generic "markdown" mislabelling found.

## v1.27.x

- ✅ **Obsidian Bases `.base` file support** — `.base` files with `website: true` parsed (YAML), filtered against vault, rendered as HTML tables. Supports `file.hasTag()`, `file.inFolder()`, property comparisons, `and`/`or`/`not`, `order`, `sort`, `limit`. New module `bases.py`; integrated in `posts.py` as pass 3. (v1.27.0)
- ✅ **Translations documentation** — full guide in `How This Blog Works`, README, CLAUDE.md, and `antonbakulin.com` vault docs. (v1.27.1)

## v1.26.x

- ✅ **Links not rendering in callouts** — added `markdown="1"` to outer and inner callout divs so Python-Markdown's `md_in_html` extension processes their content. (v1.26.2)
- ✅ **Footnotes broken** — fixed by `markdown="1"` + combined-regex code-span fix; `[^1]` now renders as superscript footnote reference. (v1.26.2)
- ✅ **Links failing mid-page** — `convert_links` incorrectly replaced patterns inside inline code spans; rewrote with combined regex that skips backtick spans. (v1.26.2)
- ✅ **`==highlights==` triple-backtick workaround** — `convert_highlights` now uses same combined regex. (v1.26.2)

## v1.25.x

- ✅ **Multilingual support** — filename suffix `_RU`/`_FR`/etc. → `/{slug}/{lang}` URLs; language toggle in header, hreflang meta, redirect for missing translations, "not yet translated" page. (v1.22.0)
- ✅ **UI string translations** — `type: translations` note with `lang:` + `strings:` dict overrides fixed template labels without editing HTML. (v1.22.0)

## v1.24.x

- ✅ **Social / `rel="me"` links** — per-platform frontmatter keys (`github:`, `mastodon:`, `bluesky:`, etc.) → SVG icon + `@handle` in footer with hover tooltip. (v1.24.0)

## v1.23.x

- ✅ **Comment system (Giscus)** — opt-in embed in `post.html` and `book.html`. Set `GISCUS_REPO`, `GISCUS_REPO_ID`, `GISCUS_CATEGORY_ID` env vars to enable. Theme sync via `postMessage`. (v1.23.0)
- ✅ **Footer attribution opt-out** — `HIDE_ATTRIBUTION` env var; footer attribution wrapped in conditional. (v1.23.0)
- ✅ **Fix media-embeds docs page** — real `![[...]]` examples with single image, caption, width, gallery, and slider. (v1.23.0)

## v1.22.x

- ✅ **Version in footer** — `built with InkStone v{{ app_version }}`. (v1.21.2)

## v1.21.x — Branding

- Logo: hex gem SVG (Catppuccin Mocha, onyx facets + folio heart)
- Favicon: default InkStone logo; vault-root override (`favicon.ico/png/svg`)
- `icon:` frontmatter: image beside site title (1.25em height); cascades to child pages
- `site_title:` frontmatter: overrides displayed website name; cascades to child pages

## v1.20.x — Mobile nav

- Hamburger removed; nav wraps below site title on narrow viewports
- Breadcrumbs fixed to single horizontal line on mobile
- Theme toggle pinned to top-right corner on mobile via flex order

## Architecture refactors

- `obsidian_syntax.py` — Obsidian-specific converters extracted from `converters.py`
- `dataview.py` — full Dataview query engine extracted from `converters.py`
- `bases.py` — Obsidian Bases renderer extracted as standalone module
- `view_helpers.py` — `build_breadcrumbs`, `get_adjacent_posts`, `get_related`, `highlight` extracted from `app.py`
- `_build_rss_xml()` — deduplicated RSS builder shared by global and section feed routes
- Related posts pre-computed at load time (`post_data["related"]`); O(1) per request
- `ALL_TAGS` cached at reload time; no per-request rebuild
- `parse_frontmatter` logs the failing filepath on YAML errors

## Features (earlier)

- Listing page "All Posts": card grid layout (matches "See also" style)
- Dataview LIST type — `LIST [field] FROM #tag`
- Dataview GROUP BY — heading per group + sub-table/sub-list
- Dataview WHERE operators: `=`, `!=`, `>`, `<`, `>=`, `<=`
- Dataview `LIMIT N` applied post-sort
- Dataview inline queries — `` `= this.field` ``
- Author field — `author:` frontmatter in post meta + JSON-LD
- `updated:` / `modified:` — "Updated …" in post meta + JSON-LD `dateModified`
- Next/prev within tag archive pages
- Next / previous post navigation (← Older / Newer →)
- Collapsible callouts (`> [!type]-` / `> [!type]+`)
- Visible image captions (`![[photo.jpg|Caption]]` → `<figcaption>`)
- `![[Note#Heading]]` partial transclusion
- Section RSS feeds (`/blog/feed.xml`, etc.)
- Tags index (`/tags`), tag archive pages (`/tag/<name>`)
- `og:image` on listing pages
- `book.html` breadcrumbs + "See also"
- Vault-wide attachments fallback chain
- Wiki-link lookup case-insensitive
- Image width hint (`![[img.png|200]]`)
- Auto-listing post dicts with safe defaults
- HTML-strip before code-block conversion (no bleed-through)
- Note transclusion fix (no false media matches)
- Mobile breadcrumbs: single-line, overflow hidden
- Search tag filter param renamed `label` → `tag`
- Print stylesheet
- Security: path traversal guard in media + transclusion
- Performance: `maybe_reload` 2s debounce

## Foundation

- README, RSS feed, OpenGraph/Twitter Card, custom 404, sitemap, canonical URLs
- `menu_order` nav pinning, breadcrumb navigation, reading time, pagination
- Search with tag filter and result highlighting, JSON-LD structured data
- Dark/light mode toggle, `==highlight==`, footnotes, Mermaid, KaTeX
- Note transclusion, audio embeds, `aliases`, block references
- Banner images, book template, private note placeholders
- Auto-generated section listings, label archive pages
- PolyForm Noncommercial 1.0.0 license
