# Canvas Embed in Notes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow any `.canvas` file in the vault to be embedded inline in a markdown note with `![[CanvasName]]`, rendering the same interactive SVG the standalone canvas page shows.

**Architecture:** A new `convert_canvas_embed(md, url_index)` function in `converters.py` scans the vault for `.canvas` files, replaces matching `![[…]]` embeds with a `<div class="canvas-embed">` wrapping the rendered SVG, and leaves unrecognised embeds untouched for `convert_transclusion()`. It runs after `convert_media()` and before `convert_transclusion()` in `render_markdown()`. `render_canvas` is imported lazily inside the function to break the existing `canvas.py → converters.py` import cycle.

**Tech stack:** Python 3.14, Flask, `os.walk` for vault scan, existing `render_canvas()` from `canvas.py`, pytest.

---

## File map

| File | Action |
|------|--------|
| `converters.py` | Add `convert_canvas_embed()`; add call in `render_markdown()` |
| `frontend/static/base.css` | Add `.canvas-embed` + `.canvas-embed .canvas-view` override |
| `tests/fixtures/vault/embed_canvas.canvas` | New minimal canvas fixture (no `__website` — proves any canvas embeds) |
| `tests/fixtures/vault/blog/dv_post.md` | Add `![[embed_canvas]]` embed |
| `tests/unit/test_canvas_embed.py` | New unit tests |
| `tests/integration/test_routes.py` | New integration assertion |
| `VERSION` | Bump MINOR (1.44.1 → 1.45.0) |

---

## Task 1: Fixture canvas file + failing unit tests

**Files:**
- Create: `tests/fixtures/vault/embed_canvas.canvas`
- Create: `tests/unit/test_canvas_embed.py`

- [ ] **Step 1: Create the minimal fixture canvas**

Create `tests/fixtures/vault/embed_canvas.canvas`:

```json
{"nodes":[{"id":"n1","type":"text","text":"Hello from canvas","x":0,"y":0,"width":200,"height":100}],"edges":[]}
```

- [ ] **Step 2: Write the failing unit tests**

Create `tests/unit/test_canvas_embed.py`:

```python
"""Unit tests for convert_canvas_embed in converters.py."""
import os
import pytest


def test_canvas_embed_by_stem(tmp_path, monkeypatch):
    """![[stem]] embeds a canvas when a matching .canvas file exists in vault."""
    import config
    monkeypatch.setattr(config, "VAULT_PATH", str(tmp_path))
    canvas = tmp_path / "my_diagram.canvas"
    canvas.write_text(
        '{"nodes":[{"id":"n1","type":"text","text":"Hi","x":0,"y":0,'
        '"width":100,"height":80}],"edges":[]}',
        encoding="utf-8",
    )

    from converters import convert_canvas_embed
    result = convert_canvas_embed("Before\n![[my_diagram]]\nAfter", url_index=None)
    assert 'class="canvas-embed"' in result
    assert 'class="canvas-view"' in result
    assert "![[my_diagram]]" not in result


def test_canvas_embed_with_canvas_extension(tmp_path, monkeypatch):
    """![[name.canvas]] also triggers the embed."""
    import config
    monkeypatch.setattr(config, "VAULT_PATH", str(tmp_path))
    canvas = tmp_path / "my_diagram.canvas"
    canvas.write_text(
        '{"nodes":[{"id":"n1","type":"text","text":"Hi","x":0,"y":0,'
        '"width":100,"height":80}],"edges":[]}',
        encoding="utf-8",
    )

    from converters import convert_canvas_embed
    result = convert_canvas_embed("![[my_diagram.canvas]]", url_index=None)
    assert 'class="canvas-embed"' in result
    assert "![[my_diagram.canvas]]" not in result


def test_unknown_embed_left_alone(tmp_path, monkeypatch):
    """![[UnknownNote]] with no matching canvas is left untouched."""
    import config
    monkeypatch.setattr(config, "VAULT_PATH", str(tmp_path))

    from converters import convert_canvas_embed
    md = "![[UnknownNote]]"
    result = convert_canvas_embed(md, url_index=None)
    assert result == md


def test_canvas_embed_skipped_in_code_block(tmp_path, monkeypatch):
    """![[canvas]] inside a fenced code block must not be evaluated."""
    import config
    monkeypatch.setattr(config, "VAULT_PATH", str(tmp_path))
    canvas = tmp_path / "diagram.canvas"
    canvas.write_text(
        '{"nodes":[{"id":"n1","type":"text","text":"Hi","x":0,"y":0,'
        '"width":100,"height":80}],"edges":[]}',
        encoding="utf-8",
    )

    from converters import convert_canvas_embed
    md = "```\n![[diagram]]\n```"
    result = convert_canvas_embed(md, url_index=None)
    assert 'class="canvas-embed"' not in result
    assert "![[diagram]]" in result


def test_canvas_embed_no_canvas_files(tmp_path, monkeypatch):
    """When the vault has no .canvas files the markdown is returned unchanged."""
    import config
    monkeypatch.setattr(config, "VAULT_PATH", str(tmp_path))

    from converters import convert_canvas_embed
    md = "![[anything]]"
    result = convert_canvas_embed(md, url_index=None)
    assert result == md
```

