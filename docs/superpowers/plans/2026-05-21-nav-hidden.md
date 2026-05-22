# nav_hidden Frontmatter Option Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `nav_hidden: true` frontmatter field that lets a `type: listing` or `type: homepage` section opt out of appearing in the top nav bar while remaining fully routable.

**Architecture:** Single filter addition in `app.py`'s `inject_globals` context processor — both the default-lang and non-default-lang `top_sections` generators get `and not route["post"].get("nav_hidden")`. No changes to `posts.py` (the field is read from post metadata like any other frontmatter field). Docs updated in two vault files and `CLAUDE.md`.

**Tech Stack:** Python/Flask, pytest

---

### Task 1: Add `nav_hidden` filter to `app.py`

**Files:**
- Modify: `app.py:108–122`

- [ ] **Step 1: Read the current filter**

Open `app.py` and locate the `inject_globals` context processor (around line 101). The two `top_sections` generators are at lines 108–114 (default lang) and 117–122 (non-default lang).

- [ ] **Step 2: Add the filter to the default-lang branch**

In the first `top_sections` sorted() call, add one more condition to the `if` clause:

```python
        top_sections = sorted(
            (url, route["post"].get("title", url.lstrip("/").title()))
            for url, route in post_store.SECTION_ROUTES.items()
            if url not in ("/", f"/{current_lang}")
            and url.count("/") == 1
            and route.get("lang", post_store.DEFAULT_LANG) == post_store.DEFAULT_LANG
            and not route["post"].get("nav_hidden")
        )
```

- [ ] **Step 3: Add the filter to the non-default-lang branch**

In the second `top_sections` sorted() call:

```python
        top_sections = sorted(
            (url, route["post"].get("title", url.lstrip("/").title()))
            for url, route in post_store.SECTION_ROUTES.items()
            if route.get("lang") == current_lang
            and url.count("/") == 2
            and not route["post"].get("nav_hidden")
        )
```

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add nav_hidden frontmatter option to hide sections from top nav"
```

---

### Task 2: Write integration test for `nav_hidden`

**Files:**
- Modify: `tests/fixtures/vault/gallery/Gallery Index.md` (temporarily add `nav_hidden: true` for one test fixture, then revert — or add a dedicated hidden fixture)
- Create: `tests/integration/test_nav_hidden.md` fixture at `tests/fixtures/vault/hidden/Hidden Section.md`
- Modify: `tests/integration/test_routes.py`

- [ ] **Step 1: Create a hidden-section fixture**

Create `tests/fixtures/vault/hidden/Hidden Section.md`:

```markdown
---
website: true
type: listing
title: Hidden Section
nav_hidden: true
---
```

- [ ] **Step 2: Write the failing tests**

Add to `tests/integration/test_routes.py`:

```python
def test_nav_hidden_section_not_in_nav(client):
    """Sections with nav_hidden: true must not appear in the top nav."""
    resp = client.get("/")
    assert resp.status_code == 200
    # The hidden section's listing page must still be routable
    hidden_resp = client.get("/hidden")
    assert hidden_resp.status_code == 200
    # But its title must not appear in the nav rendered on the homepage
    assert b"Hidden Section" not in resp.data


def test_nav_hidden_section_still_routable(client):
    """nav_hidden only hides from nav — the section must still load."""
    resp = client.get("/hidden")
    assert resp.status_code == 200
    assert b"Hidden Section" in resp.data
```

- [ ] **Step 3: Run the tests to verify they fail**

```bash
cd /Users/anton/GitHubRepos/InkStone
source ~/312/bin/activate
pytest tests/integration/test_routes.py::test_nav_hidden_section_not_in_nav tests/integration/test_routes.py::test_nav_hidden_section_still_routable -v
```

Expected: first test FAILS (Hidden Section appears in nav before fix), second test PASSES (section is routable regardless).

- [ ] **Step 4: Run again after Task 1 is complete to verify both pass**

```bash
pytest tests/integration/test_routes.py::test_nav_hidden_section_not_in_nav tests/integration/test_routes.py::test_nav_hidden_section_still_routable -v
```

Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/vault/hidden/Hidden\ Section.md tests/integration/test_routes.py
git commit -m "test: add integration tests for nav_hidden section behaviour"
```

---

### Task 3: Update docs — Navigation page

**Files:**
- Modify: `BlogPages/InkStone_Docs/site-structure/Navigation.md`

- [ ] **Step 1: Add a "Hiding sections from the nav" section**

After the "Auto-generated nav" section (after line 23), insert:

```markdown
## Hiding sections from the nav

A section appears in the nav by default. To hide it, add `nav_hidden: true` to the listing or homepage file for that section:

```yaml
---
website: true
type: listing
title: Archive
nav_hidden: true
---
```

The section is still fully routable — visitors can reach it via direct links or wiki-links. It simply won't appear as a nav item.
```

- [ ] **Step 2: Commit**

```bash
git add "BlogPages/InkStone_Docs/site-structure/Navigation.md"
git commit -m "docs: document nav_hidden frontmatter option in Navigation page"
```

---

### Task 4: Update docs — Frontmatter Reference page

**Files:**
- Modify: `BlogPages/InkStone_Docs/writing/Frontmatter Reference.md`

- [ ] **Step 1: Add nav_hidden row to the table**

Insert after the `menu_order` row:

```markdown
| `nav_hidden` | boolean | Hides this section from the auto-generated top nav. The section remains routable. Only meaningful on `type: listing` or `type: homepage` files. | `nav_hidden: true` |
```

- [ ] **Step 2: Commit**

```bash
git add "BlogPages/InkStone_Docs/writing/Frontmatter Reference.md"
git commit -m "docs: add nav_hidden to Frontmatter Reference table"
```

---

### Task 5: Update CLAUDE.md frontmatter reference

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add nav_hidden to the frontmatter YAML block**

In `CLAUDE.md`, find the frontmatter reference block (the big `---` YAML comment block under `### Frontmatter Reference`). After the `menu_order` line, add:

```yaml
nav_hidden: true      # listing/homepage only; hides section from top nav while keeping
                      #   it routable; visitors can still reach it via direct link
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add nav_hidden to CLAUDE.md frontmatter reference"
```

---

### Task 6: Version bump

**Files:**
- Modify: `VERSION`

- [ ] **Step 1: Bump MINOR version**

Current version is `1.42.0`. This is a new feature → MINOR bump.

Edit `VERSION` to contain:
```
1.43.0
```

- [ ] **Step 2: Commit and tag**

```bash
git add VERSION
git commit -m "chore: bump version to 1.43.0"
git tag v1.43.0
git push origin main --tags
```
