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
