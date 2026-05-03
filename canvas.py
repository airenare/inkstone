import html as _html
import json
import os
from urllib.parse import urlparse as _urlparse

import config as _config
from converters import render_markdown as _render_markdown
from obsidian_syntax import slugify


CANVAS_PUBLISH_FILENAME_SUFFIX = "__website"

CANVAS_COLOR_MAP = {
    "1": "#fb464c",
    "2": "#e9973f",
    "3": "#e0de71",
    "4": "#44cf6e",
    "5": "#53dfdd",
    "6": "#a882ff",
}

# Minimum bezier handle length in px units
_CTRL_MIN = 100


def canvas_filename_publish_meta(filename):
    """Parse ``*.canvas`` filename for InkStone publish marker.

    Obsidian strips custom top-level JSON keys like ``website`` when saving.
    A durable convention is ``Title__website.canvas``: the part before the
    suffix becomes the page title; the suffix marks the board for publishing.

    Returns:
        (publish_via_filename, display_stem, raw_stem)
        publish_via_filename — True if ``raw_stem`` ends with ``__website``
            (case-insensitive).
        display_stem — title base: suffix stripped when publish marker present,
            otherwise same as raw_stem.
        raw_stem — filename with ``.canvas`` removed.
    """
    if not filename.endswith(".canvas"):
        return False, "", ""
    raw_stem = filename[:-7]
    suf = CANVAS_PUBLISH_FILENAME_SUFFIX
    if raw_stem.lower().endswith(suf):
        base = raw_stem[: -len(suf)].rstrip()
        display = base if base else raw_stem
        return True, display, raw_stem
    return False, raw_stem, raw_stem


def _side_point(node, side, min_x, min_y):
    """Return (x_px, y_px) for the connection point on a given side."""
    nx = node["x"] - min_x
    ny = node["y"] - min_y
    nw = node["width"]
    nh = node["height"]
    if side == "left":
        return nx, ny + nh / 2
    if side == "right":
        return nx + nw, ny + nh / 2
    if side == "top":
        return nx + nw / 2, ny
    return nx + nw / 2, ny + nh  # bottom


def _ctrl(x, y, side, offset):
    """Bezier control point offset from (x, y) toward a given side."""
    if side == "left":
        return x - offset, y
    if side == "right":
        return x + offset, y
    if side == "top":
        return x, y - offset
    return x, y + offset  # bottom


def _resolve_file_node_url(file_field, url_index):
    """Return (display_stem, url_path) for a canvas file node."""
    stem = os.path.splitext(
        os.path.basename(file_field.replace("\\", "/"))
    )[0]
    url = ""
    if url_index:
        url = (
            url_index.get(slugify(stem))
            or url_index.get(slugify(file_field))
            or ""
        )
        if isinstance(url, dict):
            url = url.get("url_path", "")
    return stem, url


_CANVAS_MEDIA_EXT = frozenset({
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp",
    ".mp4", ".webm", ".mov",
    ".mp3", ".ogg", ".wav", ".flac", ".m4a",
})


def _canvas_direct_media_relpath(file_field, canvas_path):
    """If the node points at an image/audio/video file under VAULT_PATH, return
    its vault-relative path (posix slashes), else None.
    """
    raw = file_field.replace("\\", "/").strip()
    if not raw:
        return None
    try:
        vault_real = os.path.realpath(_config.VAULT_PATH)
    except OSError:
        return None
    candidates = [
        os.path.join(_config.VAULT_PATH, raw),
        os.path.normpath(os.path.join(os.path.dirname(canvas_path), raw)),
    ]
    seen = set()
    for cand in candidates:
        try:
            full = os.path.realpath(cand)
        except OSError:
            continue
        if full in seen:
            continue
        seen.add(full)
        if not full.startswith(vault_real + os.sep):
            continue
        if not os.path.isfile(full):
            continue
        ext = os.path.splitext(full)[1].lower()
        if ext not in _CANVAS_MEDIA_EXT:
            return None
        return os.path.relpath(full, _config.VAULT_PATH).replace("\\", "/")
    return None


def _canvas_embed_media_html(rel_under_vault):
    """HTML for a single vault-relative media file (for file-card preview)."""
    ext = rel_under_vault.rsplit(".", 1)[-1].lower()
    href = _config.vault_attachment_href(rel_under_vault)
    he = _html.escape(href, quote=True)
    if ext in {"mp4", "webm", "mov"}:
        return f'<video src="{he}" controls loading="lazy"></video>'
    if ext in {"mp3", "ogg", "wav", "flac", "m4a"}:
        return f'<audio src="{he}" controls></audio>'
    return f'<img src="{he}" alt="" loading="lazy">'


