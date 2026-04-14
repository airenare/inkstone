# OnyxFolio Rebrand Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the project from "Obsidian Blog Engine" to "OnyxFolio" across all files in the repo.

**Architecture:** Pure rename — no logic changes. Six files contain the old name; each gets updated in its own commit. GitHub repo rename is a manual step via `gh` CLI.

**Tech Stack:** Python/Flask, Jinja2 templates, Markdown, GitHub CLI (`gh`)

---

## Files to Modify

| File | What changes |
|------|-------------|
| `README.md` | Title, tagline, repo URLs, docker image name |
| `CLAUDE.md` | Module docstring reference, project description |
| `converters.py` | Module docstring line 1 |
| `frontend/templates/base.html` | HTML comment version tag |
| `BlogPages/Test Website.md` | Vault homepage content |
| GitHub repo | Rename via `gh` CLI (manual step) |

---

## Task 1: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace project title and tagline**

Open `README.md`. Change line 1:
```markdown
# OnyxFolio
```
Add tagline on line 2:
```markdown
> Your notes, published.
```

- [ ] **Step 2: Replace repo clone URLs**

Find:
```
git clone https://github.com/you/obsidian-blog-engine
cd obsidian-blog-engine
```
Replace with:
```
git clone https://github.com/airenare/onyxfolio
cd onyxfolio
```

- [ ] **Step 3: Replace Docker image name**

Find:
```
docker build -t obsidian-blog .
docker run -p 8000:8000 -v /path/to/vault:/vault obsidian-blog
```
Replace with:
```
docker build -t onyxfolio .
docker run -p 8000:8000 -v /path/to/vault:/vault onyxfolio
```

- [ ] **Step 4: Scan for any remaining old name occurrences**

```bash
grep -n "Obsidian Blog Engine\|obsidian-blog" README.md
```
Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "rebrand: update README to OnyxFolio"
```

---

## Task 2: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Replace project name in description**

Find every occurrence of `Obsidian Blog Engine` in `CLAUDE.md` and replace with `OnyxFolio`.

```bash
grep -n "Obsidian Blog Engine" CLAUDE.md
```

- [ ] **Step 2: Verify**

```bash
grep -n "Obsidian Blog Engine\|obsidian-blog" CLAUDE.md
```
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "rebrand: update CLAUDE.md to OnyxFolio"
```

---

## Task 3: Update converters.py docstring

**Files:**
- Modify: `converters.py:1`

- [ ] **Step 1: Update module docstring**

Line 1 of `converters.py` currently reads:
```python
"""Markdown rendering pipeline for the Obsidian Blog Engine.
```
Change to:
```python
"""Markdown rendering pipeline for OnyxFolio.
```

- [ ] **Step 2: Verify**

```bash
grep -n "Obsidian Blog Engine" converters.py
```
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add converters.py
git commit -m "rebrand: update converters.py docstring"
```

---

## Task 4: Update base.html version comment

**Files:**
- Modify: `frontend/templates/base.html:3`

- [ ] **Step 1: Update HTML comment**

Line 3 of `base.html` currently reads:
```html
<!-- obsidian-blog-engine v{{ app_version }} -->
```
Change to:
```html
<!-- onyxfolio v{{ app_version }} -->
```

- [ ] **Step 2: Verify**

```bash
grep -n "obsidian-blog-engine" frontend/templates/base.html
```
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add frontend/templates/base.html
git commit -m "rebrand: update base.html version comment"
```

---

## Task 5: Update vault homepage

**Files:**
- Modify: `BlogPages/Test Website.md`

- [ ] **Step 1: Check current content**

```bash
grep -n "Obsidian Blog Engine\|obsidian blog" "BlogPages/Test Website.md"
```

- [ ] **Step 2: Replace all occurrences**

Replace every instance of `Obsidian Blog Engine` with `OnyxFolio` in `BlogPages/Test Website.md`.

- [ ] **Step 3: Verify**

```bash
grep -n "Obsidian Blog Engine\|obsidian blog" "BlogPages/Test Website.md"
```
Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add "BlogPages/Test Website.md"
git commit -m "rebrand: update vault homepage to OnyxFolio"
```

---

## Task 6: Full codebase scan and cleanup

**Files:**
- Any file that still contains the old name

- [ ] **Step 1: Scan everything**

```bash
grep -r "Obsidian Blog Engine\|obsidian-blog-engine\|obsidian_blog_engine" \
  --include="*.py" --include="*.md" --include="*.html" \
  --include="*.txt" --include="*.sh" .
```
Expected: only the spec doc (`docs/superpowers/specs/2026-04-13-onyxfolio-rebrand-design.md`) should appear — that one is intentional historical record, leave it.

- [ ] **Step 2: Fix any unexpected hits**

If any other file appears in the output, update it and commit:
```bash
git add <file>
git commit -m "rebrand: replace old name in <file>"
```

---

## Task 7: Bump version and tag

- [ ] **Step 1: Bump VERSION**

This is a MINOR change (new branding/identity). Current version: `1.13.2`.

Edit `VERSION`:
```
1.14.0
```

- [ ] **Step 2: Commit and tag**

```bash
git add VERSION
git commit -m "chore: bump version to 1.14.0"
git tag v1.14.0
git push origin v1.14.0
```

---

## Task 8: Rename GitHub repository

- [ ] **Step 1: Rename via gh CLI**

```bash
gh repo rename onyxfolio --repo airenare/Obsidian-Blog-Engine
```

- [ ] **Step 2: Update remote URL locally**

```bash
git remote set-url origin https://github.com/airenare/onyxfolio
```

- [ ] **Step 3: Verify**

```bash
git remote -v
```
Expected:
```
origin  https://github.com/airenare/onyxfolio (fetch)
origin  https://github.com/airenare/onyxfolio (push)
```

- [ ] **Step 4: Push everything**

```bash
git push
```

---

## Done Criteria

- [ ] No file in the repo (excluding the spec doc) contains "Obsidian Blog Engine" or "obsidian-blog-engine"
- [ ] README opens with `# OnyxFolio` and tagline
- [ ] GitHub repo URL is `github.com/airenare/onyxfolio`
- [ ] VERSION is `1.14.0`, tagged `v1.14.0`
