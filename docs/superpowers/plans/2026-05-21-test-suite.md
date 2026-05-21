# Test Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a pytest test suite (unit + integration) with GitHub Actions CI covering the dataview engine, obsidian syntax converters, and Flask routes.

**Architecture:** Unit tests import dataview/obsidian_syntax functions directly and build minimal inline fixtures — no Flask, no disk I/O. Integration tests use Flask's test client pointed at a dedicated fixture vault in `tests/fixtures/vault/`. A top-level `conftest.py` wires the vault path before any app import.

**Tech Stack:** pytest, pytest-cov, Flask test client, GitHub Actions

---

## File Map

| Action | Path | Purpose |
|--------|------|---------|
| Create | `requirements-dev.txt` | Dev dependencies: pytest, pytest-cov |
| Create | `pytest.ini` | Root path config so `import app` works from tests/ |
| Create | `tests/conftest.py` | Sets VAULT_PATH env var; provides session-scoped `client` fixture |
| Create | `tests/fixtures/vault/Homepage.md` | type: homepage for test vault |
| Create | `tests/fixtures/vault/blog/Blog Index.md` | type: listing |
| Create | `tests/fixtures/vault/blog/simple_post.md` | Known title/date/tags for route assertions |
| Create | `tests/fixtures/vault/blog/dv_post.md` | Dataview block + inline expr + code block guard |
| Create | `tests/fixtures/vault/gallery/Gallery Index.md` | Second section for nav/listing checks |
| Create | `tests/unit/test_dataview.py` | Unit tests for FROM/WHERE/SORT/inline/code-block guard |
| Create | `tests/unit/test_obsidian_syntax.py` | Unit tests for callouts, checkboxes, highlights |
| Create | `tests/integration/test_routes.py` | HTTP status + content assertions |
| Create | `tests/integration/test_feeds.py` | /feed.xml and /sitemap.xml assertions |
| Create | `.github/workflows/test.yml` | CI workflow |

---

## Task 1: Scaffolding

**Files:**
- Create: `requirements-dev.txt`
- Create: `pytest.ini`

- [ ] **Step 1: Create `requirements-dev.txt`**

```
pytest>=8.0
pytest-cov>=5.0
```

- [ ] **Step 2: Create `pytest.ini`**

```ini
[pytest]
testpaths = tests
pythonpath = .
```

`pythonpath = .` adds the repo root to `sys.path` so `import app`, `import dataview`, `import obsidian_syntax` all work from inside `tests/`.

- [ ] **Step 3: Install dev dependencies**

```bash
/home/air/venv/3.14/bin/pip install -r requirements-dev.txt
```

- [ ] **Step 4: Verify pytest discovers nothing yet (clean baseline)**

```bash
cd /home/air/Documents/GithubRepos/InkStone
/home/air/venv/3.14/bin/pytest --collect-only
```

Expected output: `no tests ran` or `0 tests collected`.

- [ ] **Step 5: Commit**

```bash
git add requirements-dev.txt pytest.ini
git commit -m "chore: add pytest scaffolding"
```

---

## Task 2: Test vault fixture files

**Files:**
- Create: `tests/fixtures/vault/Homepage.md`
- Create: `tests/fixtures/vault/blog/Blog Index.md`
- Create: `tests/fixtures/vault/blog/simple_post.md`
- Create: `tests/fixtures/vault/blog/dv_post.md`
- Create: `tests/fixtures/vault/gallery/Gallery Index.md`

- [ ] **Step 1: Create `tests/fixtures/vault/Homepage.md`**

```markdown
---
website: true
type: homepage
title: Test Site
---

Welcome to the test site.
```

- [ ] **Step 2: Create `tests/fixtures/vault/blog/Blog Index.md`**

```markdown
---
website: true
type: listing
title: Blog
---
```

- [ ] **Step 3: Create `tests/fixtures/vault/blog/simple_post.md`**

```markdown
---
website: true
title: Simple Post
date: 2026-01-15
summary: A simple test post about nothing.
tags:
  - test
  - python
---

This is a simple test post with **bold** text.
```

- [ ] **Step 4: Create `tests/fixtures/vault/blog/dv_post.md`**

Note the code block at the end — the `` `= this.title` `` inside it must NOT be evaluated.

````markdown
---
website: true
title: Dataview Post
date: 2026-01-20
---

The title of this note is `= this.title`.

```dataview
LIST
FROM "blog"
WHERE title != "Dataview Post"
```

Code block example that must not be evaluated:

