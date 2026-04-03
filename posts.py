import os
import re
import sys
import threading
from datetime import datetime, date as date_type

import yaml

from config import VAULT_PATH, BLOG_TAGS, HOMEPAGE_TAG, FEATURED_TAG, LISTING_TAG
from converters import slugify, render_markdown, extract_h1


# url_path → post dict (content posts only, not homepage/listing files)
ALL_POSTS = {}
# section root url → {"type": "homepage"|"listing", "post": post_dict, "section": str}
SECTION_ROUTES = {}
WEBSITE_NAME = "My Blog"
# filepath → {metadata, tags, file} for ALL vault notes (feeds Dataview queries)
DATAVIEW_INDEX = {}
# url_path → dataview entry for notes that exist but are NOT published as web pages
PRIVATE_ROUTES = {}
# posts pinned to the top nav via menu_order frontmatter, sorted by menu_order
MENU_POSTS = []
# True when the root homepage has the "search" tag — controls nav search link
SHOW_SEARCH = False
# True when the root homepage has the "labels" tag — controls nav labels link
SHOW_LABELS = False
LAST_SCAN_TIME = 0
_reload_lock = threading.Lock()

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
    menu_posts = []
    show_search = False
    show_labels = False

    # ---- Pass 1: scan ALL .md files — build dataview_index + candidates ----
    candidates = []
    url_index = {}  # slugify(title) → url_path, used to resolve wiki-links
    dataview_index = {}  # filepath → dataview context (all vault notes)

    for root, _, files in os.walk(VAULT_PATH):
        for f in files:
            if not f.endswith(".md"):
                continue

            filepath = os.path.join(root, f)

            try:
                with open(filepath, encoding="utf-8") as fh:
                    text = fh.read()
            except OSError as e:
                print(f"Skipping {filepath}: {e}", file=sys.stderr)
                continue

            metadata, md = parse_frontmatter(text)

            try:
                tags = set(t.lower() for t in (metadata.get("tags") or []))
            except Exception as e:
                print(f"Error processing tags for {filepath}: {e}")
                tags = set()

            dv_title = metadata.get("title") or extract_h1(md) or f[:-3]
            dv_date = _parse_date(
                metadata.get("date") or metadata.get("created"), filepath
            )

            # Every note gets a slugified URL — web posts will override below
            dv_slug = metadata.get("slug") or slugify(dv_title)
            dv_section = _section_from_filepath(filepath)
            dv_url = (
                ("/" + dv_section + "/" + dv_slug)
                if dv_section
                else ("/" + dv_slug)
            )

            dataview_index[filepath] = {
                "filepath": filepath,
                "title": dv_title,
                "metadata": metadata,
                "tags": tags,
                "labels": [],   # populated in pass 2 for published notes
                "section": dv_section,
                "url_path": dv_url,
                "file": {
                    "path": filepath,
                    "name": dv_title,
                    "link": f'<a href="{dv_url}">{dv_title}</a>',
                    "ctime": dv_date,
                },
            }

            if BLOG_TAGS.isdisjoint(tags):
                continue

            title_raw = metadata.get("title")
            if isinstance(title_raw, dict):
                # YAML parsed "title: Some: Value" as a nested mapping.
                # The field must be quoted: title: "Some: Value"
                print(
                    f"WARNING: {filepath} — 'title' parsed as a dict "
                    f"(value contains an unquoted colon). "
                    f"Wrap it in quotes: title: \"...\". Falling back to H1/filename.",
                    file=sys.stderr,
                )
                title_raw = None
            title = title_raw or extract_h1(md) or f[:-3]
            slug_raw = metadata.get("slug")
            slug = (slug_raw if isinstance(slug_raw, str) else None) or slugify(title)
            section = _section_from_filepath(filepath)

            if section:
                url_path = "/" + section + "/" + slug
            else:
                url_path = "/" + slug

            # Store all keys lowercase so wiki-link lookup is case-insensitive
            url_index[slugify(title).lower()] = url_path
            # Also index by filename and slug so [[Filename|Display]] links
            # resolve even when the title differs from the file name.
            url_index[slugify(f[:-3]).lower()] = url_path
            url_index[slug.lower()] = url_path
            # aliases frontmatter: list of alternate names that resolve to this post
            aliases = metadata.get("aliases") or []
            if isinstance(aliases, str):
                aliases = [aliases]
            for alias in aliases:
                url_index[slugify(str(alias)).lower()] = url_path

            # Update dataview entry with web URL, section, and clickable link
            dataview_index[filepath]["url_path"] = url_path
            dataview_index[filepath]["section"] = section
            dataview_index[filepath]["file"]["link"] = (
                f'<a href="{url_path}">{title}</a>'
            )

            candidates.append((filepath, f, metadata, md, tags, title, slug,
                                section, url_path))

    # ---- Pass 2: render markdown with resolved wiki-links + dataview ----
    for (filepath, f, metadata, md, tags, title, slug,
         section, url_path) in candidates:

        date = _parse_date(metadata.get("date"), filepath)
        updated = _parse_date(
            metadata.get("updated") or metadata.get("modified"), filepath
        )
        html, toc = render_markdown(md, filepath, url_index, dataview_index,
                                    note_metadata=metadata)
        summary = metadata.get("summary") or _make_summary(html)
        priority_raw = metadata.get("priority")
        priority = float("inf") if priority_raw is None else int(priority_raw)

        section_url = ("/" + section) if section else "/"
        is_homepage = HOMEPAGE_TAG in tags
        is_listing = LISTING_TAG in tags
        is_featured = FEATURED_TAG in tags

        banner = metadata.get("banner")
        banner_x = metadata.get("banner_x")
        banner_y = metadata.get("banner_y")
        # author: string or list — normalise to a list for the template
        author_raw = metadata.get("author")
        if isinstance(author_raw, str):
            author = [author_raw] if author_raw.strip() else []
        elif isinstance(author_raw, list):
            author = [str(a) for a in author_raw if a]
        else:
            author = []

        print(
            f"Loaded: {title} | {url_path} | "
            f"homepage={is_homepage} listing={is_listing} featured={is_featured}"
        )

        # For book posts, strip the leading cover <img> paragraph — it renders
        # in the book template header instead of the body.
        body_html = html
        if "📚book" in tags:
            body_html = re.sub(
                r"^\s*<p>\s*<img[^>]+>\s*</p>", "", html.strip()
            ).strip()

        word_count = len(re.sub(r"<[^>]+>", "", body_html).split())
        reading_time = max(1, word_count // 200)

        raw_labels = metadata.get("labels") or []
        try:
            fm_labels = set(str(l).lower() for l in raw_labels)
        except Exception:
            fm_labels = set()
        # Also collect #hashtag mentions from the raw markdown body
        body_tags = set(
            t.lower() for t in re.findall(r"(?<!\w)#([A-Za-z][A-Za-z0-9_-]*)", md)
        )
        labels = sorted(fm_labels | body_tags)
        dataview_index[filepath]["labels"] = labels

        post_data = {
            "url_path": url_path,
            "section": section,
            "section_url": section_url,
            "slug": slug,
            "title": title,
            "date": date,
            "updated": updated,
            "author": author,
            "html": body_html,
            "toc": toc,
            "reading_time": reading_time,
            "tags": tags,
            "labels": labels,
            "content": re.sub(r"<[^>]+>", "", html).lower(),
            "summary": summary,
            "priority": priority,
            "featured": is_featured,
            "banner": banner,
            "banner_x": banner_x,
            "banner_y": banner_y,
            "metadata": metadata,
        }

        menu_order_raw = metadata.get("menu_order")
        if menu_order_raw is not None:
            menu_posts.append({
                "title": title,
                "url_path": url_path,
                "menu_order": int(menu_order_raw),
            })

        if is_listing:
            section_routes[section_url] = {
                "type": "listing",
                "post": post_data,
                "section": section,
            }
        elif is_homepage:
            if section == "":
                website_name = title
                show_search = "search" in tags
                show_labels = "labels" in tags
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
                    "updated": None,
                    "author": [],
                    "html": "",
                    "toc": "",
                    "reading_time": 0,
                    "tags": set(),
                    "labels": [],
                    "content": "",
                    "summary": "",
                    "priority": float("inf"),
                    "featured": False,
                    "banner": None,
                    "banner_x": None,
                    "banner_y": None,
                    "metadata": {},
                },
            }
            print(f"Auto-listing: {section_url} ('{title}')")

    # ---- Build private routes: vault notes that have a URL but are not published ----
    # Exclude homepage/listing files (served at section URLs, not their slug URL)
    private_routes = {
        entry["url_path"]: entry
        for entry in dataview_index.values()
        if entry.get("url_path")
        and entry["url_path"] not in all_posts
        and entry["url_path"] not in section_routes
        and HOMEPAGE_TAG not in entry.get("tags", set())
        and LISTING_TAG not in entry.get("tags", set())
    }

    menu_posts.sort(key=lambda x: x["menu_order"])
    return (all_posts, section_routes, website_name, dataview_index,
            private_routes, menu_posts, show_search, show_labels)


# =========================================
# AUTO RELOAD
# =========================================

def maybe_reload():
    global ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, DATAVIEW_INDEX, \
        PRIVATE_ROUTES, MENU_POSTS, SHOW_SEARCH, SHOW_LABELS, LAST_SCAN_TIME

    if not _reload_lock.acquire(blocking=False):
        return  # Another thread is already reloading

    try:
        newest = 0
        for root, _, files in os.walk(VAULT_PATH):
            for f in files:
                try:
                    newest = max(newest, os.path.getmtime(
                        os.path.join(root, f)
                    ))
                except OSError:
                    pass

        if newest > LAST_SCAN_TIME:
            print("Reloading vault...")
            (ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME,
             DATAVIEW_INDEX, PRIVATE_ROUTES, MENU_POSTS,
             SHOW_SEARCH, SHOW_LABELS) = load_posts()
            LAST_SCAN_TIME = newest
    except Exception as e:
        print(f"Reload error (serving stale data): {e}", file=sys.stderr)
    finally:
        _reload_lock.release()
