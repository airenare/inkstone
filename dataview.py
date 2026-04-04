"""Server-side Dataview query engine.

Implements a subset of Obsidian's Dataview plugin:
  TABLE / LIST queries with FROM, WHERE, SORT, LIMIT, GROUP BY.

Only converters.py imports from this module.
"""
import re
import sys


# =========================================
# VALUE HELPERS
# =========================================

def _to_str(val):
    """Coerce any value to a display string."""
    from datetime import date as date_type, datetime as datetime_type
    if val is None:
        return ""
    if isinstance(val, datetime_type):
        return val.strftime("%Y-%m-%d")
    if isinstance(val, date_type):
        return val.strftime("%Y-%m-%d")
    if isinstance(val, list):
        return ", ".join(_to_str(v) for v in val if v is not None)
    if isinstance(val, set):
        return ", ".join(sorted(_to_str(v) for v in val))
    return str(val)


def _split_tokens(text, delimiter):
    """Split text by delimiter, skipping occurrences inside parens or quotes."""
    parts = []
    current = []
    depth = 0
    in_quote = False
    quote_char = None
    i = 0
    dlen = len(delimiter)

    while i < len(text):
        ch = text[i]
        if not in_quote and ch in ('"', "'"):
            in_quote = True
            quote_char = ch
            current.append(ch)
        elif in_quote and ch == quote_char:
            in_quote = False
            current.append(ch)
        elif in_quote:
            current.append(ch)
        elif ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif depth == 0 and text[i:i + dlen] == delimiter:
            parts.append("".join(current).strip())
            current = []
            i += dlen - 1
        else:
            current.append(ch)
        i += 1

    if current:
        parts.append("".join(current).strip())
    return [p for p in parts if p]


def _get_nested(ctx, field):
    """Dot-separated field access into a nested dict.

    Checks for a flat key first so that group contexts, which store the
    group-by expression (e.g. "file.folder") as a literal dict key, resolve
    correctly before falling through to nested-path lookup.
    """
    if isinstance(ctx, dict) and field in ctx:
        val = ctx[field]
        return val if val is not None else ""
    val = ctx
    for part in field.split("."):
        if isinstance(val, dict):
            val = val.get(part, "")
        else:
            val = ""
    return val if val is not None else ""


# =========================================
# EXPRESSION EVALUATOR
# =========================================

def _eval_dv_expr(expr, ctx):
    """Evaluate a Dataview column expression against a post context dict."""
    expr = expr.strip()
    if not expr:
        return ""

    # String literal
    if expr[0] in ('"', "'"):
        q = expr[0]
        close = expr.find(q, 1)
        if close == len(expr) - 1:
            return expr[1:-1]

    # String concatenation: expr + expr
    parts = _split_tokens(expr, " + ")
    if len(parts) > 1:
        return "".join(_to_str(_eval_dv_expr(p, ctx)) for p in parts)

    # link(target_expr, text_expr)
    m = re.match(r"^link\((.+)\)$", expr, re.DOTALL)
    if m:
        args = _split_tokens(m.group(1), ", ")
        if len(args) >= 2:
            target = _to_str(_eval_dv_expr(args[0], ctx))
            text = _to_str(_eval_dv_expr(args[1], ctx))
            href_m = re.search(r'href="([^"]+)"', target)
            href = href_m.group(1) if href_m else target
            return f'<a href="{href}">{text}</a>'
        return _to_str(_eval_dv_expr(args[0], ctx)) if args else ""

    # join(list(a, b, ...) [, "sep"])
    m = re.match(r"^join\(list\((.+)\)(?:,\s*\"([^\"]*)\")?\)$", expr, re.DOTALL)
    if m:
        list_args = _split_tokens(m.group(1), ", ")
        sep = m.group(2) if m.group(2) is not None else " · "
        items = [_to_str(_eval_dv_expr(a, ctx)) for a in list_args]
        return sep.join(i for i in items if i)

    # join(field [, "sep"])
    m = re.match(r"^join\(([^,)]+)(?:,\s*\"([^\"]*)\")?\)$", expr)
    if m:
        val = _eval_dv_expr(m.group(1).strip(), ctx)
        sep = m.group(2) if m.group(2) is not None else ", "
        if isinstance(val, list):
            return sep.join(_to_str(v) for v in val if v is not None)
        return _to_str(val)

    # list(a, b, ...)
    m = re.match(r"^list\((.+)\)$", expr, re.DOTALL)
    if m:
        return [_eval_dv_expr(a, ctx) for a in _split_tokens(m.group(1), ", ")]

    # rows.field — gather a field across all grouped rows
    if expr.startswith("rows."):
        field = expr[5:]
        rows = ctx.get("rows", [])
        return [_get_nested(row, field) for row in rows]

    return _get_nested(ctx, expr)


