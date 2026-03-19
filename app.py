import os
import re
from sys import path
import yaml
import markdown
import dotenv

from datetime import datetime
from flask import Flask, render_template, abort, request, send_from_directory


# =========================================
# CONFIG
# =========================================

dotenv.load_dotenv()

# Check that VAULT_PATH exists, if not, use the BlogPages in projects directory for testing
VAULT_PATH = os.getenv("VAULT_PATH")
if not VAULT_PATH or not os.path.exists(VAULT_PATH):
    print(f"Warning: VAULT_PATH '{VAULT_PATH}' does not exist. Using './BlogPages' for testing.")
    VAULT_PATH = "./BlogPages"

BLOG_TAGS = {"blog", "website"}

app = Flask(
    __name__,
    template_folder="site/templates",
    static_folder="site/static"
)

POSTS = {}
LAST_SCAN_TIME = 0


# =========================================
# UTILITIES
# =========================================

def slugify(text):
    text = text.strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


# =========================================
# FRONTMATTER
# =========================================

def parse_frontmatter(text):
    metadata = {}

    if text.startswith("---"):
        try:
            _, yaml_text, body = text.split("---", 2)
            metadata = yaml.safe_load(yaml_text) or {}
            return metadata, body.strip()

        except Exception as e:
            print(f"Failed to parse frontmatter for {path}: {e}")
            return {}, text

    return {}, text


# =========================================
# OBSIDIAN LINK PARSER
# =========================================

def convert_links(md):
    pattern = r"\[\[([^\]]+)\]\]"
    
    def repl(match):
        target = match.group(1)
        slug = slugify(target)
        return f"[{target}](/post/{slug})"

    return re.sub(pattern, repl, md)


# =========================================
# OBSIDIAN CHECKBOX PARSER
# =========================================
def parse_checkbox(md):
    # Match indentation + checkbox
    pattern = r"^(\s*)- \[([ xX])\] (.*)$"
    match = re.match(pattern, md)
    if not match:
        return None
    

    indent, checked, text = match.groups()
    indent = indent.replace("\t", "    ") # Convert tabs to spaces for consistent indentation

    return {
        "indent": len(indent),
        "checked": checked.lower() == "x",
        "text": text
    }

def render_checkbox(item):
    indent_em = item["indent"] * 0.25 # matching the ul margin
    checked_attr = "checked" if item["checked"] else ""

    return f"""

<div class="checkbox" style="margin-left: {indent_em}em;">
    <label>
        <input type="checkbox" disabled {checked_attr}>
        {item["text"]}
    </label>
</div>

"""


# def convert_checkboxes(md):
#     lines = md.split("\n")
#     out = []

#     for line in lines:
#         item = parse_checkbox(line)

#         if item:
#             out.append(render_checkbox(item))
#         else:
#             out.append(line)

#     return "\n".join(out)

def convert_checkboxes(md):
    lines = md.split("\n")
    out = []

    stack = []  # keeps track of open <ul>
    
    def close_lists(to_level=0):
        while len(stack) > to_level:
            out.append("</ul>")
            stack.pop()

    for line in lines:
        match = re.match(r'^(\s*)- \[([ xX])\] (.*)', line)

        if match:
            indent, checked, text = match.groups()
            indent = indent.replace("\t", "    ")
            level = len(indent) // 4  # 4 spaces = 1 level

            checked_attr = "checked" if checked.lower() == "x" else ""

            # Open new lists if needed
            while len(stack) < level + 1:
                out.append('<ul class="checkbox-list">')
                stack.append("<ul>")

            # Close lists if needed
            close_lists(level + 1)

            out.append(
                f'<li><input type="checkbox" disabled {checked_attr}> {text}</li>'
            )

        else:
            # If we hit a non-checkbox line → close all lists
            if stack:
                close_lists(0)

            out.append(line)

    # Close any remaining lists
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
        # Single image → inline HTML
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
        html += '<button class="slider-arrow left">‹</button>'
        html += '<div class="slides">'
        for item in slider:
            html += f'<div class="slide">{item}</div>'
        html += '</div>'
        html += '<button class="slider-arrow right">›</button>'
        html += '<div class="slider-dots"></div>'
        html += '</div>'
        slider.clear()
        return html

    for line in lines:
        matches = re.findall(pattern, line)

        # Slider: multiple images/videos in one line separated by spaces
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
                    slider.append(f'<video src="/attachments/{rel}" controls loading="lazy"></video>')
                else:
                    slider.append(f'<img src="/attachments/{rel}" alt="{caption}" loading="lazy">')
            output.append(flush_slider())
            continue

        # Single image/video line
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
                gallery.append(f'<video src="/attachments/{rel}" controls loading="lazy"></video>')
            else:
                gallery.append(
                    f'<img src="/attachments/{rel}" '
                    f'data-gallery="gallery" data-src="/attachments/{rel}" '
                    f'data-type="image" data-caption="{caption}" loading="lazy">'
                )
            continue

        # Normal text line
        else:
            if gallery:
                output.append(flush_gallery())
            output.append(line)

    # Flush remaining gallery at the end
    if gallery:
        output.append(flush_gallery())
    if slider:
        output.append(flush_slider())

    return "\n".join(output)

