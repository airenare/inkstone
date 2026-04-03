import os
import re

import markdown

from config import VAULT_PATH, ATTACHMENTS_PATH


# =========================================
# UTILITIES
# =========================================

def slugify(text):
    text = text.strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


# =========================================
# OBSIDIAN LINK PARSER
# =========================================

def convert_links(md, url_index=None):
    """Convert [[Wiki Links]] and [[Title|Display Text]] to markdown links.

    Supports:
      [[Title]]                 → resolved URL
      [[Title|Display]]         → resolved URL with custom display text
      [[Title#Heading]]         → resolved URL + #heading-slug anchor
      [[Title#Heading|Display]]
      [[Title^block-id]]        → resolved URL + #block-id anchor
      [[Title^block-id|Display]]

    url_index: dict of {slugify(title): url_path} built during two-pass loading.
    Falls back to /slugified-title if the title is not found in the index.
    """
    # Capture optional #heading or ^block-id, then optional |display
    pattern = r"\[\[([^|\]#^]+)(?:[#^]([^|\]]+))?(?:\|([^\]]+))?\]\]"

    def repl(match):
        target = match.group(1).strip()
        anchor_text = match.group(2).strip() if match.group(2) else None
        display = (match.group(3) or
                   (f"{target} › {anchor_text}" if anchor_text else target)).strip()
        slug = slugify(target).lower()
        url = url_index.get(slug) if url_index else None
        base = url or ("/" + slug)
        anchor = ("#" + slugify(anchor_text).lower()) if anchor_text else ""
        return f"[{display}]({base}{anchor})"

    return re.sub(pattern, repl, md)


# =========================================
# OBSIDIAN CHECKBOX PARSER
# =========================================

def convert_checkboxes(md):
    lines = md.split("\n")
    out = []
    stack = []

    def close_lists(to_level=0):
        while len(stack) > to_level:
            out.append("</ul>")
            stack.pop()

    for line in lines:
        match = re.match(r'^(\s*)- \[([ xX])\] (.*)', line)

        if match:
            indent, checked, text = match.groups()
            indent = indent.replace("\t", "    ")
            level = len(indent) // 4
            checked_attr = "checked" if checked.lower() == "x" else ""

            while len(stack) < level + 1:
                out.append('<ul class="checkbox-list">')
                stack.append("<ul>")

            close_lists(level + 1)

            out.append(
                f'<li><input type="checkbox" disabled {checked_attr}> {text}</li>'
            )
        else:
            if stack:
                close_lists(0)
            out.append(line)

    close_lists(0)

    return "\n".join(out)


# =========================================
# OBSIDIAN CALLOUT PARSER
# =========================================

def convert_callouts(md):
    lines = md.split("\n")
    out = []

    callout_open = False
    callout_type = ""
    callout_title = ""
    callout_content = []
    collapsed = None  # None = regular div; True = <details>; False = <details open>

    for line in lines:
        if line.lstrip().startswith("> [!"):
            if callout_open:
                out.append(render_callout(
                    callout_type, callout_title, callout_content, collapsed
                ))
                callout_content = []

            callout_open = True
            # Fixed: strip blockquote prefix with regex so title chars are preserved
            header = re.sub(r"^[>\s]+", "", line).strip()
            type_part = header.split("]")[0]
            callout_type = type_part[2:].lower()
            raw_title = header.split("]")[1].strip()
            # Detect Obsidian collapse modifier: [!type]- (collapsed), [!type]+ (expanded)
            if raw_title.startswith("-"):
                collapsed = True
                callout_title = raw_title[1:].strip()
            elif raw_title.startswith("+"):
                collapsed = False
                callout_title = raw_title[1:].strip()
            else:
                collapsed = None
                callout_title = raw_title

        elif callout_open and line.startswith(">"):
            callout_content.append(line[1:].strip())

        else:
            if callout_open:
                out.append(render_callout(
                    callout_type, callout_title, callout_content, collapsed
                ))
                callout_open = False
                callout_content = []

            out.append(line)

    if callout_open:
        out.append(render_callout(
            callout_type, callout_title, callout_content, collapsed
        ))

    return "\n".join(out)


