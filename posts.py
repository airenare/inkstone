import os
import re
import sys
import threading
import time
from datetime import datetime, date as date_type

import yaml

from config import VAULT_PATH
from converters import slugify, render_markdown, extract_h1
from view_helpers import get_related


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
# Default language code (from root homepage `language:` frontmatter, e.g. "en")
DEFAULT_LANG: str = "en"
# All language codes found in vault, default first (e.g. ["en", "ru"])
AVAILABLE_LANGS: list = []
# base_url → {lang_code: url_path} — powers the language toggle and fallback logic
LANG_GROUPS: dict = {}
# True when the root homepage has the "search" tag — controls nav search link
SHOW_SEARCH = False
# True when the root homepage has show_tags: true — controls nav tags link
SHOW_TAGS = False
# url_path → {"icon": vault-relative path, "site_title": str} for pages that set
# a header icon or custom site title; used for cascade inheritance at request time.
ICON_OVERRIDES: dict = {}
# Sorted list of all user content tags across published posts
ALL_TAGS: list = []
# Active theme name — set from the root homepage 'theme' frontmatter field
SITE_THEME: str = "obsidian"
# Social links from root homepage 'social_links:' frontmatter — list of
# {label: str, url: str} dicts rendered as <a rel="me"> in the footer.
SOCIAL_LINKS: list = []

_VALID_THEMES = {"obsidian", "omarchy"}


def _resolve_theme(value, context=""):
    """Return a valid theme name, falling back to 'obsidian' with a warning."""
    if not value:
        return "obsidian"
    name = str(value).strip().lower()
    if name not in _VALID_THEMES:
        print(
            f"WARNING: Unknown theme '{name}'"
            + (f" in {context}" if context else "")
            + ". Falling back to 'obsidian'.",
            file=sys.stderr,
        )
        return "obsidian"
    return name
LAST_SCAN_TIME = 0
_reload_lock = threading.Lock()
_last_check_time = 0.0