```
`= this.title`
```
````

- [ ] **Step 5: Create `tests/fixtures/vault/gallery/Gallery Index.md`**

```markdown
---
website: true
type: listing
title: Gallery
---
```

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/
git commit -m "test: add fixture vault for integration tests"
```

---

## Task 3: `conftest.py` with Flask client fixture

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Create `tests/conftest.py`**

```python
import os
import pytest
from pathlib import Path

# Set VAULT_PATH before app.py (and config.py) are imported.
# conftest.py is loaded by pytest before any test file, so this
# assignment runs first.
FIXTURE_VAULT = str(Path(__file__).parent / "fixtures" / "vault")
os.environ["VAULT_PATH"] = FIXTURE_VAULT


@pytest.fixture(scope="session")
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
```

- [ ] **Step 2: Verify conftest loads without error**

```bash
/home/air/venv/3.14/bin/pytest --collect-only
```

Expected: no import errors, 0 tests collected.

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "test: add session-scoped Flask client fixture"
```

---

## Task 4: Unit tests — `_folder_matches` and `_filter_by_folder`

**Files:**
- Create: `tests/unit/test_dataview.py`

These three tests cover the folder-path FROM bug fixed in v1.40.1.

- [ ] **Step 1: Create `tests/unit/test_dataview.py` with a helper and the three folder tests**

```python
"""Unit tests for dataview.py — FROM/WHERE/SORT/inline/code-block guard."""
from dataview import (
    _folder_matches,
    _filter_by_folder,
    _parse_dv_query,
    _execute_dv_query,
    convert_dataview_inline,
)


def _make_post(title, folder="", tags=None, metadata=None):
    """Build a minimal dataview_index entry."""
    filepath = f"/vault/{folder}/{title}.md" if folder else f"/vault/{title}.md"
    return {
        "filepath": filepath,
        "title": title,
        "metadata": metadata or {},
        "tags": tags or [],
        "section": folder,
        "url_path": ("/" + folder + "/" if folder else "/") + title.lower().replace(" ", "-"),
        "file": {
            "path": filepath,
            "name": title,
            "link": f'<a href="#">{title}</a>',
            "ctime": None,
            "folder": folder,
        },
    }


def _make_index(*posts):
    return {p["filepath"]: p for p in posts}


def test_folder_matches_exact():
    assert _folder_matches("blog", "blog") is True


def test_folder_matches_subfolder():
    assert _folder_matches("blog/sub", "blog") is True


def test_folder_matches_no_false_prefix():
    # "blogging" should NOT match FROM "blog"
    assert _folder_matches("blogging", "blog") is False


def test_from_folder_exact():
    index = _make_index(
        _make_post("Blog Post", folder="blog"),
        _make_post("Gallery Post", folder="gallery"),
    )
    parsed = _parse_dv_query('LIST\nFROM "blog"')
    result = _execute_dv_query(parsed, index)
    assert "Blog Post" in result
    assert "Gallery Post" not in result


def test_from_folder_vault_prefix():
    """FROM "VaultName/blog" must resolve the same as FROM "blog"."""
    index = _make_index(
        _make_post("Blog Post", folder="blog"),
        _make_post("Gallery Post", folder="gallery"),
    )
    parsed = _parse_dv_query('LIST\nFROM "MyVault/blog"')
    result = _execute_dv_query(parsed, index)
    assert "Blog Post" in result
    assert "Gallery Post" not in result


def test_from_folder_includes_nested():
    """Posts in blog/sub/ are included when FROM targets blog."""
    index = _make_index(
        _make_post("Sub Post", folder="blog/sub"),
        _make_post("Root Blog Post", folder="blog"),
        _make_post("Gallery Post", folder="gallery"),
    )
    parsed = _parse_dv_query('LIST\nFROM "blog"')
    result = _execute_dv_query(parsed, index)
    assert "Sub Post" in result
    assert "Root Blog Post" in result
    assert "Gallery Post" not in result
```

- [ ] **Step 2: Run the four tests**

```bash
/home/air/venv/3.14/bin/pytest tests/unit/test_dataview.py -v
```

Expected: 4 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_dataview.py
git commit -m "test: unit tests for FROM folder filtering"
```

---

## Task 5: Unit tests — WHERE, SORT, LIMIT

**Files:**
- Modify: `tests/unit/test_dataview.py` (append)

- [ ] **Step 1: Append three tests to `tests/unit/test_dataview.py`**

Add these after the existing tests:

```python
def test_from_tag():
    index = _make_index(
        _make_post("Python Post", folder="blog", tags=["python"]),
        _make_post("Other Post", folder="blog", tags=["ruby"]),
    )
    parsed = _parse_dv_query("LIST\nFROM #python")
    result = _execute_dv_query(parsed, index)
    assert "Python Post" in result
    assert "Other Post" not in result