def render_callout(type_, title, content, collapsed=None):
    body = "\n".join(content)
    if collapsed is not None:
        open_attr = "" if collapsed else " open"
        return (
            f'\n<details{open_attr} class="callout callout-{type_}">\n'
            f'<summary class="callout-title">'
            f'<span class="callout-icon"></span>'
            f'<span class="callout-title-text">{title}</span>'
            f'</summary>\n'
            f'<div class="callout-content">\n{body}\n</div>\n'
            f'</details>\n'
        )
    return (
        f'\n<div class="callout callout-{type_}">\n'
        f'<div class="callout-title">'
        f'<span class="callout-icon"></span>'
        f'<span class="callout-title-text">{title}</span>'
        f'</div>\n'
        f'<div class="callout-content">\n{body}\n</div>\n'
        f'</div>\n'
    )


# =========================================
# OBSIDIAN MEDIA PARSER
# =========================================

def convert_media(md, md_path):
    folder = os.path.dirname(md_path)
    pattern = r'!\[\[([^|\]]+)(?:\|([0-9x]+))?\]\]'

    lines = md.split("\n")
    output = []

    gallery = []
    slider = []

    def flush_gallery():
        if not gallery:
            return ""
        if len(gallery) == 1:
            html = gallery[0]
        else:
            html = '<div class="thumb-gallery">' + "".join(gallery) + "</div>"
        gallery.clear()
        return html

    def flush_slider():
        if not slider:
            return ""
        html = '<div class="slider-gallery">'
        html += '<button class="slider-arrow left">&#8249;</button>'
        html += '<div class="slides">'
        for item in slider:
            html += f'<div class="slide">{item}</div>'
        html += "</div>"
        html += '<button class="slider-arrow right">&#8250;</button>'
        html += '<div class="slider-dots"></div>'
        html += "</div>"
        slider.clear()
        return html

    for line in lines:
        matches = re.findall(pattern, line)

        # Slider: multiple embeds on one line separated by spaces
        if len(matches) > 1 and " " in line:
            slider.clear()
            for filename, caption in matches:
                filename = filename.strip()
                full_path = os.path.join(folder, "_attachments", filename)
                if not os.path.exists(full_path):
                    vault_att = os.path.join(VAULT_PATH, "_attachments", filename)
                    if os.path.exists(vault_att):
                        full_path = vault_att
                    elif ATTACHMENTS_PATH:
                        custom_att = os.path.join(ATTACHMENTS_PATH, filename)
                        if os.path.exists(custom_att):
                            full_path = custom_att
                if not os.path.exists(full_path):
                    continue
                rel = os.path.relpath(full_path, VAULT_PATH)
                ext = filename.lower().split(".")[-1]
                if ext in ["mp4", "webm", "mov"]:
                    slider.append(
                        f'<video src="/attachments/{rel}" controls loading="lazy"></video>'
                    )
                elif ext in ["mp3", "ogg", "wav", "flac", "m4a"]:
                    slider.append(
                        f'<audio src="/attachments/{rel}" controls></audio>'
                    )
                else:
                    width_attr = (
                        f' style="max-width:{caption}px"'
                        if caption and caption.isdigit()
                        else ""
                    )
                    slider.append(
                        f'<img src="/attachments/{rel}" alt=""'
                        f'{width_attr} loading="lazy">'
                    )
            output.append(flush_slider())
            continue

        # Single embed on its own line
        elif len(matches) == 1 and line.strip().startswith("![["):
            filename, caption = matches[0]
            filename = filename.strip()
            full_path = os.path.join(folder, "_attachments", filename)
            if not os.path.exists(full_path):
                # Fallback 1: vault root _attachments/
                vault_att = os.path.join(VAULT_PATH, "_attachments", filename)
                if os.path.exists(vault_att):
                    full_path = vault_att
                # Fallback 2: configured ATTACHMENTS_PATH
                elif ATTACHMENTS_PATH:
                    custom_att = os.path.join(ATTACHMENTS_PATH, filename)
                    if os.path.exists(custom_att):
                        full_path = custom_att
            if not os.path.exists(full_path):
                output.append(f"<em>Missing media: {filename}</em>")
                continue
            rel = os.path.relpath(full_path, VAULT_PATH)
            ext = filename.lower().split(".")[-1]
            if ext in ["mp4", "webm", "mov"]:
                gallery.append(
                    f'<video src="/attachments/{rel}" controls loading="lazy"></video>'
                )
            elif ext in ["mp3", "ogg", "wav", "flac", "m4a"]:
                gallery.append(
                    f'<audio src="/attachments/{rel}" controls></audio>'
                )
            else:
                is_numeric = caption and caption.isdigit()
                width_attr = f' style="max-width:{caption}px"' if is_numeric else ""
                img_caption = "" if is_numeric else caption
                img_tag = (
                    f'<img src="/attachments/{rel}"{width_attr}'
                    f' data-gallery="gallery" data-src="/attachments/{rel}"'
                    f' data-type="image" data-caption="{img_caption}" loading="lazy">'
                )
                if img_caption:
                    gallery.append(
                        f'<figure>{img_tag}'
                        f'<figcaption>{img_caption}</figcaption></figure>'
                    )
                else:
                    gallery.append(img_tag)
            continue

        else:
            if gallery:
                output.append(flush_gallery())
            output.append(line)

    if gallery:
        output.append(flush_gallery())
    if slider:
        output.append(flush_slider())

    return "\n".join(output)


