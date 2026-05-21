"""Unit tests for obsidian_syntax.py — callouts, checkboxes, highlights."""
from obsidian_syntax import (
    convert_callouts,
    convert_checkboxes,
    convert_highlights,
    _parse_caption,
    convert_media,
)


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


def test_parse_caption_left():
    assert _parse_caption("left") == (False, "left", None, "")


def test_parse_caption_right_with_width_and_caption():
    assert _parse_caption("right 300 My Caption") == (
        False, "right", "300", "My Caption"
    )


def test_parse_caption_inline_unchanged():
    assert _parse_caption("inline 200 Alt") == (True, None, "200", "Alt")


def test_parse_caption_bare_number_unchanged():
    assert _parse_caption("400") == (False, None, "400", "")


def test_float_left_figure_html():
    from pathlib import Path
    fixture_post = str(
        Path(__file__).parent.parent / "fixtures" / "vault" / "blog" / "simple_post.md"
    )
    md = "![[test.jpg|left 300 My Alt]]"
    result = convert_media(md, fixture_post)
    assert 'class="figure-left"' in result
    assert 'style="max-width:300px"' in result
    assert '<figcaption>My Alt</figcaption>' in result
    assert "data-gallery" not in result