# =========================================
# WHERE CONDITION EVALUATOR
# =========================================

def _eval_dv_condition(condition, ctx):
    """Evaluate a Dataview WHERE condition string."""
    condition = condition.strip()
    if not condition:
        return True

    parts = _split_tokens(condition, " & ")
    if len(parts) > 1:
        return all(_eval_dv_condition(p, ctx) for p in parts)

    parts = _split_tokens(condition, " | ")
    if len(parts) > 1:
        return any(_eval_dv_condition(p, ctx) for p in parts)

    m = re.match(r'^!contains\((.+),\s*"([^"]*)"\)$', condition)
    if m:
        val = _eval_dv_expr(m.group(1).strip(), ctx)
        needle = m.group(2).lower()
        if isinstance(val, (list, set)):
            return needle not in [str(v).lower() for v in val]
        return needle not in str(val).lower()

    m = re.match(r'^contains\((.+),\s*"([^"]*)"\)$', condition)
    if m:
        val = _eval_dv_expr(m.group(1).strip(), ctx)
        needle = m.group(2).lower()
        if isinstance(val, (list, set)):
            return needle in [str(v).lower() for v in val]
        return needle in str(val).lower()

    if condition.startswith("(") and condition.endswith(")"):
        return _eval_dv_condition(condition[1:-1], ctx)

    print(
        f"WARNING: Dataview: unrecognised WHERE condition: {condition!r}",
        file=sys.stderr,
    )
    return False


# =========================================
# SORT / RENDER HELPERS
# =========================================

def _parse_sort_clause(sort_str):
    """Parse 'field DESC, field2 ASC' → [(field, reverse), ...]."""
    if not sort_str:
        return []
    result = []
    for part in _split_tokens(sort_str, ", "):
        tokens = part.strip().split()
        field = tokens[0]
        reverse = len(tokens) > 1 and tokens[1].upper() == "DESC"
        result.append((field, reverse))
    return result


def _render_dv_value(val):
    """Convert a dataview expression result to safe HTML for a table cell."""
    if isinstance(val, list):
        rendered = [_render_dv_value(v) for v in val if v is not None and v != ""]
        return "<br>".join(rendered)

    val = _to_str(val)

    # Obsidian image syntax: ![alt|width](url) → <img>
    val = re.sub(
        r"!\[([^\]]*)\|(\d+)\]\(([^)]+)\)",
        lambda m: (
            f'<img src="{m.group(3)}" '
            f'style="max-height:{m.group(2)}px;width:auto;border-radius:4px">'
        ),
        val,
    )

    return val


# =========================================
# QUERY PARSER
# =========================================

