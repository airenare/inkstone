import os
import re

import yaml
from datetime import datetime

from config import VAULT_PATH, BLOG_TAGS, HOMEPAGE_TAG, FEATURED_TAG
from converters import slugify, render_markdown, extract_h1


POSTS = {}
HOMEPAGE = {}
WEBSITE_NAME = "My Blog"
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

SUMMARY_LENGTH = 200


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
# SUMMARY HELPER
# =========================================

def _make_summary(html):
    plain = re.sub(r"<[^>]+>", "", html).strip()
    plain = re.sub(r"\s+", " ", plain)
    if len(plain) <= SUMMARY_LENGTH:
        return plain
    return plain[:SUMMARY_LENGTH].rsplit(" ", 1)[0] + "\u2026"


# =========================================
# LOAD POSTS
# =========================================

def load_posts():
    posts = []
    homepage = {}
    website_name = "My Blog"

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

            # Title resolution: frontmatter > H1 in body > filename
            title = metadata.get("title") or extract_h1(md) or f[:-3]
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

            # PyYAML parses bare dates (2026-01-15) as datetime.date, not datetime
            from datetime import date as date_type
            if isinstance(date, date_type) and not isinstance(date, datetime):
                date = datetime(date.year, date.month, date.day)
            elif isinstance(date, str):
                try:
                    date = datetime.fromisoformat(date)
                except Exception as e:
                    print(f"Error parsing date for {filepath}: {e}")
                    date = None

            html = render_markdown(md, filepath)

            summary = metadata.get("summary") or _make_summary(html)

            priority_raw = metadata.get("priority")
            priority = float("inf") if priority_raw is None else int(priority_raw)

            is_homepage = HOMEPAGE_TAG in tags
            is_featured = FEATURED_TAG in tags

            print(f"Loaded: {title} (slug: {slug}, date: {date}, homepage: {is_homepage}, featured: {is_featured})")

            post_data = {
                "slug": slug,
                "title": title,
                "date": date,
                "html": html,
                "tags": tags,
                "content": html.lower(),
                "summary": summary,
                "priority": priority,
                "featured": is_featured,
            }

            if is_homepage:
                homepage = post_data
                website_name = title
            else:
                posts.append(post_data)

    posts.sort(key=lambda x: x["date"] or datetime.min, reverse=True)

    return {p["slug"]: p for p in posts}, homepage, website_name


# =========================================
# AUTO RELOAD
# =========================================

def maybe_reload():
    global POSTS, HOMEPAGE, WEBSITE_NAME, LAST_SCAN_TIME

    newest = 0
    for root, _, files in os.walk(VAULT_PATH):
        for f in files:
            filepath = os.path.join(root, f)
            newest = max(newest, os.path.getmtime(filepath))

    if newest > LAST_SCAN_TIME:
        print("Reloading vault...")
        POSTS, HOMEPAGE, WEBSITE_NAME = load_posts()
        LAST_SCAN_TIME = newest
