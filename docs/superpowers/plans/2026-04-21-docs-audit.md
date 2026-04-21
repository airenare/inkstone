# Documentation Audit & Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve documentation across BlogPages/, README.md, and antonbakulin.com so new users can get live fast, developers can understand the engine, and the reference docs are complete and accurate.

**Architecture:** Three independent areas of work — BlogPages (demo vault shipped with the engine), README.md (GitHub developer-facing), and antonbakulin.com Obsidian vault docs (user reference). Each area is self-contained and can be done in any order, though BlogPages tasks should be committed together. No engine code changes.

**Tech Stack:** Markdown, YAML frontmatter, Python/Flask OnyxFolio engine (for smoke-testing BlogPages changes)

---

## File Map

**Create:**
- `BlogPages/Start Here.md` — new root-level getting-started note

**Modify:**
- `BlogPages/Test Website.md` — add "New here?" callout + developer post link
- `BlogPages/blog/How This Blog Works.md` — update internal Post Dict table and Frontmatter Reference section; add framing sentence
- `README.md` — restructure features list, fix project structure, fix URLs, fix type: language, add multilingual frontmatter fields
- `/Users/anton/Library/Mobile Documents/iCloud~md~obsidian/Documents/AirVault/antonbakulin.com/onyxfolio/Features.md` — add Multilingual section
- `/Users/anton/Library/Mobile Documents/iCloud~md~obsidian/Documents/AirVault/antonbakulin.com/onyxfolio/Getting Started.md` — add missing frontmatter fields to quick reference
- `/Users/anton/Library/Mobile Documents/iCloud~md~obsidian/Documents/AirVault/antonbakulin.com/onyxfolio/docs/Frontmatter Reference.md` — add `language:` and `lang:` fields

**Note:** antonbakulin.com files live in the Obsidian vault at `/Users/anton/Library/Mobile Documents/iCloud~md~obsidian/Documents/AirVault/antonbakulin.com/onyxfolio/`. They are not part of the OnyxFolio git repo — do not try to commit them.

---

## Task 1: Create `BlogPages/Start Here.md`

**Files:**
- Create: `BlogPages/Start Here.md`

- [ ] **Step 1: Create the file with this exact content**

```markdown
---
website: true
title: Start Here
menu_order: 1
date: 2026-04-21
summary: "Get OnyxFolio running and your first note live — three paths to choose from."
---

# Start Here

Get your Obsidian vault live on the web. Pick one path below.

---

## Option A — Run locally

**Requirements:** Python 3.11+, Git

```bash
git clone https://github.com/airenare/onyxfolio
cd onyxfolio
pip install -r requirements.txt
python3 app.py
# → http://127.0.0.1:8000
```

To serve your own vault instead of this demo:

```bash
echo "VAULT_PATH=/path/to/your/obsidian/vault" > .env
python3 app.py
```

The server watches your files and reloads automatically — no restart needed.

---

## Option B — Docker

```bash
git clone https://github.com/airenare/onyxfolio
cd onyxfolio
docker build -t onyxfolio .
docker run -p 8000:8000 -v /path/to/your/vault:/vault onyxfolio
# → http://127.0.0.1:8000
```

If no `/vault` is mounted, the bundled demo vault loads instead.

---

## Option C — Deploy with Coolify

For a production site that updates automatically when you push your vault to GitHub:

→ See the [Deployment guide](https://antonbakulin.com/onyxfolio/deployment) for step-by-step instructions.

---

## Your first published note

Add `website: true` to any note's frontmatter:

```yaml
---
website: true
title: My First Post
date: 2026-01-15
---

Write whatever you want here.
```

That note is now live. Its URL is `/my-first-post` if it's in the vault root, or `/section/my-first-post` if it's in a subfolder.

---

## Vault structure basics

| Vault path | URL |
|---|---|
| `Home.md` (with `type: homepage`) | `/` |
| `blog/Blog.md` (with `type: listing`) | `/blog` |
| `blog/My Post.md` | `/blog/my-post` |
| `About.md` | `/about` |

---

## Next steps

Full configuration reference — theming, Dataview, multilingual, deployment, and more:

→ [antonbakulin.com/onyxfolio](https://antonbakulin.com/onyxfolio)
```

- [ ] **Step 2: Start the server and verify**

```bash
conda activate conda312
python3 app.py
```

