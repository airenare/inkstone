"""Server-side renderer for Obsidian .base database views.

Parses .base YAML, evaluates filters against the dataview_index,
and renders type:table (and fallback) views as HTML.
"""
import os
import re
import sys

import yaml

BASE_PUBLISH_SUFFIX = "__website"
BASE_FEATURED_SUFFIX = "__featured"


# =========================================
# PARSING
# =========================================

def parse_base_config(text, filepath="<unknown>"):
    """Parse a .base file's YAML content into a config dict."""
    try:
        config = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        print(f"WARNING: {filepath} — YAML parse error: {exc}", file=sys.stderr)
        config = {}
    return config if isinstance(config, dict) else {}


def base_filename_publish_meta(filename):
    """Parse ``*.base`` filename markers for publish/featured/title.

    Supports case-insensitive suffix markers before ``.base``:
    - ``__website``  -> publish
    - ``__featured`` -> featured
    Markers can be combined in any order, e.g.:
    ``All Posts__website__featured.base``.
    """
    if not filename.endswith(".base"):
        return False, False, "", ""
    raw_stem = filename[:-5]
    stem = raw_stem
    low = stem.lower()
    publish = False
    featured = False
    changed = True
    while changed:
        changed = False
        if low.endswith(BASE_PUBLISH_SUFFIX):
            publish = True
            stem = stem[: -len(BASE_PUBLISH_SUFFIX)].rstrip()
            low = stem.lower()
            changed = True
        if low.endswith(BASE_FEATURED_SUFFIX):
            featured = True
            stem = stem[: -len(BASE_FEATURED_SUFFIX)].rstrip()
            low = stem.lower()
            changed = True
    display_stem = stem if stem else raw_stem
    return publish, featured, display_stem, raw_stem


# =========================================
# FIELD ACCESS
# =========================================

def _get_note_field(note_ctx, field):
    """Resolve a field name from a note's dataview context dict.

    Supports file.*, note.*, and direct frontmatter property names.
    """
    field = field.strip()

    if field.startswith("file."):
        sub = field[5:]
        file_ctx = note_ctx.get("file") or {}
        if sub == "tags":
            return note_ctx.get("tags") or []
        if sub == "basename":
            fp = note_ctx.get("filepath") or ""
            return os.path.basename(fp).rsplit(".", 1)[0]
        if sub == "ext":
            fp = note_ctx.get("filepath") or ""
            parts = fp.rsplit(".", 1)
            return ("." + parts[-1]) if len(parts) == 2 else ""
        if sub in ("name", "path", "folder", "ctime", "mtime", "link"):
            return file_ctx.get(sub, "")
        if sub == "size":
            fp = note_ctx.get("filepath") or ""
            try:
                return os.path.getsize(fp)
            except OSError:
                return 0
        return ""

    if field.startswith("note."):
        prop = field[5:]
        return (note_ctx.get("metadata") or {}).get(prop, "")

    # Direct property access: frontmatter first, then file context
    meta = note_ctx.get("metadata") or {}
    if field in meta:
        return meta[field]
    return (note_ctx.get("file") or {}).get(field, "")


# =========================================
# FILTER EVALUATION
# =========================================