# Matches fenced code blocks (``` or ~~~, with optional language label)
_FENCED_CODE_RE = re.compile(
    r"^(`{3,}|~{3,})[^\n]*\n.*?\n\1[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
# Matches inline code spans (single or multi backtick)
_INLINE_CODE_RE = re.compile(r"`+.+?`+", re.DOTALL)


def _strip_code(md):
    """Return md with fenced code blocks and inline code replaced by spaces.

    Used before hashtag extraction so that e.g. CSS colour literals
    like #f5a623 inside code blocks are not collected as body tags.
    """
    md = _FENCED_CODE_RE.sub("", md)
    md = _INLINE_CODE_RE.sub("", md)
    return md

# Matches exactly 2 uppercase letters as a filename language suffix, e.g. _RU _EN _FR
_LANG_SUFFIX_RE = re.compile(r"^(.+)_([A-Z]{2})$")


def _extract_lang(stem, frontmatter_lang=None):
    """Return (base_stem, lang_code). base_stem has any _XX suffix stripped.

    frontmatter_lang (from `lang:` frontmatter) takes precedence over suffix.
    Returns lang_code=None when no language is detected — caller should
    substitute the vault's default_lang.
    """
    if frontmatter_lang:
        m = _LANG_SUFFIX_RE.match(stem)
        base = m.group(1) if m else stem
        return base, str(frontmatter_lang).strip().lower()
    m = _LANG_SUFFIX_RE.match(stem)
    if m:
        return m.group(1), m.group(2).lower()
    return stem, None


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

def parse_frontmatter(text, filepath="<unknown>"):
    if text.startswith("---"):
        try:
            _, yaml_text, body = text.split("---", 2)
            metadata = yaml.safe_load(yaml_text) or {}
            return metadata, body.strip()
        except Exception as e:
            print(f"Failed to parse frontmatter in {filepath}: {e}")
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
    site_theme = "obsidian"
    menu_posts = []
    show_search = False
    show_tags = False
    social_links = []

    # ---- Pre-scan vault root for the homepage to detect default language ----
    default_lang = "en"
    _vault_abs = os.path.abspath(VAULT_PATH)
    try:
        for _fname in os.listdir(_vault_abs):
            if not _fname.endswith(".md"):
                continue
            _fp = os.path.join(_vault_abs, _fname)
            if not os.path.isfile(_fp):
                continue
            try:
                with open(_fp, encoding="utf-8") as _fh:
                    _meta, _ = parse_frontmatter(_fh.read(), _fp)
                if (_meta.get("type") or "").strip().lower() == "homepage":
                    _raw = _meta.get("language", "en")
                    default_lang = str(_raw).strip().lower()
                    break
            except OSError:
                pass
    except OSError:
        pass

    # ---- Pass 1: scan ALL .md files — build dataview_index + candidates ----
    candidates = []
    url_index = {}  # slugify(title) → url_path, used to resolve wiki-links
    dataview_index = {}  # filepath → dataview context (all vault notes)

    for root, dirs, files in os.walk(VAULT_PATH):
        dirs[:] = [d for d in dirs if d.lower() != "templates"]
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

            metadata, md = parse_frontmatter(text, filepath)

            dv_title = metadata.get("title") or extract_h1(md) or f[:-3]
            dv_date = _parse_date(
                metadata.get("date") or metadata.get("created"), filepath
            )

            # Every note gets a slugified URL — web posts will override below
            raw_slug = metadata.get("slug")
            dv_slug = (str(raw_slug).lower() if raw_slug else None) or slugify(dv_title)
            dv_section = _section_from_filepath(filepath)
            dv_url = (
                ("/" + dv_section + "/" + dv_slug)
                if dv_section
                else ("/" + dv_slug)
            )

            # Compute tags now so Dataview queries can filter by tag
            # during pass-2 rendering (before individual posts set their own
            # tags entry).
            raw_tags = metadata.get("tags") or []
            try:
                fm_tags = set(str(t).lower() for t in raw_tags)
            except Exception:
                fm_tags = set()
            body_hashtags = set(
                t.lower()
                for t in re.findall(
                    r"(?<!\w)#([A-Za-z][A-Za-z0-9_-]*)", _strip_code(md)
                )
            )
            dv_tags = sorted(fm_tags | body_hashtags)

            dv_folder = os.path.relpath(
                os.path.dirname(os.path.abspath(filepath)),
                os.path.abspath(VAULT_PATH),
            ).replace("\\", "/")
            if dv_folder == ".":
                dv_folder = ""

            dataview_index[filepath] = {
                "filepath": filepath,
                "title": dv_title,
                "metadata": metadata,
                "tags": dv_tags,
                "section": dv_section,
                "url_path": dv_url,
                "file": {
                    "path": filepath,
                    "name": dv_title,
                    "link": f'<a href="{dv_url}">{dv_title}</a>',
                    "ctime": dv_date,
                    "folder": dv_folder,
                },
            }

            if not metadata.get("website"):
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

            # Language detection: filename suffix (_RU) or frontmatter `lang:`
            stem = f[:-3]
            base_stem, file_lang = _extract_lang(stem, metadata.get("lang"))
            lang = file_lang if file_lang else default_lang

            slug_raw = metadata.get("slug")
            # Slug falls back to base_stem (suffix stripped) when slugify(title)
            # produces an empty string, e.g. for non-ASCII Cyrillic-only titles.
            slug = (
                (str(slug_raw).lower() if isinstance(slug_raw, str) else None)
                or slugify(title)
                or slugify(base_stem)
            )
            section = _section_from_filepath(filepath)

            base_url_path = ("/" + section + "/" + slug) if section else ("/" + slug)
            if lang != default_lang:
                url_path = base_url_path + "/" + lang
            else:
                url_path = base_url_path

            # Homepage/listing files are served at the section URL, not their
            # computed url_path — index them under the section URL so that
            # [[SectionHomepage]] wiki-links resolve correctly.
            note_type_p1 = (metadata.get("type") or "").strip().lower()
            section_url_p1 = ("/" + section) if section else "/"
            index_url = (
                section_url_p1
                if note_type_p1 in ("homepage", "listing")
                else url_path
            )

            # Store all keys lowercase so wiki-link lookup is case-insensitive
            url_index[slugify(title).lower()] = index_url
            # Also index by filename and slug so [[Filename|Display]] links
            # resolve even when the title differs from the file name.
            url_index[slugify(f[:-3]).lower()] = index_url
            url_index[slug.lower()] = index_url
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

            candidates.append((filepath, f, metadata, md, title, slug,
                                section, url_path, lang, base_url_path))

    # ---- Pass 2: render markdown with resolved wiki-links + dataview ----
    for (filepath, f, metadata, md, title, slug,
         section, url_path, lang, base_url_path) in candidates:

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
        # Non-default language homepages/listings get a lang-suffixed section URL
        # e.g. "/blog" → "/blog/ru"  and  "/" → "/ru"
        if lang != default_lang:
            section_url = (section_url.rstrip("/") + "/" + lang) if section \
                else ("/" + lang)
        note_type = (metadata.get("type") or "").strip().lower()
        is_homepage = note_type == "homepage"
        is_listing = note_type == "listing"
        is_book = note_type == "book"
        is_featured = bool(metadata.get("featured"))

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
        if is_book:
            body_html = re.sub(
                r"^\s*<p>\s*<img[^>]+>\s*</p>", "", html.strip()
            ).strip()

        word_count = len(re.sub(r"<[^>]+>", "", body_html).split())
        reading_time = max(1, word_count // 200)

        raw_tags = metadata.get("tags") or []
        try:
            fm_tags = set(str(t).lower() for t in raw_tags)
        except Exception:
            fm_tags = set()
        # Also collect #hashtag mentions from the raw markdown body
        # Run on code-stripped text so CSS colour literals etc. are excluded
        body_hashtags = set(
            t.lower()
            for t in re.findall(
                r"(?<!\w)#([A-Za-z][A-Za-z0-9_-]*)", _strip_code(md)
            )
        )
        tags = sorted(fm_tags | body_hashtags)
        dataview_index[filepath]["tags"] = tags

        post_data = {
            "url_path": url_path,
            "base_url_path": base_url_path,
            "lang": lang,
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
            "post_type": note_type,
            "tags": tags,
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
                "lang": lang,
            })

        if is_listing:
            section_routes[section_url] = {
                "type": "listing",
                "post": post_data,
                "section": section,
                "lang": lang,
            }
        elif is_homepage:
            if section == "" and lang == default_lang:
                website_name = title
                show_search = bool(metadata.get("show_search"))
                show_tags = bool(metadata.get("show_tags"))
                site_theme = _resolve_theme(
                    metadata.get("theme"), filepath
                )
                raw_social = metadata.get("social_links") or []
                if isinstance(raw_social, list):
                    social_links = [
                        s for s in raw_social
                        if isinstance(s, dict)
                        and s.get("label") and s.get("url")
                    ]
            section_routes[section_url] = {
                "type": "homepage",
                "post": post_data,
                "lang": lang,
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
                    "post_type": "",
                    "tags": [],
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
    # Exclude homepage/listing files — their slug URL differs from the section URL
    # they are registered under, so they pass the section_routes check but must
    # not appear as private placeholders.
    private_routes = {
        entry["url_path"]: entry
        for entry in dataview_index.values()
        if entry.get("url_path")
        and entry["url_path"] not in all_posts
        and entry["url_path"] not in section_routes
        and entry.get("metadata", {}).get("type") not in ("homepage", "listing")
    }

    # ---- Pre-compute related posts (O(n²) at load time, O(1) per request) ----
    for post_data in all_posts.values():
        post_data["related"] = get_related(post_data, all_posts)

    # ---- Build sorted tag list for search page dropdown ----
    all_tags = sorted(
        set(t for p in all_posts.values() for t in p["tags"])
    )

    # ---- Build LANG_GROUPS: base_url → {lang: url_path} ----
    # For regular posts: base_url = base_url_path (slug-derived, no lang suffix)
    # For homepage/listing: the served URL is section_url, not url_path (which
    # is slug-based and may contain Cyrillic).  Strip the lang suffix from
    # section_url to get the base key.
    lang_groups = {}
    _all_pd = {
        **{r["post"]["url_path"]: r["post"] for r in section_routes.values()},
        **all_posts,
    }
    for _pd in _all_pd.values():
        _lang = _pd.get("lang", default_lang)
        _ptype = _pd.get("post_type", "")
        if _ptype in ("homepage", "listing"):
            _served = _pd.get("section_url") or _pd["url_path"]
            if _lang != default_lang:
                # Strip trailing "/" + lang_code to get the base
                _base = _served.rsplit("/" + _lang, 1)[0] or "/"
            else:
                _base = _served
            _value = _served
        else:
            _base = _pd.get("base_url_path") or _pd["url_path"]
            _value = _pd["url_path"]
        if _base not in lang_groups:
            lang_groups[_base] = {}
        lang_groups[_base][_lang] = _value

    # Collect all language codes; default_lang first, then others sorted
    _seen = {default_lang}
    _others = []
    for _pd in _all_pd.values():
        _l = _pd.get("lang", default_lang)
        if _l not in _seen:
            _seen.add(_l)
            _others.append(_l)
    available_langs = [default_lang] + sorted(_others)

    # ---- Build icon/site-title override map for cascade inheritance ----
    # Section routes are keyed by their *section URL* (e.g. "/onyxfolio"), not
    # by the homepage file's slug path — that's what the cascade lookup uses.
    icon_overrides = {}
    for section_url, route in section_routes.items():
        meta = route["post"].get("metadata", {})
        icon = meta.get("icon") or None
        st = meta.get("site_title") or None
        if icon or st:
            icon_overrides[section_url] = {"icon": icon, "site_title": st}
    for url_path, post_data in all_posts.items():
        meta = post_data.get("metadata", {})
        icon = meta.get("icon") or None
        st = meta.get("site_title") or None
        if icon or st:
            icon_overrides[url_path] = {"icon": icon, "site_title": st}

    menu_posts.sort(key=lambda x: x["menu_order"])
    return (all_posts, section_routes, website_name, site_theme, dataview_index,
            private_routes, menu_posts, show_search, show_tags, all_tags,
            icon_overrides, default_lang, available_langs, lang_groups,
            social_links)


# =========================================
# AUTO RELOAD
# =========================================

def force_reload():
    """Reset scan timestamps so maybe_reload() reloads on the next request."""
    global LAST_SCAN_TIME, _last_check_time
    LAST_SCAN_TIME = 0
    _last_check_time = 0


def maybe_reload():
    global ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, SITE_THEME, DATAVIEW_INDEX, \
        PRIVATE_ROUTES, MENU_POSTS, SHOW_SEARCH, SHOW_TAGS, ALL_TAGS, ICON_OVERRIDES, \
        DEFAULT_LANG, AVAILABLE_LANGS, LANG_GROUPS, SOCIAL_LINKS, \
        LAST_SCAN_TIME, _last_check_time

    if time.time() - _last_check_time < 2.0:
        return

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

        _last_check_time = time.time()
        if newest > LAST_SCAN_TIME:
            print("Reloading vault...")
            (ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, SITE_THEME,
             DATAVIEW_INDEX, PRIVATE_ROUTES, MENU_POSTS,
             SHOW_SEARCH, SHOW_TAGS, ALL_TAGS, ICON_OVERRIDES,
             DEFAULT_LANG, AVAILABLE_LANGS, LANG_GROUPS,
             SOCIAL_LINKS) = load_posts()
            LAST_SCAN_TIME = newest
    except Exception as e:
        print(f"Reload error (serving stale data): {e}", file=sys.stderr)
    finally:
        _reload_lock.release()