- [ ] **Step 3: Run tests to confirm they fail**

```bash
/Users/anton/GitHubRepos/InkStone/.venv/bin/python3 -m pytest tests/unit/test_canvas_embed.py -v
```

Expected: `ImportError` or `AttributeError` — `convert_canvas_embed` does not exist yet.

---

## Task 2: Implement `convert_canvas_embed` and wire into pipeline

**Files:**
- Modify: `converters.py`

- [ ] **Step 1: Add `convert_canvas_embed` to `converters.py`**

Add the import of `config` at the top of `converters.py` (after the existing imports):

```python
import config as _config
```

Then add the function body after the `_restore_mermaid` function and before `render_markdown`:

```python
def convert_canvas_embed(md, url_index=None):
    """Replace ![[CanvasName]] / ![[CanvasName.canvas]] with inline SVG embeds.

    Scans VAULT_PATH for .canvas files, builds a stem lookup, and substitutes
    matching embeds.  Unrecognised embeds are left for convert_transclusion().
    Runs after convert_media() so image/video embeds are already resolved.
    """
    from canvas import render_canvas  # lazy import — canvas.py imports converters

    # Build stem → filepath index from vault
    canvas_index = {}
    vault = _config.VAULT_PATH
    try:
        for root, _dirs, files in os.walk(vault):
            for fname in files:
                if fname.endswith(".canvas"):
                    stem = fname[:-7]
                    fpath = os.path.join(root, fname)
                    canvas_index[stem.lower()] = fpath
                    canvas_index[slugify(stem).lower()] = fpath
    except OSError:
        return md

    if not canvas_index:
        return md

    _fence_open = re.compile(r"^(`{3,}|~{3,})")
    pattern = re.compile(r'!\[\[([^|\]#\n]+?)(?:\|[^\]]*)?\]\]')
    lines = md.split("\n")
    output = []
    fence_marker = None

    for line in lines:
        if fence_marker is None:
            m = _fence_open.match(line)
            if m:
                fence_marker = m.group(1)
                output.append(line)
                continue
        else:
            output.append(line)
            if re.match(r"^" + re.escape(fence_marker) + r"`*~*\s*$", line):
                fence_marker = None
            continue

        def _repl(match):
            raw = match.group(1).strip()
            stem = raw[:-7] if raw.lower().endswith(".canvas") else raw
            filepath = (
                canvas_index.get(stem.lower())
                or canvas_index.get(slugify(stem).lower())
            )
            if not filepath:
                return match.group(0)
            try:
                canvas_html = render_canvas(filepath, url_index=url_index)
                return f'<div class="canvas-embed">\n{canvas_html}\n</div>'
            except Exception:
                return (
                    f'<em class="canvas-embed-error">'
                    f"Canvas error: {stem}</em>"
                )

        output.append(pattern.sub(_repl, line))

    return "\n".join(output)
```

- [ ] **Step 2: Insert the call in `render_markdown()`**

Find this block in `render_markdown()`:

```python
    md = convert_media(md, path)
    if dataview_index is not None:
        md = convert_transclusion(md, dataview_index)
```

Replace with:

```python
    md = convert_media(md, path)
    md = convert_canvas_embed(md, url_index)
    if dataview_index is not None:
        md = convert_transclusion(md, dataview_index)
