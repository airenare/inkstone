import os
import re

import markdown

from config import VAULT_PATH


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
    """Convert [[Wiki Links]] to markdown links.

    url_index: dict of {slugify(title): url_path} built during two-pass loading.
    Falls back to /slugified-title if the title is not found in the index.
    """
    pattern = r"\[\[([^\]]+)\]\]"

    def repl(match):
        target = match.group(1)
        slug = slugify(target)
        url = url_index.get(slug) if url_index else None
        return f"[{target}]({url or '/' + slug})"

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

    for line in lines:
        if line.lstrip().startswith("> [!"):
            if callout_open:
                out.append(render_callout(callout_type, callout_title, callout_content))
                callout_content = []

            callout_open = True
            header = line.lstrip("> ").strip()
            type_part = header.split("]")[0]
            callout_type = type_part[2:].lower()
            callout_title = header.split("]")[1].strip()

        elif callout_open and line.startswith(">"):
            callout_content.append(line[1:].strip())

        else:
            if callout_open:
                out.append(render_callout(callout_type, callout_title, callout_content))
                callout_open = False
                callout_content = []

            out.append(line)

    if callout_open:
        out.append(render_callout(callout_type, callout_title, callout_content))

    return "\n".join(out)


def render_callout(type_, title, content):
    body = "\n".join(content)
    return f"""
<div class="callout callout-{type_}">

<div class="callout-title">
<span class="callout-icon"></span>
<span class="callout-title-text">{title}</span>
</div>

<div class="callout-content">
{body}
</div>

</div>
"""


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
                    continue
                rel = os.path.relpath(full_path, VAULT_PATH)
                ext = filename.lower().split(".")[-1]
                if ext in ["mp4", "webm", "mov"]:
                    slider.append(
                        f'<video src="/attachments/{rel}" controls loading="lazy"></video>'
                    )
                else:
                    slider.append(
                        f'<img src="/attachments/{rel}" alt="{caption}" loading="lazy">'
                    )
            output.append(flush_slider())
            continue

        # Single embed on its own line
        elif len(matches) == 1 and line.strip().startswith("![["):
            filename, caption = matches[0]
            filename = filename.strip()
            full_path = os.path.join(folder, "_attachments", filename)
            if not os.path.exists(full_path):
                output.append(f"<em>Missing media: {filename}</em>")
                continue
            rel = os.path.relpath(full_path, VAULT_PATH)
            ext = filename.lower().split(".")[-1]
            if ext in ["mp4", "webm", "mov"]:
                gallery.append(
                    f'<video src="/attachments/{rel}" controls loading="lazy"></video>'
                )
            else:
                gallery.append(
                    f'<img src="/attachments/{rel}" '
                    f'data-gallery="gallery" data-src="/attachments/{rel}" '
                    f'data-type="image" data-caption="{caption}" loading="lazy">'
                )
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


def render_markdown(md, path, url_index=None):
    md = strip_leading_h1(md)
    md = convert_media(md, path)
    md = convert_links(md, url_index)
    md = convert_callouts(md)
    md = convert_checkboxes(md)

    html = markdown.markdown(
        md,
        extensions=["fenced_code", "tables", "toc", "md_in_html", "codehilite"],
        output_format="html5",
    )

    return html
