import os
import re
from datetime import datetime, date as date_type

import yaml

from config import VAULT_PATH, BLOG_TAGS, HOMEPAGE_TAG, FEATURED_TAG, LISTING_TAG
from converters import slugify, render_markdown, extract_h1


# url_path → post dict (content posts only, not homepage/listing files)
ALL_POSTS = {}
# section root url → {"type": "homepage"|"listing", "post": post_dict, "section": str}
SECTION_ROUTES = {}
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
# HELPERS
# =========================================

def _make_summary(html):
    plain = re.sub(r"<[^>]+>", "", html).strip()
    plain = re.sub(r"\s+", " ", plain)
    if len(plain) <= SUMMARY_LENGTH:
        return plain
    return plain[:SUMMARY_LENGTH].rsplit(" ", 1)[0] + "\u2026"


def _section_from_filepath(filepath):
    """Return the section string for a file, e.g. '' for root, 'blog', 'gallery/arts'."""
    folder = os.path.dirname(os.path.abspath(filepath))
    vault = os.path.abspath(VAULT_PATH)
    rel = os.path.relpath(folder, vault)
    if rel == ".":
        return ""
    parts = rel.replace("\\", "/").split("/")
    return "/".join(slugify(p) for p in parts)


def _parse_date(date, filepath):
    """Normalize a raw date value (str, date, datetime) to datetime or None."""
    if isinstance(date, date_type) and not isinstance(date, datetime):
        return datetime(date.year, date.month, date.day)
    if isinstance(date, str):
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(date, fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(date)
        except Exception:
            pass
        print(f"Unrecognized date format for {filepath}: {date}")
    return date if isinstance(date, datetime) else None


# =========================================
# LOAD POSTS
# =========================================

def load_posts():
    all_posts = {}
    section_routes = {}
    website_name = "My Blog"

    # ---- Pass 1: collect metadata and build title → url_path index ----
    candidates = []
    url_index = {}  # slugify(title) → url_path, used to resolve wiki-links

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

            title = metadata.get("title") or extract_h1(md) or f[:-3]
            slug = metadata.get("slug") or slugify(title)
            section = _section_from_filepath(filepath)

            if section:
                url_path = "/" + section + "/" + slug
            else:
                url_path = "/" + slug

            url_index[slugify(title)] = url_path
            candidates.append((filepath, f, metadata, md, tags, title, slug,
                                section, url_path))

    # ---- Pass 2: render markdown with resolved wiki-links ----
    for (filepath, f, metadata, md, tags, title, slug,
         section, url_path) in candidates:

        date = _parse_date(metadata.get("date"), filepath)
        html = render_markdown(md, filepath, url_index)
        summary = metadata.get("summary") or _make_summary(html)
        priority_raw = metadata.get("priority")
        priority = float("inf") if priority_raw is None else int(priority_raw)

        section_url = ("/" + section) if section else "/"
        is_homepage = HOMEPAGE_TAG in tags
        is_listing = LISTING_TAG in tags
        is_featured = FEATURED_TAG in tags

        print(
            f"Loaded: {title} | {url_path} | "
            f"homepage={is_homepage} listing={is_listing} featured={is_featured}"
        )

        post_data = {
            "url_path": url_path,
            "section": section,
            "section_url": section_url,
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

        if is_listing:
            section_routes[section_url] = {
                "type": "listing",
                "post": post_data,
                "section": section,
            }
        elif is_homepage:
            if section == "":
                website_name = title
            section_routes[section_url] = {
                "type": "homepage",
                "post": post_data,
            }
        else:
            all_posts[url_path] = post_data

    # ---- Auto-generate listing routes for sections with no explicit index ----
    for post_data in all_posts.values():
        section = post_data["section"]
        section_url = post_data["section_url"]
        if section and section_url not in section_routes:
            last_segment = section.rsplit("/", 1)[-1]
            title = last_segment.replace("-", " ").replace("_", " ").title()
            section_routes[section_url] = {
                "type": "listing",
                "section": section,
                "post": {
                    "url_path": section_url,
                    "section": section,
                    "section_url": section_url,
                    "slug": last_segment,
                    "title": title,
                    "date": None,
                    "html": "",
                    "tags": set(),
                    "content": "",
                    "summary": "",
                    "priority": float("inf"),
                    "featured": False,
                },
            }
            print(f"Auto-listing: {section_url} ('{title}')")

    return all_posts, section_routes, website_name


# =========================================
# AUTO RELOAD
# =========================================

def maybe_reload():
    global ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, LAST_SCAN_TIME

    newest = 0
    for root, _, files in os.walk(VAULT_PATH):
        for f in files:
            filepath = os.path.join(root, f)
            newest = max(newest, os.path.getmtime(filepath))

    if newest > LAST_SCAN_TIME:
        print("Reloading vault...")
        ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME = load_posts()
        LAST_SCAN_TIME = newest