Open http://127.0.0.1:8000 — confirm "Start Here" appears as the first nav link. Click it and confirm the page renders with all three options and the correct code blocks.

- [ ] **Step 3: Stop the server (Ctrl+C)**

---

## Task 2: Verify BlogPages demo post frontmatter

**Files:**
- Read only (no edits expected)

All demo posts are expected to already use `website: true`. This step confirms that before proceeding so there are no surprises.

- [ ] **Step 1: Check each BlogPages post for old publish mechanism**

```bash
grep -rL "website: true" BlogPages/ --include="*.md"
```

Expected output: only files that are intentionally private (e.g. `books/Project Hail Mary.md`, `templates/web page template.md`, `_UI Translations_RU.md`, language variants that already have `website: true` at the right level). If any content post is missing `website: true`, add it before continuing.

- [ ] **Step 2: If any content posts are missing `website: true`, add it**

For each file flagged that is a real content post (not a private/template/translation note), open the file and add `website: true` as the first line of the frontmatter block.

---

## Task 3: Update `BlogPages/Test Website.md`

**Files:**
- Modify: `BlogPages/Test Website.md`

- [ ] **Step 1: Read the current file**

Run: `head -30 "BlogPages/Test Website.md"`

- [ ] **Step 2: Add the "New here?" callout and developer link**

After the opening `# OnyxFolio` heading and the first paragraph ("A lightweight blog engine..."), and before the `---` divider that leads into "What it does", insert:

```markdown
> [!tip] New here?
> See [[Start Here]] to get your own vault live in minutes.
```

And at the bottom of the page, after the "Standalone pages" section and before the existing `> [!note] This is the demo vault` callout, add:

```markdown
## Under the hood

Curious how the engine works? [[How This Blog Works|From Vault to Web: How This Blog Works]] is a full technical walkthrough — two-pass loading, the markdown pipeline, routing, hot-reload, and Dataview.

---
```

- [ ] **Step 3: Start the server and verify**

```bash
conda activate conda312
python3 app.py
```

Open http://127.0.0.1:8000 — confirm the tip callout renders near the top, the wiki-link to `[[Start Here]]` resolves correctly, and the "Under the hood" section with the developer post link appears before the demo vault note at the bottom.

- [ ] **Step 4: Stop the server (Ctrl+C)**

- [ ] **Step 5: Commit Tasks 1 and 2 together**

```bash
git add "BlogPages/Start Here.md" "BlogPages/Test Website.md"
git commit -m "docs: add Start Here getting-started note; link from demo homepage"
```

---

## Task 4: Update `BlogPages/blog/How This Blog Works.md`

**Files:**
- Modify: `BlogPages/blog/How This Blog Works.md`

This post has two outdated sections: (1) the "Post Dict" table uses `labels` (old field name) instead of `tags`, and describes `featured` incorrectly; (2) the "Frontmatter Reference" section at the bottom documents the old `tags: [blog, homepage, listing]` publish mechanism and `labels:` content tags — both replaced years ago.

- [ ] **Step 1: Add framing sentence at the top**

After the opening paragraph ("Every page you read here was written as a plain `.md` file in Obsidian...") and before the `> [!abstract] What This Covers` callout, add one sentence:

```markdown
This is the developer deep-dive — if you want to get your own vault live first, start with [[Start Here]].
```

- [ ] **Step 2: Update the Post Dict table**

Find the "The Post Dict" section (around line 375). Replace:

```markdown
| `labels` | Sorted, lowercased list from frontmatter `labels:` |
| `featured` | `True` if `featured` tag is present |
```

With:

```markdown
| `tags` | Sorted, lowercased list from frontmatter `tags:` and inline `#hashtags` |
| `featured` | `True` if `featured: true` is set in frontmatter |
```

- [ ] **Step 3: Replace the Frontmatter Reference section**

Find the "## Frontmatter Reference" section (starts around line 398). Replace everything from `## Frontmatter Reference` through the closing `> [!warning] Colons in frontmatter values` callout block (ends around line 437) with the content below. (The outer fence uses `~~~~` to avoid conflict with the inner yaml fence.)

~~~~markdown
## Frontmatter Reference

