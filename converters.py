"""Markdown rendering pipeline for OnyxFolio.

This module is the only one imported externally.  It re-exports the
utilities that other modules (posts.py) need and wires all the converter
steps into render_markdown().

Import graph (no cycles):
  config  ←  obsidian_syntax  ←  converters  ←  posts  ←  app
                dataview      ↗
"""
import os

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

# Re-export so callers that do `from converters import slugify` keep working
__all__ = [
    "slugify",
    "extract_h1",
    "strip_leading_h1",
    "render_markdown",
]


def render_markdown(md, path, url_index=None, dataview_index=None,
                    note_metadata=None):
    md = strip_leading_h1(md)
    md = convert_media(md, path)
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
        md = convert_dataview_inline(md, note_ctx)
    if dataview_index is not None:
        md = convert_dataview(md, dataview_index)

    md_obj = markdown.Markdown(
        extensions=["fenced_code", "tables", "toc", "md_in_html", "codehilite",
                    "footnotes"],
        output_format="html5",
    )
    html_str = md_obj.convert(md)
    toc = md_obj.toc if md_obj.toc_tokens else ""

    return html_str, toc
