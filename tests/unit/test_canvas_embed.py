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