def _parse_dv_query(query_text):
    """Parse a Dataview TABLE or LIST query into a structured dict."""
    lines = [ln.strip() for ln in query_text.strip().split("\n") if ln.strip()]
    if not lines:
        return None
    first_upper = lines[0].upper()
    is_list = first_upper.startswith("LIST")
    if not first_upper.startswith("TABLE") and not is_list:
        return None

    result = {
        "type": "list" if is_list else "table",
        "without_id": "WITHOUT ID" in lines[0].upper(),
        "columns": [],
        "list_expr": "",
        "from": "",
        "where": "",
        "group_by": "",
        "sort": "",
        "limit": "",
    }

    keywords = {"FROM", "WHERE", "GROUP BY", "SORT", "LIMIT", "FLATTEN"}
    i = 1

    if is_list:
        list_expr = re.sub(r"^LIST\s*", "", lines[0], flags=re.IGNORECASE).strip()
        result["list_expr"] = list_expr
    else:
        col_lines = []
        inline_cols = re.sub(
            r"^TABLE\s*(WITHOUT\s+ID\s*)?", "", lines[0], flags=re.IGNORECASE
        ).strip()
        if inline_cols:
            col_lines.append(inline_cols)
        while i < len(lines):
            upper = lines[i].upper()
            if any(upper.startswith(kw) for kw in keywords):
                break
            col_lines.append(lines[i])
            i += 1

        col_text = " ".join(col_lines)
        for part in _split_tokens(col_text, ", "):
            part = part.strip()
            if not part:
                continue
            m = re.match(r"^(.*?)\s+as\s+(.+)$", part, re.IGNORECASE)
            if m:
                result["columns"].append(
                    {"expr": m.group(1).strip(), "label": m.group(2).strip()}
                )
            else:
                result["columns"].append({"expr": part, "label": part})

    while i < len(lines):
        line = lines[i]
        upper = line.upper()
        if upper.startswith("FROM"):
            result["from"] = line[4:].strip()
        elif upper.startswith("WHERE"):
            result["where"] = line[5:].strip()
        elif upper.startswith("GROUP BY"):
            result["group_by"] = line[8:].strip()
        elif upper.startswith("SORT"):
            result["sort"] = line[4:].strip()
        elif upper.startswith("LIMIT"):
            result["limit"] = line[5:].strip()
        i += 1

    return result


# =========================================
# QUERY EXECUTOR
# =========================================

def _execute_dv_query(parsed, dataview_index):
    """Execute a parsed Dataview TABLE or LIST query and return an HTML string."""
    # --- Filter by FROM ---
    posts = list(dataview_index.values())
    from_clause = (parsed.get("from") or "").strip()
    if from_clause:
        m = re.match(r"^#(.+)$", from_clause)
        if m:
            tag = m.group(1).lower()
            posts = [p for p in posts if tag in p.get("tags", [])]

    # --- Build context dicts ---
    contexts = []
    for p in posts:
        ctx = {}
        for k, v in (p.get("metadata") or {}).items():
            ctx[k] = v
            ctx[k.lower()] = v
        ctx["tags"] = p.get("tags", [])
        ctx["section"] = p.get("section", "")
        ctx["file"] = p.get("file", {})
        contexts.append(ctx)

    # --- Apply WHERE ---
    where = (parsed.get("where") or "").strip()
    if where:
        contexts = [c for c in contexts if _eval_dv_condition(where, c)]

    group_by = (parsed.get("group_by") or "").strip()
    sort_str = (parsed.get("sort") or "").strip()

    if group_by:
        groups: dict = {}
        group_order: list = []
        for ctx in contexts:
            key = _to_str(_eval_dv_expr(group_by, ctx))
            if key not in groups:
                groups[key] = []
                group_order.append(key)
            groups[key].append(ctx)

        group_contexts = [
            {group_by: key, "rows": groups[key], "file": {}}
            for key in group_order
        ]

        if sort_str:
            for field, reverse in reversed(_parse_sort_clause(sort_str)):
                group_contexts.sort(
                    key=lambda gc, f=field: _to_str(_eval_dv_expr(f, gc)),
                    reverse=reverse,
                )
        contexts = group_contexts
    else:
        if sort_str:
            for field, reverse in reversed(_parse_sort_clause(sort_str)):
                contexts.sort(
                    key=lambda ctx, f=field: _to_str(_eval_dv_expr(f, ctx)),
                    reverse=reverse,
                )

    # --- Apply LIMIT ---
    limit_str = (parsed.get("limit") or "").strip()
    if limit_str:
        try:
            contexts = contexts[:int(limit_str)]
        except ValueError:
            pass

    if not contexts:
        return '<p class="dataview-empty">No results.</p>'

    # --- LIST rendering ---
    if parsed.get("type") == "list":
        list_expr = (parsed.get("list_expr") or "").strip()
        group_by = (parsed.get("group_by") or "").strip()
        if group_by:
            html = '<div class="dataview dataview-list">\n'
            for ctx in contexts:
                group_label = _to_str(_eval_dv_expr(group_by, ctx))
                html += f'<h4 class="dv-group-heading">{group_label}</h4>\n<ul>\n'
                for row in ctx.get("rows", []):
                    link = _render_dv_value(row.get("file", {}).get("link", ""))
                    extra = (
                        f' — {_render_dv_value(_eval_dv_expr(list_expr, row))}'
                        if list_expr else ""
                    )
                    html += f'<li>{link}{extra}</li>\n'
                html += "</ul>\n"
            html += "</div>"
        else:
            html = '<ul class="dataview dataview-list">\n'
            for ctx in contexts:
                link = _render_dv_value(ctx.get("file", {}).get("link", ""))
                extra = (
                    f' — {_render_dv_value(_eval_dv_expr(list_expr, ctx))}'
                    if list_expr else ""
                )
                html += f'<li>{link}{extra}</li>\n'
            html += "</ul>"
        return html

    # --- TABLE rendering ---
    columns = parsed.get("columns") or []
    group_by = (parsed.get("group_by") or "").strip()

    if group_by:
        uses_rows = any(col["expr"].startswith("rows.") for col in columns)
        if uses_rows:
            # Obsidian-native: one row per group, rows.field collects values
            html = '<table class="dataview-table">\n<thead><tr>\n'
            for col in columns:
                html += f'<th>{col["label"]}</th>\n'
            html += "</tr></thead>\n<tbody>\n"
            for ctx in contexts:
                html += "<tr>\n"
                for col in columns:
                    val = _eval_dv_expr(col["expr"], ctx)
                    html += f"<td>{_render_dv_value(val)}</td>\n"
                html += "</tr>\n"
            html += "</tbody>\n</table>\n"
        else:
            # Flattened: heading per group, sub-table of rows
            html = '<div class="dataview dataview-grouped">\n'
            for ctx in contexts:
                group_label = _to_str(_eval_dv_expr(group_by, ctx))
                html += f'<h4 class="dv-group-heading">{group_label}</h4>\n'
                html += '<table class="dataview-table">\n<thead><tr>\n'
                for col in columns:
                    html += f'<th>{col["label"]}</th>\n'
                html += "</tr></thead>\n<tbody>\n"
                for row in ctx.get("rows", []):
                    html += "<tr>\n"
                    for col in columns:
                        val = _eval_dv_expr(col["expr"], row)
                        html += f"<td>{_render_dv_value(val)}</td>\n"
                    html += "</tr>\n"
                html += "</tbody>\n</table>\n"
            html += "</div>"
        return html

    html = '<table class="dataview-table">\n<thead><tr>\n'
    for col in columns:
        html += f'<th>{col["label"]}</th>\n'
    html += "</tr></thead>\n<tbody>\n"
    for ctx in contexts:
        html += "<tr>\n"
        for col in columns:
            val = _eval_dv_expr(col["expr"], ctx)
            html += f"<td>{_render_dv_value(val)}</td>\n"
        html += "</tr>\n"
    html += "</tbody>\n</table>"
    return html


