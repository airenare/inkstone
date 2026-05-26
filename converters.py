"""Markdown rendering pipeline for InkStone.

This module is the only one imported externally.  It re-exports the
utilities that other modules (posts.py) need and wires all the converter
steps into render_markdown().

Import graph (no cycles):
  config  ←  obsidian_syntax  ←  converters  ←  posts  ←  app
                dataview      ↗
"""
import html as _html_module
import os
import re

import markdown

from obsidian_syntax import (
    slugify,
    extract_h1,
    strip_leading_h1,
    convert_links,
    convert_checkboxes,
    convert_callouts,
    convert_media,
    convert_transclusion,
    convert_block_ids,
    convert_highlights,
    convert_math,
)
from dataview import convert_dataview, convert_dataview_inline
import config as _config

# Re-export so callers that do `from converters import slugify` keep working
__all__ = [
    "slugify",
    "extract_h1",
    "strip_leading_h1",
    "render_markdown",
    "convert_canvas_embed",
]


_MERMAID_TOKEN = "ONYXMERMAID{i}ONYXEND"


def _extract_mermaid(md):
    """Pull ```mermaid blocks out before codehilite can strip their class.

    Only extracts top-level mermaid blocks — blocks nested inside a larger
    fenced block (e.g. a ````markdown```` example) are left untouched.
    """
    blocks = []
    result = []
    outer_fence = None  # fence marker of the enclosing non-mermaid block
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if outer_fence is None:
            m = re.match(r"^(`{3,}|~{3,})(\S*)", line)
            if m:
                marker, lang = m.group(1), m.group(2).lower()
                if lang == "mermaid":
                    content = []
                    i += 1
                    while i < len(lines) and not lines[i].startswith(marker):
                        content.append(lines[i])
                        i += 1
                    idx = len(blocks)
                    blocks.append("\n".join(content))
                    result += ["", _MERMAID_TOKEN.format(i=idx), ""]
                else:
                    outer_fence = marker
                    result.append(line)
            else:
                result.append(line)
        else:
            result.append(line)
            if re.match(rf"^{re.escape(outer_fence)}\s*$", line):
                outer_fence = None
        i += 1
    return "\n".join(result), blocks


def _restore_mermaid(html_str, blocks):
    """Replace tokens with <div class="mermaid"> elements."""
    for i, src in enumerate(blocks):
        escaped = _html_module.escape(src)
        div = (
            f'<div class="mermaid" data-mermaid-src="{escaped}">'
            f"{escaped}</div>"
        )
        html_str = html_str.replace(
            f"<p>{_MERMAID_TOKEN.format(i=i)}</p>", div
        )
    return html_str


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


def render_markdown(md, path, url_index=None, dataview_index=None,
                    note_metadata=None, skip_strip_h1=False):
    if not skip_strip_h1:
        md = strip_leading_h1(md)
    md = convert_media(md, path)
    md = convert_canvas_embed(md, url_index)
    if dataview_index is not None:
        md = convert_transclusion(md, dataview_index)
    md = convert_links(md, url_index)
    md = convert_callouts(md)
    md = convert_checkboxes(md)
    md = convert_highlights(md)
    md = convert_block_ids(md)
    md = convert_math(md)
    if note_metadata is not None:
        note_ctx = dict(note_metadata)
        note_ctx["file"] = {"name": os.path.basename(path)}
        md = convert_dataview_inline(md, note_ctx, dataview_index=dataview_index)
    if dataview_index is not None:
        md = convert_dataview(md, dataview_index)

    md, mermaid_blocks = _extract_mermaid(md)

    md_obj = markdown.Markdown(
        extensions=["fenced_code", "tables", "toc", "md_in_html", "codehilite",
                    "footnotes"],
        output_format="html5",
    )
    html_str = md_obj.convert(md)
    toc = md_obj.toc if md_obj.toc_tokens else ""

    html_str = _restore_mermaid(html_str, mermaid_blocks)

    return html_str, toc