def render_canvas(
    canvas_path,
    url_index=None,
    post_html_by_url=None,
    post_title_by_url=None,
):
    """Parse a .canvas JSON file and return an HTML string.

    post_html_by_url maps published ``url_path`` to rendered note HTML for
    scrollable in-card previews on file nodes. post_title_by_url overrides
    the card header label when present.
    """
    try:
        with open(canvas_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return f"<p><em>Canvas could not be loaded: {_html.escape(str(exc))}</em></p>"

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    if not nodes:
        return "<p><em>Empty canvas.</em></p>"

    PAD = 60
    min_x = min(n["x"] for n in nodes) - PAD
    min_y = min(n["y"] for n in nodes) - PAD
    max_x = max(n["x"] + n["width"] for n in nodes) + PAD
    max_y = max(n["y"] + n["height"] for n in nodes) + PAD
    total_w = max_x - min_x
    total_h = max_y - min_y

    node_map = {n["id"]: n for n in nodes}
    out = [
        '<div class="canvas-view">',
        '<button class="canvas-fit-btn" title="Fit to view"'
        ' aria-label="Fit to view">&#8861;</button>',
        '<button class="canvas-wide-btn" title="Wide view"'
        ' aria-label="Toggle wide view">&#9974;</button>',
        f'<div class="canvas-stage"'
        f' style="width:{total_w}px;height:{total_h}px">',
    ]

    _marker_ids = {}
    for edge in edges:
        fn = node_map.get(edge.get("fromNode"))
        tn = node_map.get(edge.get("toNode"))
        if not fn or not tn:
            continue
        stroke = CANVAS_COLOR_MAP.get(edge.get("color", ""), "currentColor")
        if edge.get("toEnd", "arrow") == "arrow":
            mk = (stroke, "end")
            if mk not in _marker_ids:
                _marker_ids[mk] = f"cm-{len(_marker_ids)}"
        if edge.get("fromEnd", "none") == "arrow":
            mk = (stroke, "start")
            if mk not in _marker_ids:
                _marker_ids[mk] = f"cm-{len(_marker_ids)}"

    out.append(
        f'<svg class="canvas-edges"'
        f' viewBox="0 0 {total_w} {total_h}"'
        f' aria-hidden="true">'
    )
    out.append("<defs>")
    for (stroke, direction), mid in _marker_ids.items():
        esc = _html.escape(stroke, quote=True)
        if direction == "end":
            out.append(
                f'<marker id="{mid}" viewBox="0 0 10 10" '
                f'markerWidth="10" markerHeight="10" refX="10" refY="5" '
                f'orient="auto" markerUnits="userSpaceOnUse">'
                f'<path d="M0,0 L10,5 L0,10 Z" fill="{esc}" stroke="none" />'
                f"</marker>"
            )
        else:
            out.append(
                f'<marker id="{mid}" viewBox="0 0 10 10" '
                f'markerWidth="10" markerHeight="10" refX="0" refY="5" '
                f'orient="auto-start-reverse" markerUnits="userSpaceOnUse">'
                f'<path d="M10,0 L0,5 L10,10 Z" fill="{esc}" stroke="none" />'
                f"</marker>"
            )
    out.append("</defs>")
    for edge in edges:
        fn = node_map.get(edge.get("fromNode"))
        tn = node_map.get(edge.get("toNode"))
        if not fn or not tn:
            continue
        fs = edge.get("fromSide", "right")
        ts = edge.get("toSide", "left")
        fx, fy = _side_point(fn, fs, min_x, min_y)
        tx_c, ty_c = _side_point(tn, ts, min_x, min_y)
        if fs in ("left", "right"):
            offset = max(_CTRL_MIN, abs(tx_c - fx) * 0.55)
        else:
            offset = max(_CTRL_MIN, abs(ty_c - fy) * 0.55)
        cx1, cy1 = _ctrl(fx, fy, fs, offset)
        cx2, cy2 = _ctrl(tx_c, ty_c, ts, offset)
        stroke = CANVAS_COLOR_MAP.get(edge.get("color", ""), "currentColor")
        esc_stroke = _html.escape(stroke, quote=True)
        has_end = edge.get("toEnd", "arrow") == "arrow"
        has_start = edge.get("fromEnd", "none") == "arrow"
        marker_end_attr = (
            f' marker-end="url(#{_marker_ids[(stroke, "end")]})"'
            if has_end else ""
        )
        marker_start_attr = (
            f' marker-start="url(#{_marker_ids[(stroke, "start")]})"'
            if has_start else ""
        )
        out.append(
            f'<path d="M{fx:.2f},{fy:.2f} '
            f'C{cx1:.2f},{cy1:.2f} {cx2:.2f},{cy2:.2f} {tx_c:.2f},{ty_c:.2f}"'
            f' stroke="{esc_stroke}" fill="none" stroke-width="1.5"'
            f' vector-effect="non-scaling-stroke" opacity="0.7"'
            f'{marker_end_attr}{marker_start_attr} />'
        )
    out.append("</svg>")

    # Edge labels as HTML divs (SVG text distorts with preserveAspectRatio=none)
    for edge in edges:
        fn = node_map.get(edge.get("fromNode"))
        tn = node_map.get(edge.get("toNode"))
        label = edge.get("label", "")
        if not label or not fn or not tn:
            continue
        fs = edge.get("fromSide", "right")
        ts = edge.get("toSide", "left")
        fx, fy = _side_point(fn, fs, min_x, min_y)
        tx_c, ty_c = _side_point(tn, ts, min_x, min_y)
        if fs in ("left", "right"):
            offset = max(_CTRL_MIN, abs(tx_c - fx) * 0.55)
        else:
            offset = max(_CTRL_MIN, abs(ty_c - fy) * 0.55)
        cx1, cy1 = _ctrl(fx, fy, fs, offset)
        cx2, cy2 = _ctrl(tx_c, ty_c, ts, offset)
        mx = 0.125*fx + 0.375*cx1 + 0.375*cx2 + 0.125*tx_c
        my = 0.125*fy + 0.375*cy1 + 0.375*cy2 + 0.125*ty_c
        out.append(
            f'<div class="canvas-edge-label"'
            f' style="left:{mx:.1f}px;top:{my:.1f}px">'
            f'{_html.escape(label)}</div>'
        )

    # Node divs — groups first so they render beneath other nodes
    for node in sorted(nodes, key=lambda n: 0 if n.get("type") == "group" else 1):
        ntype = node.get("type", "text")
        nid = _html.escape(node.get("id", ""))
        x = node["x"] - min_x
        y = node["y"] - min_y
        w = node["width"]
        h = node["height"]
        border = CANVAS_COLOR_MAP.get(node.get("color", ""), "")
        style = f"left:{x}px;top:{y}px;width:{w}px;height:{h}px;"
        if border:
            style += f"border-color:{border};border-width:2px;"

        if ntype == "group":
            label = _html.escape(node.get("label", ""))
            lbl = f'<div class="canvas-group-label">{label}</div>' if label else ""
            group_style = style
            if border:
                group_style += f"background-color:{border}14;"
            out.append(
                f'<div class="canvas-node canvas-group" data-id="{nid}"'
                f' style="{group_style}">{lbl}</div>'
            )

        elif ntype == "file":
            file_field = node.get("file", "")
            stem, url = _resolve_file_node_url(file_field, url_index)
            esc_stem = _html.escape(stem)
            header_label = esc_stem
            if url and post_title_by_url:
                t = post_title_by_url.get(url)
                if t:
                    header_label = _html.escape(t)
            preview = ""
            if url and post_html_by_url:
                preview = post_html_by_url.get(url) or ""
            if not preview:
                rel_m = _canvas_direct_media_relpath(file_field, canvas_path)
                if rel_m:
                    preview = _canvas_embed_media_html(rel_m)
            if preview:
                if url:
                    head = (
                        f'<a href="{_html.escape(url)}" class="canvas-file-link">'
                        f"{header_label}</a>"
                    )
                else:
                    bn = os.path.basename(file_field.replace("\\", "/"))
                    head = (
                        f'<span class="canvas-file-name">'
                        f"{_html.escape(bn)}</span>"
                    )
                out.append(
                    f'<div class="canvas-node canvas-node-file" data-id="{nid}"'
                    f' style="{style}">'
                    f'<div class="canvas-file-card">'
                    f'<div class="canvas-file-header">{head}</div>'
                    f'<div class="canvas-file-preview">{preview}</div>'
                    f"</div></div>"
                )
            else:
                inner = (
                    f'<a href="{_html.escape(url)}" class="canvas-file-link">'
                    f"{header_label}</a>"
                    if url
                    else f'<span class="canvas-file-name">{header_label}</span>'
                )
                out.append(
                    f'<div class="canvas-node canvas-node-file'
                    f' canvas-node-file-only-title" data-id="{nid}"'
                    f' style="{style}">{inner}</div>'
                )

        elif ntype == "link":
            raw = node.get("url", "")
            try:
                domain = _urlparse(raw).netloc or raw
            except Exception:
                domain = raw
            out.append(
                f'<div class="canvas-node canvas-node-link" data-id="{nid}"'
                f' style="{style}">'
                f'<a href="{_html.escape(raw, quote=True)}" class="canvas-ext-link"'
                f' target="_blank" rel="noopener">'
                f'<span class="canvas-link-icon">&#8599;</span>'
                f'<span class="canvas-link-domain">{_html.escape(domain)}</span>'
                f'<span class="canvas-link-url">{_html.escape(raw)}</span>'
                f"</a></div>"
            )

        else:  # text
            raw_text = node.get("text", "")
            content, _ = _render_markdown(
                raw_text, canvas_path, url_index=url_index,
                skip_strip_h1=True,
            )
            out.append(
                f'<div class="canvas-node canvas-node-text" data-id="{nid}"'
                f' style="{style}">'
                f'<div class="canvas-node-content">{content}</div></div>'
            )

    out.append("</div>")  # canvas-stage
    out.append("</div>")  # canvas-view
    return "\n".join(out)