# =========================================
# MARKDOWN CONVERTERS (called by pipeline)
# =========================================

def convert_dataview(md, dataview_index):
    """Replace ```dataview ... ``` fenced blocks with rendered HTML."""
    pattern = re.compile(r"```dataview\n(.*?)\n```", re.DOTALL | re.IGNORECASE)

    def replace_block(match):
        parsed = _parse_dv_query(match.group(1))
        if not parsed:
            return '<div class="dataview-error">Could not parse query.</div>'
        try:
            table_html = _execute_dv_query(parsed, dataview_index)
            return f'<div class="dataview">\n{table_html}\n</div>'
        except Exception as e:
            return f'<div class="dataview-error">Dataview error: {e}</div>'

    return pattern.sub(replace_block, md)


def convert_dataview_inline(md, note_ctx):
    """Replace `= expr` inline queries with evaluated values.

    note_ctx is a dict of the current note's frontmatter fields plus
    special keys: file.name, file.link, file.ctime, tags.
    `this.field` is an alias for the top-level field name.
    """
    # Skip multi-backtick code spans; only match single-backtick `= expr`
    pattern = r'(``+[^`].*?``+)|`= ([^`]+)`'

    def repl(match):
        if match.group(1) is not None:
            return match.group(1)  # multi-backtick code span — leave untouched
        expr = match.group(2).strip()
        expr = re.sub(r"^this\.", "", expr)
        try:
            val = _eval_dv_expr(expr, note_ctx)
            return f'<span class="dv-inline">{_to_str(val)}</span>'
        except Exception:
            return f'<span class="dv-inline dv-inline-error">{expr}</span>'

    return re.sub(pattern, repl, md)