def test_where_excludes_type():
    index = _make_index(
        _make_post("Listing", folder="blog", metadata={"type": "listing"}),
        _make_post("Post", folder="blog", metadata={"type": "post"}),
    )
    parsed = _parse_dv_query('LIST\nWHERE type != "listing"')
    result = _execute_dv_query(parsed, index)
    assert "Post" in result
    assert "Listing" not in result


def test_sort_and_limit():
    from datetime import date
    index = _make_index(
        _make_post("Alpha", folder="blog", metadata={"date": date(2026, 1, 1)}),
        _make_post("Beta", folder="blog", metadata={"date": date(2026, 3, 1)}),
        _make_post("Gamma", folder="blog", metadata={"date": date(2026, 2, 1)}),
    )
    parsed = _parse_dv_query("LIST\nSORT date ASC\nLIMIT 2")
    result = _execute_dv_query(parsed, index)
    # Earliest two: Alpha (Jan) and Gamma (Feb)
    assert "Alpha" in result
    assert "Gamma" in result
    assert "Beta" not in result
```

- [ ] **Step 2: Run all dataview unit tests so far**

```bash
/home/air/venv/3.14/bin/pytest tests/unit/test_dataview.py -v
```

Expected: 7 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_dataview.py
git commit -m "test: unit tests for FROM tag, WHERE, SORT, LIMIT"
```

---

## Task 6: Unit tests — inline expression renderer

**Files:**
- Modify: `tests/unit/test_dataview.py` (append)

These three tests cover the code-block guard bug fixed in v1.40.2.

- [ ] **Step 1: Append three inline tests to `tests/unit/test_dataview.py`**

