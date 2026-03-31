import os

import yaml
from datetime import datetime

from config import VAULT_PATH, BLOG_TAGS
from converters import slugify, render_markdown


POSTS = {}
LAST_SCAN_TIME = 0

DATE_FORMATS = [
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
    "%d/%m/%Y %H:%M:%S",
]


# =========================================
# FRONTMATTER
# =========================================

def parse_frontmatter(text):
    if text.startswith("---"):
        try:
            _, yaml_text, body = text.split("---", 2)
            metadata = yaml.safe_load(yaml_text) or {}
            return metadata, body.strip()
        except Exception as e:
            print(f"Failed to parse frontmatter: {e}")
            return {}, text
    return {}, text


# =========================================
# LOAD POSTS
# =========================================

def load_posts():
    posts = []

    for root, _, files in os.walk(VAULT_PATH):
        for f in files:
            if not f.endswith(".md"):
                continue

            filepath = os.path.join(root, f)

            with open(filepath, encoding="utf-8") as fh:
                text = fh.read()

            metadata, md = parse_frontmatter(text)

            try:
                tags = set(t.lower() for t in metadata.get("tags", []))
            except Exception as e:
                print(f"Error processing tags for {filepath}: {e}")
                tags = set()

            if BLOG_TAGS.isdisjoint(tags):
                continue

            title = metadata.get("title", f[:-3])
            slug = metadata.get("slug") or slugify(title)
            date = metadata.get("date")

            if isinstance(date, str):
                for fmt in DATE_FORMATS:
                    try:
                        date = datetime.strptime(date, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    print(f"Unrecognized date format for {filepath}: {date}")
                    date = None

            # PyYAML may parse dates as datetime.date objects
            if isinstance(date, str):
                try:
                    date = datetime.fromisoformat(date)
                except Exception as e:
                    print(f"Error parsing date for {filepath}: {e}")
                    date = None

            print(f"Loaded post: {title} (slug: {slug}, date: {date})")

            html = render_markdown(md, filepath)

            posts.append({
                "slug": slug,
                "title": title,
                "date": date,
                "html": html,
                "tags": tags,
                "content": html.lower(),
            })

    posts.sort(key=lambda x: x["date"] or datetime.min, reverse=True)

    return {p["slug"]: p for p in posts}


# =========================================
# AUTO RELOAD
# =========================================

def maybe_reload():
    global POSTS, LAST_SCAN_TIME

    newest = 0
    for root, _, files in os.walk(VAULT_PATH):
        for f in files:
            filepath = os.path.join(root, f)
            newest = max(newest, os.path.getmtime(filepath))

    if newest > LAST_SCAN_TIME:
        print("Reloading vault...")
        POSTS = load_posts()
        LAST_SCAN_TIME = newest
