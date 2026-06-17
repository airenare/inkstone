"""Unit tests for obsidian_syntax.py — callouts, checkboxes, highlights."""
from obsidian_syntax import (
    convert_callouts,
    convert_checkboxes,
    convert_highlights,
    convert_links,
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


def test_convert_links_skips_html_code_tags():
    """[[...]] inside a <code> HTML element must not be converted to a markdown link.

    convert_transclusion embeds rendered HTML before convert_links runs, so
    <code>![[Note Title]]</code> must survive unchanged.
    """
    md = "Before <code>![[Note Title]]</code> after"
    result = convert_links(md, {})
    assert "<code>![[Note Title]]</code>" in result
    assert "Note Title" not in result.replace("<code>![[Note Title]]</code>", "")


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
    assert 'data-gallery="g1"' in result
    assert 'data-type="image"' in result


def test_gallery_ids_are_unique_across_groups():
    """Two image groups separated by text must get different gallery IDs."""
    from pathlib import Path
    fixture_post = str(
        Path(__file__).parent.parent / "fixtures" / "vault" / "blog" / "simple_post.md"
    )
    md = "![[test.jpg]]\n\nSome text between.\n\n![[test.jpg]]"
    result = convert_media(md, fixture_post)
    assert 'data-gallery="g1"' in result
    assert 'data-gallery="g2"' in result


def test_consecutive_images_share_gallery_id():
    """Consecutive image lines (a gallery block) must share one gallery ID."""
    from pathlib import Path
    fixture_post = str(
        Path(__file__).parent.parent / "fixtures" / "vault" / "blog" / "simple_post.md"
    )
    md = "![[test.jpg]]\n![[test.jpg]]"
    result = convert_media(md, fixture_post)
    assert result.count('data-gallery="g1"') == 2
    assert 'data-gallery="g2"' not in result