```yaml
---
website: true        # required to publish as a web page
type: homepage       # optional: homepage | listing | book
                     #   homepage  — renders this note's content at the section root
                     #   listing   — auto-generates a post index at the section root
                     #   book      — uses the book template with cover/metadata header
featured: true       # optional; highlight in the section's featured area
priority: 0          # featured posts only; lower = higher rank; date breaks ties
date: 2026-01-20
title: My Post
slug: my-post        # optional; auto-generated from title if omitted
summary: "..."       # listing card text; auto-derived if omitted
banner: "https://..."
banner_x: 0.5        # horizontal focal point (0 = left, 1 = right)
banner_y: 0.4        # vertical focal point (0 = top, 1 = bottom)
menu_order: 1        # pin to top nav; lower = further left
show_search: true    # root homepage only: adds Search link to nav
show_tags: true      # root homepage only: adds Tags link to nav
language: en         # root homepage only: sets the default site language
lang: ru             # per-note: marks this note as a specific language variant
tags:
  - python
  - obsidian
---
```

> [!warning] Colons in frontmatter values
> YAML uses `: ` (colon + space) as a key-value separator. If your `title`, `summary`, or any other string field contains a colon, you must wrap the entire value in double quotes — otherwise the YAML parser silently turns it into a nested dict and the post's URL, title, and wiki-links all break.
> ```yaml
> title: "From Vault to Web: How This Blog Works"   # correct — quotes are YAML syntax, stripped from value
> title: From Vault to Web: How This Blog Works      # broken
> ```
> The engine will log a warning to stderr and fall back to the H1 heading or filename when it detects this, so the post still loads — but the title will be wrong until you add the quotes.
>
> **Intentional quotes in a title:** YAML double-quote wrappers are always stripped by the parser — they never appear in the rendered title. To include literal `"` characters in a title (e.g. `"Hello World" Considered Harmful`), wrap the whole value in single quotes instead:
> ```yaml
> title: '"Hello World" Considered Harmful'   # renders as → "Hello World" Considered Harmful
> title: "No quotes here: just a colon"       # renders as → No quotes here: just a colon
> ```
~~~~

- [ ] **Step 4: Start the server and verify**

```bash
conda activate conda312
python3 app.py
```

Open http://127.0.0.1:8000/blog/how-this-blog-works — confirm:
- The framing sentence appears near the top with a working link to `/start-here`
- The Post Dict table shows `tags` (not `labels`)
- The Frontmatter Reference section shows `website: true` syntax (not old `tags: [blog, homepage, listing]`)

- [ ] **Step 5: Commit**

```bash
git add "BlogPages/blog/How This Blog Works.md"
git commit -m "docs: update How This Blog Works — fix post dict, frontmatter reference to current syntax"
```

---

## Task 5: README — Restructure features list into categories

**Files:**
- Modify: `README.md`

The current flat list of ~45 bullets has no hierarchy. Replace it with grouped categories.

- [ ] **Step 1: Find the features section bounds**

The features section starts with `## Features` and ends just before `## Frontmatter reference`. Note the line numbers before editing.

- [ ] **Step 2: Replace the entire `## Features` section**

Replace everything from `## Features` up to (but not including) `## Frontmatter reference` with:

