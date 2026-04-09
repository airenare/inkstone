"""Obsidian-specific markdown converters.

All functions that understand Obsidian's extended syntax live here:
wiki-links, embeds, callouts, checkboxes, highlights, math, block IDs,
transclusion, and the slug utility.  converters.py imports from this
module and wires them into the render_markdown() pipeline.
"""
import os
import re

import markdown

from config import VAULT_PATH, ATTACHMENTS_PATH


# =========================================
# SLUG UTILITY
# =========================================

def slugify(text):
    text = text.strip().lower()
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
                vault_real = os.path.realpath(VAULT_PATH)
                if not os.path.realpath(full_path).startswith(
                    vault_real + os.sep
                ):
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
                vault_att = os.path.join(VAULT_PATH, "_attachments", filename)
                if os.path.exists(vault_att):
                    full_path = vault_att
                elif ATTACHMENTS_PATH:
                    custom_att = os.path.join(ATTACHMENTS_PATH, filename)
                    if os.path.exists(custom_att):
                        full_path = custom_att
            if not os.path.exists(full_path):
                output.append(f"<em>Missing media: {filename}</em>")
                continue
            vault_real = os.path.realpath(VAULT_PATH)
            if not os.path.realpath(full_path).startswith(
                vault_real + os.sep
            ):
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
    """Replace trailing ^block-id markers with anchor spans."""
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

    Skips content inside backtick code spans so that e.g. `$inline$`
    is not converted.
    """
    # Alternation trick: match code spans first (group 1) and leave them
    # untouched; only convert when the math group (group 2) matched.
    md = re.sub(
        r"(`+[^`]*`+)|\$\$(.+?)\$\$",
        lambda m: m.group(0) if m.group(1)
                  else f'<div class="math-block">{m.group(2)}</div>',
        md,
        flags=re.DOTALL,
    )
    md = re.sub(
        r"(`+[^`]*`+)|\$([^\$\n]+)\$",
        lambda m: m.group(0) if m.group(1)
                  else f'<span class="math-inline">{m.group(2)}</span>',
        md,
    )
    return md
