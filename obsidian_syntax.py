"""Obsidian-specific markdown converters.

All functions that understand Obsidian's extended syntax live here:
wiki-links, embeds, callouts, checkboxes, highlights, math, block IDs,
transclusion, and the slug utility.  converters.py imports from this
module and wires them into the render_markdown() pipeline.
"""
import os
import re

import markdown
from unidecode import unidecode

from config import ATTACHMENTS_PATH, VAULT_PATH, vault_attachment_href


# =========================================
# SLUG UTILITY
# =========================================

def slugify(text):
    text = unidecode(text.strip()).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


# =========================================
# MARKDOWN UTILITIES
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
    Skips content inside fenced code blocks and inline code spans.
    """
    _link_re = re.compile(
        r"\[\[([^|\]#^]+)(?:[#^]([^|\]]+))?(?:\|([^\]]+))?\]\]"
    )

    # Combined: HTML code elements (skip) | backtick spans (skip) | wiki-links.
    # convert_transclusion runs before this and may insert <code>...</code> HTML;
    # those must be skipped so [[...]] inside rendered code blocks isn't converted.
    # The backtick branch uses a backreference so ` ``` ` isn't misread as a span.
    _combined = re.compile(
        r"(<code>[\s\S]*?</code>)"
        r"|(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\2(?!`)"
        r"|\[\[([^|\]#^]+)(?:[#^]([^|\]]+))?(?:\|([^\]]+))?\]\]"
    )

    def repl(match):
        if match.group(1) is not None:  # HTML code element — leave untouched
            return match.group(0)
        if match.group(2) is not None:  # backtick span — leave untouched
            return match.group(0)
        target = match.group(3).strip()
        anchor_text = match.group(4).strip() if match.group(4) else None
        display = (match.group(5) or
                   (f"{target} › {anchor_text}" if anchor_text else target)).strip()
        slug = slugify(target).lower()
        url = url_index.get(slug) if url_index else None
        base = url or ("/" + slug)
        anchor = ("#" + slugify(anchor_text).lower()) if anchor_text else ""
        return f"[{display}]({base}{anchor})"

    return _combined.sub(repl, md)


# =========================================
# OBSIDIAN CHECKBOX PARSER
# =========================================

def convert_checkboxes(md):
    lines = md.split("\n")
    out = []
    stack = []
    fence_marker = None
    _fence_open = re.compile(r"^(`{3,}|~{3,})")

    # Detect the indent unit from the smallest non-zero indent present
    indent_sizes = []
    for ln in lines:
        m2 = re.match(r'^(\s+)- \[([ xX])\]', ln)
        if m2:
            size = len(m2.group(1).replace("\t", "    "))
            if size > 0:
                indent_sizes.append(size)
    indent_unit = min(indent_sizes) if indent_sizes else 4

    def close_lists(to_level=0):
        while len(stack) > to_level:
            out.append("</ul>")
            stack.pop()

    for line in lines:
        # Pass fenced code blocks through untouched
        if fence_marker is None:
            m = _fence_open.match(line)
            if m:
                fence_marker = m.group(1)
                if stack:
                    close_lists(0)
                out.append(line)
                continue
        else:
            out.append(line)
            if re.match(
                r"^" + re.escape(fence_marker) + r"`*~*\s*$", line
            ):
                fence_marker = None
            continue

        match = re.match(r'^(\s*)- \[([ xX])\] (.*)', line)

        if match:
            indent, checked, text = match.groups()
            indent = indent.replace("\t", "    ")
            level = len(indent) // indent_unit
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
    fence_marker = None
    _fence_open = re.compile(r"^(`{3,}|~{3,})")

    for line in lines:
        # Pass fenced code blocks through untouched
        if fence_marker is None:
            m = _fence_open.match(line)
            if m:
                fence_marker = m.group(1)
                if callout_open:
                    out.append(render_callout(
                        callout_type, callout_title, callout_content, collapsed
                    ))
                    callout_open = False
                    callout_content = []
                out.append(line)
                continue
        else:
            out.append(line)
            if re.match(
                r"^" + re.escape(fence_marker) + r"`*~*\s*$", line
            ):
                fence_marker = None
            continue

        if line.lstrip().startswith("> [!"):
            if callout_open:
                out.append(render_callout(
                    callout_type, callout_title, callout_content, collapsed
                ))
                callout_content = []

            callout_open = True
            header = re.sub(r"^[>\s]+", "", line).strip()
            type_part = header.split("]")[0]
            callout_type = type_part[2:].lower()
            raw_title = header.split("]")[1].strip()
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
            f'\n<details{open_attr} class="callout callout-{type_}" markdown="1">\n'
            f'<summary class="callout-title">'
            f'<span class="callout-icon"></span>'
            f'<span class="callout-title-text">{title}</span>'
            f'</summary>\n'
            f'<div class="callout-content" markdown="1">\n{body}\n</div>\n'
            f'</details>\n'
        )
    return (
        f'\n<div class="callout callout-{type_}" markdown="1">\n'
        f'<div class="callout-title">'
        f'<span class="callout-icon"></span>'
        f'<span class="callout-title-text">{title}</span>'
        f'</div>\n'
        f'<div class="callout-content" markdown="1">\n{body}\n</div>\n'
        f'</div>\n'
    )


# =========================================
# OBSIDIAN MEDIA PARSER
# =========================================

_MEDIA_EXTS = {
    "jpg", "jpeg", "png", "gif", "webp", "svg", "bmp",
    "mp4", "webm", "mov",
    "mp3", "ogg", "wav", "flac", "m4a",
}
_FENCE_RE = re.compile(r"^(`{3,}|~{3,})")


def _resolve_attachment(filename, folder):
    """Return full path to attachment or None if not found anywhere."""
    for base in (
        os.path.join(folder, "_attachments"),
        os.path.join(VAULT_PATH, "_attachments"),
        ATTACHMENTS_PATH or "",
    ):
        if not base:
            continue
        p = os.path.join(base, filename)
        if os.path.exists(p):
            return p
    return None


def _parse_caption(cap):
    """Parse ![[file|...]] pipe arg into (inline, float_side, width, caption).

    float_side is 'left', 'right', or None. inline and float_side are
    mutually exclusive; if 'inline' appears, float_side stays None.
    """
    if not cap:
        return False, None, None, ""
    text = cap.strip()

    is_inline = text == "inline" or text.startswith("inline ")
    if is_inline:
        text = text[len("inline"):].strip()

    float_side = None
    if not is_inline:
        if text == "left" or text.startswith("left "):
            float_side = "left"
            text = text[len("left"):].strip()
        elif text == "right" or text.startswith("right "):
            float_side = "right"
            text = text[len("right"):].strip()

    parts = text.split(None, 1)
    width = None
    if parts and parts[0].isdigit():
        width = parts[0]
        text = parts[1] if len(parts) > 1 else ""
    elif not is_inline and float_side is None and text.isdigit():
        width = text
        text = ""

    return is_inline, float_side, width, text


def convert_media(md, md_path):
    folder = os.path.dirname(md_path)
    pattern = r'!\[\[([^|\]]+)(?:\|([^\]]+))?\]\]'
    vault_real = os.path.realpath(VAULT_PATH)

    lines = md.split("\n")
    output = []
    gallery = []
    slider = []
    fence_marker = None

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
        # Fence tracking — skip content inside code blocks
        m = _FENCE_RE.match(line)
        if m:
            if fence_marker is None:
                fence_marker = m.group(1)
            elif line.startswith(fence_marker):
                fence_marker = None
            if gallery:
                output.append(flush_gallery())
            output.append(line)
            continue
        if fence_marker is not None:
            if gallery:
                output.append(flush_gallery())
            output.append(line)
            continue

        matches = re.findall(pattern, line)

        # Slider: multiple embeds on one line separated by spaces
        if len(matches) > 1 and " " in line:
            slider.clear()
            for filename, caption in matches:
                filename = filename.strip()
                full_path = _resolve_attachment(filename, folder)
                if not full_path:
                    continue
                if not os.path.realpath(full_path).startswith(
                    vault_real + os.sep
                ):
                    continue
                rel = os.path.relpath(full_path, VAULT_PATH)
                href = vault_attachment_href(rel)
                ext = filename.lower().rsplit(".", 1)[-1]
                if ext in {"mp4", "webm", "mov"}:
                    slider.append(
                        f'<video src="{href}" controls loading="lazy"></video>'
                    )
                elif ext in {"mp3", "ogg", "wav", "flac", "m4a"}:
                    slider.append(
                        f'<audio src="{href}" controls></audio>'
                    )
                else:
                    width_attr = (
                        f' style="max-width:{caption}px"'
                        if caption and caption.isdigit()
                        else ""
                    )
                    slider.append(
                        f'<img src="{href}" alt=""'
                        f'{width_attr} loading="lazy">'
                    )
            output.append(flush_slider())
            continue

        # Single embed on its own line
        elif len(matches) == 1 and line.strip().startswith("![["):
            filename, caption = matches[0]
            filename = filename.strip()
            full_path = _resolve_attachment(filename, folder)
            if not full_path:
                # Not a media file — leave for convert_transclusion if no ext
                ext_guess = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
                if ext_guess in _MEDIA_EXTS:
                    output.append(f"<em>Missing media: {filename}</em>")
                else:
                    if gallery:
                        output.append(flush_gallery())
                    output.append(line)
                continue
            if not os.path.realpath(full_path).startswith(vault_real + os.sep):
                output.append(f"<em>Missing media: {filename}</em>")
                continue
            rel = os.path.relpath(full_path, VAULT_PATH)
            href = vault_attachment_href(rel)
            ext = filename.lower().rsplit(".", 1)[-1]
            if ext in {"mp4", "webm", "mov"}:
                gallery.append(
                    f'<video src="{href}" controls loading="lazy"></video>'
                )
            elif ext in {"mp3", "ogg", "wav", "flac", "m4a"}:
                gallery.append(
                    f'<audio src="{href}" controls></audio>'
                )
            else:
                is_inline, float_side, width, img_caption = (
                    _parse_caption(caption)
                )
                width_attr = f' style="max-width:{width}px"' if width else ""
                if float_side:
                    if gallery:
                        output.append(flush_gallery())
                    img_tag = (
                        f'<img src="{href}" alt="{img_caption}"'
                        f'{width_attr} loading="lazy">'
                    )
                    css_class = f"figure-{float_side}"
                    if img_caption:
                        output.append(
                            f'<figure class="{css_class}">{img_tag}'
                            f'<figcaption>{img_caption}</figcaption></figure>'
                        )
                    else:
                        output.append(
                            f'<figure class="{css_class}">{img_tag}</figure>'
                        )
                elif is_inline:
                    if gallery:
                        output.append(flush_gallery())
                    img_tag = (
                        f'<img src="{href}"{width_attr}'
                        f' loading="lazy">'
                    )
                    if img_caption:
                        output.append(
                            f'<figure class="inline-figure">{img_tag}'
                            f'<figcaption>{img_caption}</figcaption></figure>'
                        )
                    else:
                        output.append(
                            f'<figure class="inline-figure">{img_tag}</figure>'
                        )
                else:
                    img_tag = (
                        f'<img src="{href}"{width_attr}'
                        f' data-gallery="gallery" data-src="{href}"'
                        f' data-type="image" data-caption="{img_caption}"'
                        f' loading="lazy">'
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
# PARTIAL TRANSCLUSION HELPER
# =========================================

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


# =========================================
# NOTE TRANSCLUSION
# =========================================

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
        title_map[slugify(entry.get("title", "")).lower()] = filepath

    # Group 1: code spans/blocks (returned unchanged)
    # Group 2: note title; Group 3: optional #heading; Group 4: optional |alias
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
        vault_real = os.path.realpath(VAULT_PATH)
        if not os.path.realpath(filepath).startswith(vault_real + os.sep):
            return f'<em class="transclusion-missing">Note not found: {target}</em>'
        try:
            with open(filepath, encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            return f'<em class="transclusion-missing">Could not read: {target}</em>'
        _, body = (text.split("---", 2)[1:3] if text.startswith("---")
                   else ("", text))
        body = body.strip()
        if heading_fragment:
            body = _extract_heading_section(body, heading_fragment)
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


# =========================================
# BLOCK IDs / HIGHLIGHTS / MATH
# =========================================

def convert_block_ids(md):
    """Replace trailing ^block-id markers with anchor spans, skipping code blocks."""
    _block_id_re = re.compile(r" \^([A-Za-z0-9_-]+)\s*$")
    fence_marker = None
    lines = md.split("\n")
    out = []
    for line in lines:
        m = _FENCE_RE.match(line)
        if m:
            if fence_marker is None:
                fence_marker = m.group(1)
            elif line.startswith(fence_marker):
                fence_marker = None
            out.append(line)
            continue
        if fence_marker is None:
            line = _block_id_re.sub(
                lambda m: f' <span id="{m.group(1).lower()}"></span>', line
            )
        out.append(line)
    return "\n".join(out)


def convert_highlights(md):
    """Convert ==highlighted text== to <mark> tags, skipping code blocks/spans."""
    _combined = re.compile(
        r"(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)"
        r"|==([^=\n]+)=="
    )

    def repl(match):
        if match.group(1) is not None:
            return match.group(0)
        return f"<mark>{match.group(2)}</mark>"

    return _combined.sub(repl, md)


def convert_math(md):
    """Protect LaTeX math from the markdown parser.

    $$...$$ block math → <div class="math-block">...</div>
    $...$ inline math  → <span class="math-inline">...</span>

    Skips content inside fenced code blocks and backtick code spans.
    """
    _combined = re.compile(
        r"(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)"  # code span — skip
        r"|\$\$(.+?)\$\$"  # block math
        r"|\$([^\$\n]+)\$",  # inline math
        re.DOTALL,
    )

    def repl(match):
        if match.group(1) is not None:
            return match.group(0)
        if match.group(2) is not None:
            return f'<div class="math-block">{match.group(2)}</div>'
        return f'<span class="math-inline">{match.group(3)}</span>'

    return _combined.sub(repl, md)
