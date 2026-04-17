# OnyxFolio — Backlog

---

## Immediate  *(small, pick up and finish in one session)*

- **Version in footer** — `base.html` footer currently reads "built with OnyxFolio" with no version.
  Change to `built with OnyxFolio v{{ app_version }}`. One-line template edit.

- **Footer attribution opt-out** — some users will want to remove the attribution.
  Read a `HIDE_ATTRIBUTION` env var in `config.py`; pass as `hide_attribution` to the context
  processor; wrap the footer `<span>` in `{% if not hide_attribution %}`. Default: attribution shown.

- **Fix media-embeds docs page** — `/onyxfolio/docs/media-embeds` uses placeholder text instead of
  real images. Replace with actual `![[...]]` embeds from `_attachments/` so the page demonstrates
  what it documents.

---

## Upcoming  *(defined features, ready to implement)*

- **Social / `rel="me"` links** — useful for Mastodon verification and portfolio sites.
  Add optional `social_links:` list to the root homepage frontmatter (or `.env` / `SOCIAL_LINKS`):
  ```yaml
  social_links:
    - label: Mastodon
      url: https://mastodon.social/@you
    - label: GitHub
      url: https://github.com/you
  ```
  Render as `<a rel="me" href="...">` in the footer. Pass list through context processor (similar to
  `menu_posts`). No `rel="me"` on links that don't point to social profiles — keep it opt-in per link.

- **Comment system (Giscus)** — opt-in Giscus embed at the bottom of `post.html` and `book.html`.
  Three env vars needed: `GISCUS_REPO`, `GISCUS_REPO_ID`, `GISCUS_CATEGORY_ID`.
  When all three are set, inject the `<script>` block and pass a `giscus_config` dict to the template.
  Giscus automatically adapts to dark/light via `data-theme`; wire it to the existing theme toggle JS.

- **Inline Dataview `dv.pages()` expression** — extend `convert_dataview_inline` in `dataview.py`
  beyond `this.*` to handle `` `= dv.pages("#tag").length` `` and similar cross-note expressions.
  The pattern is: detect `dv.pages(selector)` in the expression, run a filtered count/list against
  `DATAVIEW_INDEX`, return the result. Start with `.length` and `FROM #tag`; keep scope narrow.

---

## Polish & Bugs

- **Mermaid inner background** — Mermaid v11 injects an inline `style="background: ..."` on the
  SVG element that overwrites the transparent background. The current `fixSvgBg()` post-render strip
  in `base.html` is a workaround. Investigate the correct Mermaid v11 initialisation API:
  `mermaid.initialize({ htmlLabels: false, ... })` or `suppressErrorRendering`. Goal: remove the
  JS workaround and let Mermaid initialise cleanly.

- **Lowercase URLs audit** — slugify already lowercases; verify that vault folders with mixed-case
  names (e.g. `Blog/`, `Gallery/`) produce lowercase section URLs in practice. If not, apply
  `.lower()` to each path segment in `_section_from_filepath`. Mark done once confirmed.

---

## Ideas  *(not committed — explore when the time is right)*

- **Canvas file rendering** — Obsidian `.canvas` files are JSON graphs of nodes and edges.
  Render as a read-only visual board: parse the JSON, position `<div>`s or draw SVG to mirror
  the layout. Useful for publishing mind-maps and project boards. Effort: high; reward: unique.

- **`dv.pages()` full expression support** — after the `.length` case above, consider supporting
  richer expressions: field access (`dv.pages("#tag").file.name`), sorting, limiting. Makes inline
  Dataview genuinely powerful. Keep it server-side; no client JS needed.

- **Private note access control** — currently private notes show a "not published" placeholder.
  An opt-in password/token gate (HTTP Basic or a query-param token) would let authors share
  drafts without publishing them. Niche use case, worth noting.

---

## Business / External

- **Domain** — register `onyxfolio.com`, `.dev`, or `.app`

- **Hosting** — try in order of simplicity:
  1. **Fly.io** — Docker-native, `fly deploy` from repo root, free tier
  2. **Render** — GitHub auto-deploy, free tier (spin-down on idle)
  3. **Railway** — minimal config, generous free tier, `gunicorn` start command
  4. **Hetzner VPS** — €4/mo, persistent, gunicorn + nginx reverse proxy
  5. **DigitalOcean App Platform** — auto-deploy from GitHub like Render

---

## Done

**v1.21.0 — Branding**
- Logo: hex gem SVG (Catppuccin Mocha, onyx facets + folio heart)
- Favicon: default OnyxFolio logo; vault-root override (`favicon.ico/png/svg`)
- `icon:` frontmatter: image beside site title (1.25em height); cascades to child pages
- `site_title:` frontmatter: overrides displayed website name; cascades to child pages

**v1.20.x — Mobile nav**
- Hamburger removed; nav wraps below site title on narrow viewports
- Breadcrumbs fixed to single horizontal line on mobile
- Theme toggle pinned to top-right corner on mobile via flex order

**Architecture refactors** *(all shipped, codebase reflects this)*
- `obsidian_syntax.py` — Obsidian-specific converters extracted from `converters.py`
- `dataview.py` — full Dataview query engine extracted from `converters.py`
- `view_helpers.py` — `build_breadcrumbs`, `get_adjacent_posts`, `get_related`, `highlight` extracted from `app.py`
- `_build_rss_xml()` — deduplicated RSS builder shared by global and section feed routes
- Related posts pre-computed at load time (`post_data["related"]`); O(1) per request
- `ALL_TAGS` cached at reload time; no per-request rebuild
- `parse_frontmatter` logs the failing filepath on YAML errors

**Features**
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

**Foundation**
- README, RSS feed, OpenGraph/Twitter Card, custom 404, sitemap, canonical URLs
- `menu_order` nav pinning, breadcrumb navigation, reading time, pagination
- Search with tag filter and result highlighting, JSON-LD structured data
- Dark/light mode toggle, `==highlight==`, footnotes, Mermaid, KaTeX
- Note transclusion, audio embeds, `aliases`, block references
- Banner images, book template, private note placeholders
- Auto-generated section listings, label archive pages
- PolyForm Noncommercial 1.0.0 license