# =========================================
# MARKDOWN PIPELINE
# =========================================

def render_markdown(md, path):

    md = convert_media(md, path)
    md = convert_links(md)
    md = convert_callouts(md)
    md = convert_checkboxes(md)

    html = markdown.markdown(
        md,
        extensions=["fenced_code", "tables", "toc", "md_in_html", "codehilite"],
        output_format="html5"
    )

    return html


# =========================================
# LOAD POSTS
# =========================================

def load_posts():

    posts = []

    for root, _, files in os.walk(VAULT_PATH):

        for f in files:

            if not f.endswith(".md"):
                continue

            path = os.path.join(root, f)

            with open(path, encoding="utf-8") as file:
                text = file.read()

            metadata, md = parse_frontmatter(text)

            try:
                tags = set(t.lower() for t in metadata.get("tags", []))
            except Exception as e:
                print(f"Error occurred while processing tags for {path}: {e}")
                tags = set()

            if BLOG_TAGS.isdisjoint(tags):
                continue

            title = metadata.get("title", f[:-3])
            slug = metadata.get("slug") or slugify(title)
            date = metadata.get("date")
            # Make sure all dates are parsed no matter the format
            date_formats = [
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d",
                "%Y/%m/%d %H:%M",
                "%Y/%m/%d %H:%M:%S",
                "%d-%m-%Y",
                "%d-%m-%Y %H:%M",
                "%d-%m-%Y %H:%M:%S",
                "%d/%m/%Y",
                "%d/%m/%Y %H:%M",
                "%d/%m/%Y %H:%M:%S"
            ]

            # Try parsing date with multiple formats
            if isinstance(date, str):

                for fmt in date_formats:
                    try:
                        date = datetime.strptime(date, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    print(f"Error: Unrecognized date format for {path}: {date}")
                    date = None


            print(f"Loaded post: {title} (slug: {slug}, date: {date})")

            if isinstance(date, str):

                try:
                    date = datetime.fromisoformat(date)
                except Exception as e:
                    print(f"Error occurred while parsing date for {path}: {e}")
                    date = None

            html = render_markdown(md, path)

            posts.append({
                "slug": slug,
                "title": title,
                "date": date,
                "html": html,
                "tags": tags,
                "content": html.lower()
            })

    posts.sort(key=lambda x: x["date"] or datetime.min, reverse=True)

    return {p["slug"]: p for p in posts}


# =========================================
# AUTO RELOAD
# =========================================

def maybe_reload():

    global POSTS
    global LAST_SCAN_TIME

    newest = 0

    for root, _, files in os.walk(VAULT_PATH):

        for f in files:

            path = os.path.join(root, f)

            newest = max(newest, os.path.getmtime(path))

    if newest > LAST_SCAN_TIME:

        print("Reloading vault...")

        POSTS = load_posts()

        LAST_SCAN_TIME = newest


# =========================================
# ROUTES
# =========================================

@app.route("/")
def index():

    maybe_reload()

    return render_template(
        "index.html",
        posts=POSTS.values()
    )


@app.route("/post/<slug>")
def post(slug):

    maybe_reload()

    if slug not in POSTS:
        abort(404)

    return render_template(
        "post.html",
        post=POSTS[slug]
    )


@app.route("/attachments/<path:path>")
def attachments(path):

    return send_from_directory(VAULT_PATH, path)


@app.route("/search")
def search():

    maybe_reload()

    q = request.args.get("q", "").lower()

    results = []

    if q:

        results = [
            p for p in POSTS.values()
            if q in p["title"].lower()
            or q in p["content"]
        ]

    return render_template(
        "search.html",
        posts=results,
        query=q
    )


# =========================================
# START
# =========================================

if __name__ == "__main__":

    POSTS = load_posts()

    app.run("127.0.0.1", 8000, debug=True)