def _eval_filter_expr(expr_str, note_ctx):
    """Evaluate one Bases filter expression string against a note context."""
    expr_str = expr_str.strip()

    # file.hasTag("x") / file.hasTag('x')
    m = re.match(r'^file\.hasTag\(["\'](.+)["\']\)$', expr_str, re.IGNORECASE)
    if m:
        tag = m.group(1).lower()
        return tag in [t.lower() for t in (note_ctx.get("tags") or [])]

    # file.inFolder("folder/") / file.inFolder('folder/')
    m = re.match(r'^file\.inFolder\(["\'](.+)["\']\)$', expr_str, re.IGNORECASE)
    if m:
        target = m.group(1).rstrip("/").lower()
        note_folder = ((note_ctx.get("file") or {}).get("folder") or "").lower()
        # Direct match: dv_folder is relative to VAULT_PATH
        if note_folder == target or note_folder.startswith(target + "/"):
            return True
        # Vault-sub-root match: Obsidian writes paths relative to its own
        # vault root, which may be a parent of VAULT_PATH. Check whether
        # note_folder (or a prefix of it) appears as a path suffix of target.
        # e.g. target="inkstone_docs/writing", note_folder="writing" → match
        # e.g. target="inkstone_docs/writing", note_folder="writing/sub" → match
        if note_folder:
            parts = note_folder.split("/")
            for i in range(len(parts), 0, -1):
                seg = "/".join(parts[:i])
                if target == seg or target.endswith("/" + seg):
                    return True
        return False

    # file.hasLink("note") — not implementable without a link graph; pass through
    if re.match(r'^file\.hasLink\(', expr_str, re.IGNORECASE):
        return True

    # <field>.contains("value") or <field>.contains('value')
    m = re.match(
        r'^([A-Za-z_][\w.]*)\.contains\((.+)\)$', expr_str, re.IGNORECASE
    )
    if m:
        field = m.group(1)
        raw_val = m.group(2).strip()
        lhs = _get_note_field(note_ctx, field)
        if ((raw_val.startswith('"') and raw_val.endswith('"')) or
                (raw_val.startswith("'") and raw_val.endswith("'"))):
            rhs = raw_val[1:-1]
        else:
            rhs = raw_val
        if isinstance(lhs, list):
            rhs_low = str(rhs).lower()
            return any(str(v).lower() == rhs_low for v in lhs)
        lhs_str = str(lhs or "")
        return str(rhs).lower() in lhs_str.lower()

    # Comparison: field OP value  (== != >= <= > <)
    m = re.match(
        r'^([A-Za-z_][\w.]*)\s*(==|!=|>=|<=|>|<)\s*(.+)$', expr_str
    )
    if m:
        field, op, raw_val = m.group(1), m.group(2), m.group(3).strip()
        lhs = _get_note_field(note_ctx, field)

        if ((raw_val.startswith('"') and raw_val.endswith('"')) or
                (raw_val.startswith("'") and raw_val.endswith("'"))):
            rhs = raw_val[1:-1]
            lhs = str(lhs) if lhs is not None else ""
        elif raw_val.lower() == "true":
            rhs = True
        elif raw_val.lower() == "false":
            rhs = False
        else:
            try:
                rhs = float(raw_val)
                lhs = float(lhs) if lhs is not None else 0.0
            except (ValueError, TypeError):
                rhs = raw_val
                lhs = str(lhs) if lhs is not None else ""

        try:
            if op == "==": return lhs == rhs
            if op == "!=": return lhs != rhs
            if op == ">":  return lhs > rhs
            if op == "<":  return lhs < rhs
            if op == ">=": return lhs >= rhs
            if op == "<=": return lhs <= rhs
        except TypeError:
            return False

    return True  # unknown expression: don't filter out


def eval_base_filter(filter_node, note_ctx):
    """Recursively evaluate a Bases filter node (str | list | dict)."""
    if filter_node is None:
        return True
    if isinstance(filter_node, str):
        return _eval_filter_expr(filter_node, note_ctx)
    if isinstance(filter_node, list):
        # Bare list = implicit AND
        return all(eval_base_filter(item, note_ctx) for item in filter_node)
    if isinstance(filter_node, dict):
        if "and" in filter_node:
            return all(eval_base_filter(i, note_ctx) for i in filter_node["and"])
        if "or" in filter_node:
            return any(eval_base_filter(i, note_ctx) for i in filter_node["or"])
        if "not" in filter_node:
            return not eval_base_filter(filter_node["not"], note_ctx)
    return True


# =========================================
# QUERY
# =========================================

def query_base(base_config, dataview_index):
    """Apply global filters and return matching note contexts."""
    global_filters = base_config.get("filters")
    results = []
    for filepath, note_ctx in dataview_index.items():
        if not filepath.endswith(".md"):
            continue
        if global_filters and not eval_base_filter(global_filters, note_ctx):
            continue
        results.append(note_ctx)
    return results