# =========================================
# MARKDOWN PIPELINE
# =========================================

def extract_h1(md):
    """Return the text of the first H1 line in raw markdown, or None."""
    for line in md.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return None


def strip_leading_h1(md):
    """Remove the first H1 line from markdown — the template renders the title."""
    lines = md.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            del lines[i]
            break
    return "\n".join(lines)


def _extract_heading_section(md, heading):
    """Return only the content under a specific heading in a markdown string.

    Extracts text from the matched heading line down to the next heading of
    equal or higher level.  Falls back to the full text if the heading is
    not found.
    """
    lines = md.split("\n")
    heading_key = heading.strip().lower()
    target_level = None
    start_idx = None
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.+)", line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            if (text.lower() == heading_key
                    or slugify(text).lower() == slugify(heading_key).lower()):
                target_level = level
                start_idx = i + 1
                break
    if start_idx is None:
        return md  # heading not found — embed full note
    end_idx = len(lines)
    for i in range(start_idx, len(lines)):
        m = re.match(r"^(#{1,6})\s+", lines[i])
        if m and len(m.group(1)) <= target_level:
            end_idx = i
            break
    return "\n".join(lines[start_idx:end_idx]).strip()


def convert_transclusion(md, dataview_index):
    """Replace ![[Note Title]] with the target note's rendered content.

    Supports ![[Note Title#Heading]] to transclude only the section under a
    specific heading.  Only fires for embeds that were NOT consumed by
    convert_media() (i.e. not resolved to a file in _attachments/).
    Renders the target note's body markdown inline, wrapped in a blockquote-
    style div so it is visually distinct.
    """
    if not dataview_index:
        return md

    # Build a title → filepath map from the dataview index
    title_map = {}
    for filepath, entry in dataview_index.items():
        stem = os.path.splitext(os.path.basename(filepath))[0].lower()
        title_map[stem] = filepath
        # also map by slugified title
        title_map[slugify(entry.get("title", "")).lower()] = filepath

    # Group 1: code spans/blocks (returned unchanged)
    # Group 2: note title
    # Group 3: optional #heading fragment (now captured)
    # Group 4: optional |alias
    pattern = (
        r'(`+[^`]*`+|```[\s\S]*?```)'
        r'|!\[\[([^|\]#]+?)(?:#([^\]|]*))?(?:\|[^\]]*)?\]\]'
    )

    def repl(match):
        if match.group(1) is not None:
            return match.group(1)  # inside code — leave untouched
        target = match.group(2).strip()
        heading_fragment = match.group(3).strip() if match.group(3) else None
        key = target.lower()
        filepath = title_map.get(key) or title_map.get(slugify(target).lower())
        if not filepath:
            return f'<em class="transclusion-missing">Note not found: {target}</em>'
        try:
            with open(filepath, encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            return f'<em class="transclusion-missing">Could not read: {target}</em>'
        _, body = (text.split("---", 2)[1:3] if text.startswith("---")
                   else ("", text))
        body = body.strip()
        # Apply heading filter before rendering
        if heading_fragment:
            body = _extract_heading_section(body, heading_fragment)
        # Render the transclusion body through the pipeline (no recursive
        # transclusion to avoid infinite loops; no dataview_index passed)
        body_md = strip_leading_h1(body)
        body_md = convert_callouts(body_md)
        body_md = convert_checkboxes(body_md)
        body_md = convert_highlights(body_md)
        md_obj = markdown.Markdown(
            extensions=["fenced_code", "tables", "md_in_html", "codehilite",
                        "footnotes"],
            output_format="html5",
        )
        body_html = md_obj.convert(body_md)
        entry = dataview_index[filepath]
        title = entry.get("title", target)
        url = entry.get("url_path", "")
        display_title = (
            f"{title} › {heading_fragment}" if heading_fragment else title
        )
        link = f'<a href="{url}">{display_title}</a>' if url else display_title
        return (
            f'<div class="transclusion">'
            f'<div class="transclusion-title">{link}</div>'
            f'<div class="transclusion-body">{body_html}</div>'
            f'</div>'
        )

    return re.sub(pattern, repl, md)


def convert_block_ids(md):
    """Replace trailing ^block-id markers with anchor spans.

    Obsidian uses `^word` at the end of a paragraph to assign a block ID.
    This converts them to <span id="block-id"></span> so that
    [[Note^block-id]] links have a valid anchor to scroll to.
    """
    return re.sub(
        r" \^([A-Za-z0-9_-]+)\s*$",
        lambda m: f' <span id="{m.group(1).lower()}"></span>',
        md,
        flags=re.MULTILINE,
    )


def convert_highlights(md):
    """Convert ==highlighted text== to <mark> tags."""
    return re.sub(r"==([^=\n]+)==", r"<mark>\1</mark>", md)


def convert_math(md):
    """Protect LaTeX math from the markdown parser.

    $$...$$ block math → <div class="math-block">...</div>
    $...$ inline math  → <span class="math-inline">...</span>

    Conversion happens before markdown.Markdown() runs so that
    underscores and asterisks inside math expressions are not
    interpreted as markdown emphasis.
    """
    # Block math first (must come before inline to avoid partial matches)
    md = re.sub(
        r"\$\$(.+?)\$\$",
        lambda m: f'<div class="math-block">{m.group(1)}</div>',
        md,
        flags=re.DOTALL,
    )
    # Inline math — avoid matching empty $$ (already handled above)
    md = re.sub(
        r"\$([^\$\n]+)\$",
        lambda m: f'<span class="math-inline">{m.group(1)}</span>',
        md,
    )
    return md


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


# =========================================
# DATAVIEW QUERY ENGINE
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
    """Dot-separated field access into a nested dict."""
    val = ctx
    for part in field.split("."):
        if isinstance(val, dict):
            val = val.get(part, "")
        else:
            val = ""
    return val if val is not None else ""


def _eval_dv_expr(expr, ctx):
    """Evaluate a Dataview column expression against a post context dict."""
    expr = expr.strip()
    if not expr:
        return ""

    # String literal: only if the ENTIRE expression is a single quoted string
    # (i.e. the first quote closes at the very last character)
    if expr[0] in ('"', "'"):
        q = expr[0]
        close = expr.find(q, 1)
        if close == len(expr) - 1:
            return expr[1:-1]
        # Not a pure literal — fall through to concat / function checks

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


def _eval_dv_condition(condition, ctx):
    """Evaluate a Dataview WHERE condition string."""
    condition = condition.strip()
    if not condition:
        return True

    # AND
    parts = _split_tokens(condition, " & ")
    if len(parts) > 1:
        return all(_eval_dv_condition(p, ctx) for p in parts)

    # OR
    parts = _split_tokens(condition, " | ")
    if len(parts) > 1:
        return any(_eval_dv_condition(p, ctx) for p in parts)

    # !contains(expr, "value")
    m = re.match(r'^!contains\((.+),\s*"([^"]*)"\)$', condition)
    if m:
        val = _eval_dv_expr(m.group(1).strip(), ctx)
        needle = m.group(2).lower()
        if isinstance(val, (list, set)):
            return needle not in [str(v).lower() for v in val]
        return needle not in str(val).lower()

    # contains(expr, "value")
    m = re.match(r'^contains\((.+),\s*"([^"]*)"\)$', condition)
    if m:
        val = _eval_dv_expr(m.group(1).strip(), ctx)
        needle = m.group(2).lower()
        if isinstance(val, (list, set)):
            return needle in [str(v).lower() for v in val]
        return needle in str(val).lower()

    # Parenthesized sub-condition
    if condition.startswith("(") and condition.endswith(")"):
        return _eval_dv_condition(condition[1:-1], ctx)

    import sys
    print(
        f"WARNING: Dataview: unrecognised WHERE condition: {condition!r}",
        file=sys.stderr,
    )
    return False


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
        # LIST [expr] — optional field expression after the keyword
        list_expr = re.sub(r"^LIST\s*", "", lines[0], flags=re.IGNORECASE).strip()
        result["list_expr"] = list_expr
    else:
        col_lines = []
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


def _execute_dv_query(parsed, dataview_index):
    """Execute a parsed Dataview TABLE query and return an HTML string."""
    # --- Filter by FROM ---
    posts = list(dataview_index.values())
    from_clause = (parsed.get("from") or "").strip()
    if from_clause:
        m = re.match(r"^#(.+)$", from_clause)
        if m:
            tag = m.group(1).lower()
            posts = [p for p in posts if tag in p.get("tags", set())]

    # --- Build context dicts ---
    contexts = []
    for p in posts:
        ctx = {}
        for k, v in (p.get("metadata") or {}).items():
            ctx[k] = v
            ctx[k.lower()] = v
        ctx["tags"] = p.get("tags", set())
        ctx["file"] = p.get("file", {})
        contexts.append(ctx)

    # --- Apply WHERE ---
    where = (parsed.get("where") or "").strip()
    if where:
        contexts = [c for c in contexts if _eval_dv_condition(where, c)]

    group_by = (parsed.get("group_by") or "").strip()
    sort_str = (parsed.get("sort") or "").strip()

    if group_by:
        # Group rows
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

        # Sort groups
        if sort_str:
            for field, reverse in reversed(_parse_sort_clause(sort_str)):
                group_contexts.sort(
                    key=lambda gc, f=field: _to_str(_eval_dv_expr(f, gc)),
                    reverse=reverse,
                )
        contexts = group_contexts
    else:
        # Sort rows
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
            # Grouped list: <h4> per group, <ul> per group's rows
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
        # Flattened GROUP BY: heading per group, table per group
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


def convert_dataview(md, dataview_index):
    """Replace ```dataview ... ``` fenced blocks with rendered HTML tables."""
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

    Example: `= this.title` → the note's title value.
    `this.field` is an alias for the top-level field name.
    """
    # Skip code spans that don't start with `= `
    pattern = r'`= ([^`]+)`'

    def repl(match):
        expr = match.group(1).strip()
        # `this.field` → field
        expr = re.sub(r"^this\.", "", expr)
        try:
            val = _eval_dv_expr(expr, note_ctx)
            return f'<span class="dv-inline">{_to_str(val)}</span>'
        except Exception:
            return f'<span class="dv-inline dv-inline-error">{expr}</span>'

    return re.sub(pattern, repl, md)