```markdown
## Features

### Obsidian-native syntax

- **Callouts** — `> [!tip]` boxes; all standard Obsidian types; collapsible (`> [!type]-`) or pinned open (`> [!type]+`); rendered as native `<details>`
- **Wiki-links** — `[[Note]]`, `[[Note|alias]]`, `[[Note#Heading]]`, `[[Note^block-id]]` — resolved across all vault sections even when filename, title, and slug differ
- **Image embeds** — `![[file.jpg]]` on its own line becomes a lightbox-enabled image; multiple on one line become a slider; `![[photo.jpg|Caption]]` renders a `<figcaption>`
- **Note transclusion** — `![[Note Title]]` or `![[Note Title#Heading]]` embeds another note (or just one section) inline
- **Audio embeds** — `![[file.mp3]]` → `<audio>` element; `.mp3`, `.ogg`, `.wav`, `.flac`, `.m4a` supported
- **Checkboxes** — `- [ ]` / `- [x]` → HTML checkbox lists with proper nesting
- **Highlights** — `==text==` → `<mark>` tags
- **Footnotes** — `[^1]` / `[^note]` syntax with backlinks
- **Block references** — `^block-id` on a paragraph creates an anchor target; `[[Note^id]]` links scroll to it
- **Aliases** — `aliases:` frontmatter registers alternate wiki-link names that resolve to the same post

### Math & diagrams

- **Mermaid** — fenced ` ```mermaid ``` ` blocks rendered client-side via Mermaid.js; adapts to dark and light theme automatically
- **LaTeX / KaTeX** — `$inline$` and `$$block$$`; expressions protected from the markdown parser before rendering

### Dataview

- **Table and list queries** — `TABLE` and `LIST` queries in fenced ` ```dataview ``` ` blocks executed server-side; supports `FROM`, `WHERE`, `SORT`, `LIMIT`, `GROUP BY` with per-group headings
- **Inline queries** — `` `= this.field` `` expressions in prose evaluated against the current note's frontmatter

### Publishing & structure

- **Private notes** — notes without `website: true` are invisible as web pages but fully queryable by Dataview; navigating to their URL shows a styled placeholder
- **Auto-listings** — folders with no explicit index file get an auto-generated listing page automatically
- **Banner images** — `banner: "url"` in frontmatter for a hero image; `banner_x`/`banner_y` control the focal point
- **Vault-wide attachments** — media resolution falls back to vault root `_attachments/`, then `ATTACHMENTS_PATH` from `.env`
- **Favicon** — default OnyxFolio favicon included; override by placing `favicon.ico`, `favicon.png`, or `favicon.svg` in your vault root
- **Author field** — `author:` frontmatter (string or list) shown below the post title and in JSON-LD
- **Date last modified** — `updated:` frontmatter shows "Updated …" in post meta and populates `dateModified` in JSON-LD
- **Site icon** — `icon: path/to/image` shows an image beside the site title; cascades to all child pages unless overridden
- **Custom header title** — `site_title: My Brand` changes the displayed title in the header; also cascades to child pages

### Navigation & discovery

- **Full-text search** — `/search` with tag filter; opt-in via `show_search: true` on the root homepage
- **Tags** — `tags:` frontmatter + inline `#hashtag` body mentions; clickable badges; `/tag/<name>` archive pages; `/tags` index opt-in via `show_tags: true`
- **Breadcrumb navigation** — `Home › Section › Post` trail; useful for nested paths like `/gallery/arts/post`
- **Nav pinning** — `menu_order: N` in any note's frontmatter pins it to the top nav; lower = further left
- **Related posts** — automatic "See also" section scored by shared tags and section; top four results
- **Next / previous navigation** — "← Older" / "Newer →" links at the bottom of each post, ordered by date within the same section
- **Pagination** — listing pages paginate at 20 posts per page
- **Reading time** — estimated reading time shown on post pages and listing cards

### SEO & feeds

- **RSS feed** — latest 20 posts at `/feed.xml`; per-section feeds at `/blog/feed.xml`, `/gallery/feed.xml`, etc.
- **Sitemap** — auto-generated from all published routes at `/sitemap.xml`
- **OpenGraph / Twitter Card** — per-page meta tags for rich link previews; uses banner image if set
- **JSON-LD structured data** — Article, Book, and WebSite schemas for rich Google results

### Developer experience

- **Hot-reload** — the server watches file modification times and reloads the vault on any change; no restart needed
- **Syntax highlighting** — fenced code blocks get language labels, a copy button, and Tokyo Night Dark theme via highlight.js
- **Dark / light mode** — toggle button in the header; preference persisted in `localStorage`
- **Inline body tags** — `#hashtag` mentions in the note body are collected as tags; merged with frontmatter `tags:`
- **Mobile nav** — nav links wrap below the site title on narrow viewports (≤ 600 px)
- **Print stylesheet** — `@media print` hides nav and interactive chrome, resets colours, appends link URLs inline
- **Custom 404** — styled 404 page consistent with the rest of the site
- **Docker-ready** — pass `VAULT_REPO` as a build arg to clone your private vault at deploy time

### Multilingual

- **Language routing** — add a two-letter suffix to any filename (`Post_RU.md` → `/post/ru`), or set `lang:` in frontmatter; language toggle in header; `hreflang` meta tags; auto-redirect for missing translations; "not yet translated" placeholder for content that exists only in a non-default language
- **UI string translations** — create a `type: translations` vault note with `lang:` and a `strings:` dict to translate fixed UI labels (Tags, Search, nav items) into any language without editing templates

---
```

- [ ] **Step 3: Verify the README renders correctly**

Open `README.md` in a Markdown viewer or GitHub preview. Confirm all 8 category headers appear and no bullets are orphaned or duplicated.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: restructure README features list into categories"
```

---

## Task 6: README — Fix project structure, URLs, type: language, frontmatter

**Files:**
- Modify: `README.md`

Four targeted fixes in one commit.

- [ ] **Step 1: Fix "How it works" section — `type:` language**

Find this text (in the "How it works" section, after the URL table):

```
A note tagged `homepage` serves its content at the section root (`/`, `/blog`, `/gallery`). A note tagged `listing` renders an auto-generated post index at the section root instead.
```

Replace with:

```
A note with `type: homepage` in its frontmatter serves its content at the section root (`/`, `/blog`, `/gallery`). A note with `type: listing` renders an auto-generated post index at the section root instead.
```

- [ ] **Step 2: Fix project structure section**

Find the `## Project structure` section with the code block. Replace the entire code block with:

```
app.py               Flask app, single catch-all route
config.py            Loads .env, VAULT_PATH, tag constants
obsidian_syntax.py   Obsidian-specific converters: wiki-links, callouts, embeds, math, block IDs
dataview.py          Server-side Dataview query engine
converters.py        Markdown pipeline coordinator; imports obsidian_syntax + dataview
posts.py             Two-pass vault loader, ALL_POSTS, SECTION_ROUTES, LANG_GROUPS
view_helpers.py      Pure view utilities: breadcrumbs, adjacent posts, related posts
frontend/
  templates/         base, index, post, listing, book, private, search, tag, 404
  static/            base.css, callouts-base.css, obsidian.css, omarchy.css, code.css
BlogPages/           Bundled demo vault (fallback when no VAULT_PATH set)
Dockerfile
```

Keep the line after: `The import chain is strictly one-way: \`config ← obsidian_syntax / dataview ← converters ← posts ← app\`.`

- [ ] **Step 3: Fix demo vault table**

Find the `## Demo vault` section. Replace the entire table with:

```markdown
| URL | Content |
|---|---|
| `/` | Engine homepage with feature overview |
| `/start-here` | Getting-started guide — three paths to go live |
| `/blog` | Blog listing with featured posts |
| `/blog/how-this-blog-works` | Architecture deep-dive: two-pass loading, markdown pipeline, routing |
| `/blog/writing-for-the-web` | Authoring workflow in Obsidian |
| `/blog/engine-features` | Showcase: related posts, Dataview, block references, dark/light mode |
| `/gallery` | Image gallery with lightbox and slider |
| `/books` | Dataview-powered bookshelf |
| `/books/project-hail-mary` | Example of a private note placeholder |
```

- [ ] **Step 4: Add multilingual fields to the frontmatter reference**

In the `## Frontmatter reference` code block, find the line:

```yaml
tags:                 # user content tags — shown as badges, used for /tag/<name> archive pages,
```

Add these two lines immediately before it (after the `site_title` line):

```yaml
language: en          # root homepage only: sets the default site language (e.g. "en", "ru", "fr")
lang: ru              # per-note: marks this note as a specific language variant; also set
                      #   automatically by filename suffix (_RU.md → ru, _FR.md → fr)
```

- [ ] **Step 5: Verify README**

Skim the README. Confirm: (a) "How it works" says `type: homepage` not "tagged `homepage`"; (b) project structure shows 7 modules; (c) demo vault table shows lowercase URLs and current posts; (d) frontmatter reference includes `language:` and `lang:`.

- [ ] **Step 6: Commit**

```bash
git add README.md
git commit -m "docs: fix README project structure, demo URLs, type: language, add multilingual frontmatter fields"
```

---

## Task 7: antonbakulin.com `Features.md` — add Multilingual section

**Files:**
- Modify: `/Users/anton/Library/Mobile Documents/iCloud~md~obsidian/Documents/AirVault/antonbakulin.com/onyxfolio/Features.md`

**Note:** This file is in the Obsidian vault, not the OnyxFolio repo. No git commit needed.

- [ ] **Step 1: Read the current file**

Read the file to confirm the last section ends at `[[Attachments|docs]]` under "Developer experience".

- [ ] **Step 2: Add Multilingual section at the bottom**

After the last line of the "Developer experience" section, append:

```markdown

---

## Multilingual

- **Language routing** — add a two-letter suffix to any filename (`Post_RU.md` → `/post/ru`), or set `lang:` in frontmatter; language toggle in header; `hreflang` meta tags for search engines — [[Multilingual|docs]]
- **Missing translation handling** — navigating to `/post/ru` when no RU version exists redirects to the default language; notes that exist only in a non-default language show a "not yet translated" placeholder — [[Multilingual|docs]]
- **UI string translations** — create a `type: translations` note (no `website: true` needed) with `lang:` and a `strings:` dict to translate fixed labels (Tags, Search, "min read", etc.) without editing templates — [[Multilingual|docs]]
```

- [ ] **Step 3: Verify**

Open the file in Obsidian or a Markdown viewer. Confirm the new section renders at the bottom with three bullets and working wiki-links.

---

## Task 8: antonbakulin.com `Getting Started.md` — add missing frontmatter fields

**Files:**
- Modify: `/Users/anton/Library/Mobile Documents/iCloud~md~obsidian/Documents/AirVault/antonbakulin.com/onyxfolio/Getting Started.md`

**Note:** This file is in the Obsidian vault. No git commit needed.

- [ ] **Step 1: Read the current frontmatter reference section**

The quick reference YAML block near the bottom currently ends with `aliases:` / `- alternate name`. Confirm by reading the file.

- [ ] **Step 2: Add missing fields to the YAML block**

In the frontmatter reference YAML block, after the line:

```yaml
updated: 2026-04-01   # shown as "Updated …" in post meta
```

Add:

```yaml
icon: _attachments/logo.png  # image beside the site title; cascades to child pages
site_title: "My Brand"       # replaces the website name in the header; cascades to child pages
language: en          # root homepage only: default site language ("en", "ru", "fr", etc.)
lang: ru              # per-note: marks this note as a language variant; also set by _RU.md suffix
```

- [ ] **Step 3: Verify**

Open the file and confirm the four new lines appear in the YAML block in the correct position.

---

## Task 9: antonbakulin.com `docs/Frontmatter Reference.md` — add multilingual fields

**Files:**
- Modify: `/Users/anton/Library/Mobile Documents/iCloud~md~obsidian/Documents/AirVault/antonbakulin.com/onyxfolio/docs/Frontmatter Reference.md`

**Note:** This file is in the Obsidian vault. No git commit needed.

The Frontmatter Reference doc is already comprehensive. It needs one addition: `language:` and `lang:` in the full reference YAML block, and a new "See also" link to Multilingual.

- [ ] **Step 1: Read the current file**

Confirm the "Root homepage only" comment section currently contains `show_search:` and `show_tags:`. Find the line:

```yaml
# ── Root homepage only ───────────────────────────────────────────
show_search: true      # Adds a Search link to the top nav.
show_tags: true        # Adds a Tags link to the top nav.
```

- [ ] **Step 2: Add multilingual fields to the reference block**

After the `show_tags:` line and before the `# Social links` comment, add:

```yaml

# ── Multilingual ─────────────────────────────────────────────────
language: en           # Root homepage only. Sets the default language for the site (e.g. "en", "ru").
lang: ru               # Per-note language code. Overrides filename suffix if both are present.
                       # Filename suffix _RU.md is equivalent to setting lang: ru in frontmatter.
```

- [ ] **Step 3: Add Multilingual to the "See also" section**

At the bottom of the file, find the `## See also` section. Add this line:

```markdown
- [[Multilingual]] — filename suffix routing, language toggle, UI string translations
```

- [ ] **Step 4: Verify**

Open the file and confirm: (a) the multilingual fields appear in the correct section of the YAML block; (b) the See also link to Multilingual is present.

---

## Task 10: Final commit and version bump

**Files:**
- Modify: `VERSION`

All BlogPages and README changes are documentation improvements. Bump the patch version.

- [ ] **Step 1: Check current version**

```bash
cat VERSION
```

Expected: `1.26.0`

- [ ] **Step 2: Bump patch version**

Edit `VERSION` to `1.26.1`.

- [ ] **Step 3: Commit and tag**

```bash
git add VERSION
git commit -m "chore: bump version to 1.26.1"
git tag v1.26.1
git push && git push origin v1.26.1
```

- [ ] **Step 4: Verify remote**

```bash
git log --oneline -5
```

Confirm all documentation commits appear and v1.26.1 tag is present.