# =========================================
# RENDERING
# =========================================

_SKIP_COLS = frozenset({
    "website", "type", "slug", "banner", "banner_x", "banner_y",
    "menu_order", "priority", "featured", "summary",
})


def _col_label(prop_name, properties_config):
    cfg = (properties_config or {}).get(prop_name) or {}
    if isinstance(cfg, dict):
        dn = cfg.get("displayName")
        if dn:
            return str(dn)
    return prop_name.replace("_", " ").replace(".", " ").title()


def _render_cell(val):
    from datetime import date as date_type, datetime as datetime_type
    if val is None or val == "":
        return ""
    if isinstance(val, bool):
        return "✓" if val else "✗"
    if isinstance(val, datetime_type):
        return val.strftime("%Y-%m-%d")
    if isinstance(val, date_type):
        return val.strftime("%Y-%m-%d")
    if isinstance(val, list):
        return ", ".join(_render_cell(v) for v in val if v is not None and v != "")
    return str(val)


def _sort_key(val):
    if val is None:
        return (1, "")
    from datetime import date as date_type, datetime as datetime_type
    if isinstance(val, (date_type, datetime_type)):
        return (0, val.isoformat())
    try:
        return (0, float(val))
    except (ValueError, TypeError):
        return (0, str(val).lower())


def render_base_view(base_config, dataview_index):
    """Execute a .base query and render the first view as HTML.

    Returns an HTML string ready to embed in post.html's {{ post.html }}.
    """
    views = base_config.get("views") or []
    view = views[0] if views else {}

    view_type = (view.get("type") or "table").lower()
    view_filters = view.get("filters")
    order = view.get("order") or []
    limit = view.get("limit")
    sort_cfg = view.get("sort") or []
    properties_config = base_config.get("properties") or {}

    rows = query_base(base_config, dataview_index)

    if view_filters:
        rows = [r for r in rows if eval_base_filter(view_filters, r)]

    # Sort
    if sort_cfg:
        for entry in reversed(sort_cfg):
            col = entry.get("column", "")
            rev = str(entry.get("direction", "ASC")).upper() == "DESC"
            rows.sort(key=lambda r: _sort_key(_get_note_field(r, col)), reverse=rev)
    else:
        # Default: newest first, then alphabetical
        rows.sort(key=lambda r: (
            -(_get_note_field(r, "file.ctime").toordinal()
              if hasattr(_get_note_field(r, "file.ctime"), "toordinal") else 0),
            (r.get("title") or "").lower(),
        ))

    if limit:
        try:
            rows = rows[:int(limit)]
        except (ValueError, TypeError):
            pass

    if not rows:
        return '<p class="bases-empty">No notes match this query.</p>'

    # Determine data columns (everything except the title/link column)
    if order:
        columns = [c for c in order if c not in ("file.name", "file.link")]
    else:
        # Auto-detect from metadata keys across all rows
        freq = {}
        for row in rows:
            for key in (row.get("metadata") or {}):
                if key not in _SKIP_COLS:
                    freq[key] = freq.get(key, 0) + 1
        columns = [k for k, _ in sorted(freq.items(), key=lambda x: -x[1])[:5]]

    # Render table (both table and cards fall back to table for now)
    html = '<table class="dataview-table bases-table">\n<thead><tr>\n'
    html += "<th>Note</th>\n"
    for col in columns:
        html += f"<th>{_col_label(col, properties_config)}</th>\n"
    html += "</tr></thead>\n<tbody>\n"

    for row in rows:
        url_path = row.get("url_path") or ""
        title = row.get("title") or ""
        link = (f'<a href="{url_path}">{title}</a>' if url_path else title)
        html += "<tr>\n"
        html += f"<td>{link}</td>\n"
        for col in columns:
            html += f"<td>{_render_cell(_get_note_field(row, col))}</td>\n"
        html += "</tr>\n"

    html += "</tbody>\n</table>"
    return html
