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


# --- _folder_matches ---

def test_folder_matches_exact():
    assert _folder_matches("blog", "blog") is True


def test_folder_matches_subfolder():
    assert _folder_matches("blog/sub", "blog") is True


def test_folder_matches_no_false_prefix():
    # "blogging" must NOT match FROM "blog"
    assert _folder_matches("blogging", "blog") is False


# --- FROM folder ---

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


# --- FROM tag, WHERE, SORT, LIMIT ---

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


# --- Inline expression renderer ---

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
