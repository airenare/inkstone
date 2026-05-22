# InkStone Documentation Audit & Reorganization — Design Spec

## Goal

Improve documentation across three locations so that new users can get a site live quickly, developers can understand the engine internals, and the reference docs on antonbakulin.com are complete and up to date.

## Audience split

- **New users** (just cloned, want their vault live) — served by BlogPages/ getting-started content and README quick-start
- **Developers / contributors** (want to understand the engine) — served by BlogPages/ architecture post and README project structure
- **Existing users** (configuring features) — served by antonbakulin.com/inkstone reference docs

## Doc locations and responsibilities

| Location | Primary audience | Purpose |
|---|---|---|
| `BlogPages/` | New users + developers | First contact: get live fast + showcase features + architecture deep-dive |
| `README.md` | Developers evaluating or contributing | Project overview, quick-start, frontmatter reference, deployment |
| `antonbakulin.com/inkstone` | Existing users | Complete per-feature reference; links are the canonical answer for "how do I configure X" |

BlogPages links to antonbakulin.com for deep configuration details — it is not self-contained documentation.

---

## Area 1: BlogPages/

### New file: `Start Here.md`

Root-level, `menu_order: 1` (first nav item).

Content sections:
1. **Requirements** — Python 3.11+ or Docker
2. **Three paths to go live**
   - Localhost: git clone + pip install + `python3 app.py`
   - Docker: `docker run` one-liner
   - Coolify: vault repo + `VAULT_REPO` build arg (link to Deployment doc on antonbakulin.com)
3. **Point at your vault** — `VAULT_PATH=/path/to/vault` in `.env`; or edit notes in `BlogPages/` to try features first
4. **Your first published note** — minimum frontmatter (`website: true`, `title`, `date`)
5. **Next steps** — link to antonbakulin.com/inkstone for full configuration reference

Stays short: one page, no deep explanations.

### Update: `Test Website.md` homepage

Add a `[!tip]` callout near the top linking to `[[Start Here]]`:

```
> [!tip] New here?
> See [[Start Here]] to get your own vault live in minutes.
```

All existing showcase content stays unchanged.

### Update: `How This Blog Works.md`

Two changes:
1. Update frontmatter to use `website: true` and current keys (currently uses old `tags: [blog]` publish mechanism — confusing for users who copy it as a template)
2. Add a short framing sentence at the top positioning it as the developer/architecture reference

Add a link to this post from the homepage as "curious how it works under the hood?"

### Audit: all other demo posts

Check each `.md` in BlogPages/ for old `tags: [blog]` publish mechanism. Update any found to use `website: true` + proper frontmatter keys. This matters because new users copy-paste from demo posts.

---

## Area 2: GitHub README

Five targeted in-place fixes. No structural overhaul.

### 1. Restructure features list

Group ~70 flat bullets into categories matching antonbakulin.com/Features.md:
- Obsidian-native syntax
- Math & diagrams
- Dataview
- Publishing & structure
- Navigation & discovery
- SEO & feeds
- Developer experience
- Multilingual

No features added or removed — just organized. Each category gets a `###` header.

### 2. Fix project structure section

Add missing modules: `obsidian_syntax.py`, `dataview.py`, `view_helpers.py`. Update `converters.py` description (pipeline coordinator, not dataview engine).

### 3. Fix demo vault URLs

Table entries use old capitalized slugs (`/blog/Test-Post-One`). Update to lowercase (`/blog/test-post-one`).

### 4. Fix `type:` language

"A note tagged `homepage`" → "A note with `type: homepage`". Same for `listing`. One paragraph in "How it works."

### 5. Update frontmatter reference

Add multilingual fields: `language:` (root homepage default language), `lang:` (per-note language override), and a one-liner for `type: translations` notes. These shipped in v1.22–1.26 and are absent from the README.

---

## Area 3: antonbakulin.com/inkstone docs

Targeted additions only. No structural changes.

### 1. `Features.md` — add Multilingual category

New section at the bottom with two bullets:
- Filename suffix routing + language toggle + hreflang tags (`[[Multilingual|docs]]`)
- UI string translations via `type: translations` notes (`[[Multilingual|docs]]`)

### 2. `Getting Started.md` — update frontmatter quick reference

Add missing fields to the reference table:
- `language:` — root homepage default language
- `lang:` — per-note language override
- `site_title:` — custom header title (cascades to child pages)
- `icon:` — image beside site title (cascades to child pages)

### 3. `docs/Frontmatter Reference.md` — verify completeness

Read the file and confirm it includes all current fields including the new multilingual ones. Patch if any are missing.

---

## Out of scope

- Restructuring the antonbakulin.com docs hierarchy
- Writing new individual reference docs beyond what already exists
- Adding configuration content to BlogPages/ beyond `Start Here.md` (deep config stays on antonbakulin.com)
- Any engine code changes
