# OnyxFolio — Completed Work

---

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

- ✅ **Version in footer** — `built with OnyxFolio v{{ app_version }}`. (v1.21.2)

## v1.21.x — Branding

- Logo: hex gem SVG (Catppuccin Mocha, onyx facets + folio heart)
- Favicon: default OnyxFolio logo; vault-root override (`favicon.ico/png/svg`)
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