```python
def test_inline_eval_title():
    ctx = {"title": "My Note", "file": {"name": "My Note"}}
    result = convert_dataview_inline("Title: `= this.title`", ctx)
    assert '<span class="dv-inline">My Note</span>' in result


def test_inline_skips_fenced_code_block():
    """Expressions inside ``` blocks must not be evaluated."""
    ctx = {"title": "My Note", "file": {"name": "My Note"}}
    md = "```\n`= this.title`\n```"
    result = convert_dataview_inline(md, ctx)
    assert "dv-inline" not in result
    assert "`= this.title`" in result


def test_inline_skips_multi_backtick_span():
    """Double-backtick code spans must pass through untouched."""
    ctx = {"title": "My Note", "file": {"name": "My Note"}}
    md = "Example: `` `= this.title` ``"
    result = convert_dataview_inline(md, ctx)
    assert "dv-inline" not in result
```

- [ ] **Step 2: Run all dataview unit tests**

```bash
/home/air/venv/3.14/bin/pytest tests/unit/test_dataview.py -v
```

Expected: 10 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_dataview.py
git commit -m "test: unit tests for inline dataview expression renderer"
```

---

## Task 7: Unit tests — `obsidian_syntax.py`

**Files:**
- Create: `tests/unit/test_obsidian_syntax.py`

- [ ] **Step 1: Create `tests/unit/test_obsidian_syntax.py`**

```python
"""Unit tests for obsidian_syntax.py — callouts, checkboxes, highlights."""
from obsidian_syntax import convert_callouts, convert_checkboxes, convert_highlights


def test_callout_renders():
    md = "> [!note] My Title\n> Some content"
    result = convert_callouts(md)
    assert 'class="callout callout-note"' in result
    assert "My Title" in result
    assert "Some content" in result


def test_checkbox_unchecked():
    md = "- [ ] Do this"
    result = convert_checkboxes(md)
    assert 'type="checkbox"' in result
    assert "checked" not in result
    assert "Do this" in result


def test_checkbox_checked():
    md = "- [x] Done"
    result = convert_checkboxes(md)
    assert 'type="checkbox"' in result
    assert "checked" in result
    assert "Done" in result


def test_highlight():
    md = "This is ==highlighted== text"
    result = convert_highlights(md)
    assert "<mark>highlighted</mark>" in result
```

- [ ] **Step 2: Run the tests**

```bash
/home/air/venv/3.14/bin/pytest tests/unit/test_obsidian_syntax.py -v
```

Expected: 4 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_obsidian_syntax.py
git commit -m "test: unit tests for callouts, checkboxes, highlights"
```

---

## Task 8: Integration tests — routes

**Files:**
- Create: `tests/integration/test_routes.py`

- [ ] **Step 1: Create `tests/integration/test_routes.py`**

```python
"""Integration tests for Flask routes using the fixture vault."""


def test_homepage_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_blog_listing_200(client):
    resp = client.get("/blog")
    assert resp.status_code == 200
    # Listing page must link to the simple post
    assert b"Simple Post" in resp.data


def test_simple_post_200(client):
    resp = client.get("/blog/simple-post")
    assert resp.status_code == 200
    assert b"Simple Post" in resp.data


def test_post_with_dataview_200(client):
    resp = client.get("/blog/dataview-post")
    assert resp.status_code == 200
    # Dataview block must have been rendered to HTML
    assert b'class="dataview"' in resp.data


def test_post_dataview_inline_not_in_code_block(client):
    """The `` `= this.title` `` inside the code block must appear as literal code."""
    resp = client.get("/blog/dataview-post")
    html = resp.data.decode()
    # The literal string should appear in a <code> element, not as a dv-inline span
    assert "`= this.title`" in html


def test_unknown_route_404(client):
    resp = client.get("/this-does-not-exist")
    assert resp.status_code == 404


def test_search_returns_results(client):
    # "simple" appears in simple_post.md body
    resp = client.get("/search?q=simple")
    assert resp.status_code == 200
    assert b"Simple Post" in resp.data


def test_search_no_results(client):
    resp = client.get("/search?q=zzznomatchxxx")
    assert resp.status_code == 200
    # Page renders without crashing; no post title in results
    assert b"Simple Post" not in resp.data
```

- [ ] **Step 2: Run the integration route tests**

```bash
/home/air/venv/3.14/bin/pytest tests/integration/test_routes.py -v
```

Expected: 8 passed. If any fail, the most common cause is a slug mismatch — check the actual URL by looking at startup output or `/sitemap.xml`.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_routes.py
git commit -m "test: integration tests for Flask routes"
```

---

## Task 9: Integration tests — feeds

**Files:**
- Create: `tests/integration/test_feeds.py`

- [ ] **Step 1: Create `tests/integration/test_feeds.py`**

```python
"""Integration tests for /feed.xml and /sitemap.xml."""


def test_feed_xml_200(client):
    resp = client.get("/feed.xml")
    assert resp.status_code == 200
    assert b"xml" in resp.content_type.encode()


def test_feed_has_items(client):
    resp = client.get("/feed.xml")
    assert b"<item>" in resp.data


def test_sitemap_200(client):
    resp = client.get("/sitemap.xml")
    assert resp.status_code == 200


def test_sitemap_has_urls(client):
    resp = client.get("/sitemap.xml")
    assert b"<url>" in resp.data
```

- [ ] **Step 2: Run the feed tests**

```bash
/home/air/venv/3.14/bin/pytest tests/integration/test_feeds.py -v
```

Expected: 4 passed.

- [ ] **Step 3: Run the full suite**

```bash
/home/air/venv/3.14/bin/pytest -v
```

Expected: all 26 tests pass (10 dataview + 4 obsidian_syntax + 8 routes + 4 feeds).

- [ ] **Step 4: Commit**

```bash
git add tests/integration/test_feeds.py
git commit -m "test: integration tests for feed.xml and sitemap.xml"
```

---

## Task 10: GitHub Actions CI

**Files:**
- Create: `.github/workflows/test.yml`

- [ ] **Step 1: Create `.github/workflows/test.yml`**

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

Python 3.12 is used on CI because GitHub Actions runners do not yet have 3.14. The app is expected to be compatible — CI will surface any incompatibilities on the first push.

- [ ] **Step 2: Commit and push**

```bash
git add .github/workflows/test.yml
git commit -m "ci: add GitHub Actions test workflow"
git push origin main
```

- [ ] **Step 3: Verify CI passes**

Go to the GitHub Actions tab on the InkStone repo and confirm the workflow run is green. If it fails on a dependency missing from `requirements.txt`, add it there and push again.

- [ ] **Step 4: Version bump**

This is a new feature (test infrastructure), so bump MINOR:

```bash
echo "1.41.0" > VERSION
git add VERSION
git commit -m "chore: bump version to 1.41.0"
git tag v1.41.0
git push origin main
git push origin v1.41.0
```
