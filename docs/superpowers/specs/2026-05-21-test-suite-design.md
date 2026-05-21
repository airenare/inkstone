# Test Suite Design — InkStone

**Date:** 2026-05-21
**Status:** Approved

## Goal

Add automated tests so rendering bugs (like the two fixed in v1.40.1–1.40.2) are caught before shipping. Tests run locally with `pytest` and automatically on every push via GitHub Actions.

## Scope

- Unit tests for `dataview.py` and `obsidian_syntax.py`
- Integration tests for Flask routes, feed, and sitemap
- A minimal dedicated test vault as fixture data
- GitHub Actions CI workflow

## Directory Structure

```
tests/
├── conftest.py                  # shared: app factory, VAULT_PATH fixture
├── fixtures/
│   └── vault/                   # minimal stable test vault
│       ├── Homepage.md          # type: homepage
│       ├── blog/
│       │   ├── Blog Index.md    # type: listing
│       │   ├── simple_post.md   # plain post with known frontmatter
│       │   └── dv_post.md       # post with dataview TABLE/LIST/inline queries
│       └── gallery/
│           └── Gallery Index.md # type: listing (second section)
├── unit/
│   ├── test_dataview.py
│   └── test_obsidian_syntax.py
└── integration/
    ├── test_routes.py
    └── test_feeds.py
```

New files at repo root:
- `requirements-dev.txt` — `pytest`, `pytest-cov`
- `.github/workflows/test.yml` — CI workflow

## Test Vault

The fixture vault contains the minimum content needed to exercise each test. It is never used as a demo vault and should not change unless tests require it.

**`Homepage.md`** — `website: true`, `type: homepage`, title "Test Site"
**`blog/Blog Index.md`** — `website: true`, `type: listing`
**`blog/simple_post.md`** — `website: true`, known title/date/summary/tags
**`blog/dv_post.md`** — `website: true`, contains a `dataview` LIST block and an `` `= this.title` `` inline expression
**`gallery/Gallery Index.md`** — `website: true`, `type: listing`

## Unit Tests

### `test_dataview.py`

All tests call dataview functions directly with inline data — no Flask, no I/O.

| Test | Covers |
|------|--------|
| `test_from_tag` | `FROM #tag` filters to tagged posts only |
| `test_from_folder_exact` | `FROM "blog"` filters to posts in `blog/` folder |
| `test_from_folder_vault_prefix` | `FROM "VaultName/blog"` resolves same as `FROM "blog"` |
| `test_from_folder_nested` | Posts in `blog/sub/` included when FROM targets `blog` |
| `test_where_condition` | `WHERE type != "listing"` excludes listing posts |
| `test_sort_limit` | SORT + LIMIT return correct subset in order |
| `test_inline_eval` | `` `= this.title` `` in prose → `<span class="dv-inline">Title</span>` |
| `test_inline_skips_code_block` | `` `= this.title` `` inside ` ``` ` block → literal, no span |
| `test_inline_skips_multi_backtick` | ` ``` `= this.title` ``` ` → untouched |

### `test_obsidian_syntax.py`

| Test | Covers |
|------|--------|
| `test_callout_renders` | `> [!note] Title` → `<div class="callout callout-note">` |
| `test_checkbox_unchecked` | `- [ ] item` → disabled unchecked input |
| `test_checkbox_checked` | `- [x] item` → disabled checked input |
| `test_highlight` | `==text==` → `<mark>text</mark>` |

## Integration Tests

The `client` fixture in `conftest.py` sets `VAULT_PATH` to the fixture vault, imports `app`, and yields `app.test_client()` scoped to the session.

### `test_routes.py`

| Test | Asserts |
|------|---------|
| `test_homepage_200` | `/` → 200 |
| `test_listing_200` | `/blog` → 200, contains link to simple post |
| `test_post_200` | `/blog/simple-post` → 200, contains expected title |
| `test_post_with_dataview` | `/blog/dv-post` → 200, contains `<div class="dataview">` |
| `test_404` | `/nonexistent` → 404 |
| `test_search_returns_results` | `/search?q=<known word>` → 200, contains a match |
| `test_search_empty` | `/search?q=zzznomatch` → 200, no results message |

### `test_feeds.py`

| Test | Asserts |
|------|---------|
| `test_feed_xml_200` | `/feed.xml` → 200, Content-Type contains `xml` |
| `test_feed_has_items` | Response body contains `<item>` |
| `test_sitemap_200` | `/sitemap.xml` → 200 |
| `test_sitemap_has_urls` | Response body contains `<url>` |

## CI

`.github/workflows/test.yml` runs on every push and pull request:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=. --cov-report=term-missing
```

Python 3.12 on CI (3.14 is used locally; 3.14 is not yet on GitHub Actions runners). The app is expected to be compatible with 3.12 — CI will surface any incompatibilities on the first run.

## What Is Not Covered

- Canvas rendering (`posts.py` Pass 4) — complex, lower ROI for initial suite
- Bases rendering — same reason
- Attachment serving — static file pass-through, minimal logic
- Private note token auth — can be added later

These can be added incrementally as the suite matures.