```

- [ ] **Step 3: Run the unit tests**

```bash
/Users/anton/GitHubRepos/InkStone/.venv/bin/python3 -m pytest tests/unit/test_canvas_embed.py -v
```

Expected: all 5 tests **PASS**.

- [ ] **Step 4: Run the full suite to check for regressions**

```bash
/Users/anton/GitHubRepos/InkStone/.venv/bin/python3 -m pytest --tb=short
```

Expected: all tests pass (count increases by 5).

- [ ] **Step 5: Commit**

```bash
git add converters.py tests/fixtures/vault/embed_canvas.canvas tests/unit/test_canvas_embed.py
git commit -m "feat: convert_canvas_embed — inline ![[Canvas]] embeds in notes"
```

---

## Task 3: CSS for embedded canvas wrapper

**Files:**
- Modify: `frontend/static/base.css`

- [ ] **Step 1: Find the canvas CSS block in `base.css`**

Look for the comment `/* CANVAS VIEW */` around line 1638. The `.canvas-view` rule starts immediately below it.

- [ ] **Step 2: Add `.canvas-embed` styles after the last canvas rule**

After the final existing `.canvas-*` rule in that block (around line 1860), add:

```css
/* Inline canvas embed (inside a note) */
.canvas-embed {
    margin: 1.5em 0;
}

.canvas-embed .canvas-view {
    height: 400px;
    margin: 0;
}
```

This keeps the standalone canvas at `min(80vh, 600px)` and constrains embedded ones to `400px`.

- [ ] **Step 3: Run the full suite**

```bash
/Users/anton/GitHubRepos/InkStone/.venv/bin/python3 -m pytest --tb=short
```

Expected: all tests still pass (CSS has no test coverage, just a sanity check).

- [ ] **Step 4: Commit**

```bash
git add frontend/static/base.css
git commit -m "style: canvas-embed wrapper constrains inline canvas to 400px"
```

---

## Task 4: Integration test

**Files:**
- Modify: `tests/fixtures/vault/blog/dv_post.md`
- Modify: `tests/integration/test_routes.py`

- [ ] **Step 1: Add canvas embed to the fixture post**

Edit `tests/fixtures/vault/blog/dv_post.md`. After the last dataview block, add:

```markdown
Canvas embed example:

![[embed_canvas]]
```

Full file after edit:

```markdown
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

```dataview
TABLE
FROM "blog"
WHERE contains(type, listing)
```

Code block example that must not be evaluated:

```
`= this.title`
```

Canvas embed example:

![[embed_canvas]]
```

(Note: the triple-backtick blocks inside the markdown above are literal — copy the file content exactly as it will appear on disk.)

- [ ] **Step 2: Write the integration test**

Add to `tests/integration/test_routes.py`:

```python
def test_canvas_embed_renders_in_post(client):
    """![[embed_canvas]] in a post must render an inline canvas-embed div."""
    resp = client.get("/blog/dataview-post")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert 'class="canvas-embed"' in html
    assert "![[embed_canvas]]" not in html
```

- [ ] **Step 3: Run the integration tests**

```bash
/Users/anton/GitHubRepos/InkStone/.venv/bin/python3 -m pytest tests/integration/test_routes.py -v
```

Expected: `test_canvas_embed_renders_in_post` **PASS**; all other tests still pass.

- [ ] **Step 4: Run full suite**

```bash
/Users/anton/GitHubRepos/InkStone/.venv/bin/python3 -m pytest --tb=short
```

Expected: all tests pass (total increases by 1).

- [ ] **Step 5: Commit**

```bash
git add "tests/fixtures/vault/blog/dv_post.md" tests/integration/test_routes.py
git commit -m "test: integration test for inline canvas embed"
```

---

## Task 5: Version bump, tag, push

**Files:**
- Modify: `VERSION`

- [ ] **Step 1: Bump VERSION**

Edit `VERSION` to read:

```
1.45.0
```

- [ ] **Step 2: Commit, tag, push**

```bash
git add VERSION
git commit -m "chore: bump version to 1.45.0"
git tag v1.45.0
git push origin main v1.45.0
```

Expected output includes `* [new tag] v1.45.0 -> v1.45.0`.
