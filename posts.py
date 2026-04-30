import json
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
from bases import parse_base_config, render_base_view
from canvas import render_canvas


# url_path → post dict (content posts only, not homepage/listing files)
ALL_POSTS = {}
# section root url → {"type": "homepage"|"listing", "post": post_dict, "section": str}
SECTION_ROUTES = {}
WEBSITE_NAME = "My Blog"
# lang_code → site title for that language's root homepage
WEBSITE_NAMES: dict = {}
# lang_code → {key: translated_string} — loaded from `type: translations` vault notes
UI_TRANSLATIONS: dict = {}
# filepath → {metadata, tags, file} for ALL vault notes (feeds Dataview queries)
DATAVIEW_INDEX = {}
# url_path → dataview entry for notes that exist but are NOT published as web pages
PRIVATE_ROUTES = {}
# url_path → rendered post_data for private notes (served when ACCESS_TOKEN auth passes)
PRIVATE_RENDERED: dict = {}
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
# Default dark/light mode for visitors with no saved preference: "dark", "light", or "system"
DEFAULT_THEME: str = "system"
# Social links built from per-platform keys on the root homepage frontmatter
# (e.g. github:, mastodon:, bluesky:). Each entry: {name, icon, handle, url, rel}.
SOCIAL_LINKS: list = []

_VALID_THEMES = {"obsidian", "omarchy"}

# ── Social network registry ───────────────────────────────────────────────────
# Keys are the exact frontmatter field names users set on the root homepage,
# e.g.  github: https://github.com/you
#        mastodon: https://mastodon.social/@you
# icon:  Simple Icons SVG path (viewBox="0 0 24 24")
# rel:   link rel attribute (me noopener for identity-verifiable networks)
# handle: callable(url) → display string shown next to the icon

def _last_segment(url):
    """Return the last non-empty path segment of a URL."""
    seg = url.rstrip("/").rsplit("/", 1)[-1]
    return seg if seg else url


def _at(url):
    """Last segment, ensuring it starts with @."""
    seg = _last_segment(url)
    return seg if seg.startswith("@") else "@" + seg


_SOCIAL_REGISTRY = {
    "github": {
        "name": "GitHub",
        "rel": "me noopener",
        "handle": _at,
        "icon": (
            "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 "
            "11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338"
            ".724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c"
            "-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236"
            " 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605"
            "-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22"
            "-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267"
            " 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285"
            "-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91"
            " 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 "
            "2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565"
            " 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
        ),
    },
    "mastodon": {
        "name": "Mastodon",
        "rel": "me noopener",
        "handle": _at,
        "icon": (
            "M23.268 5.313c-.35-2.578-2.617-4.61-5.304-5.004C17.51.242 "
            "15.792 0 11.813 0h-.03c-3.98 0-4.835.242-5.288.309C3.882.692 "
            "1.496 2.518.917 5.127.64 6.412.61 7.837.661 9.143c.074 1.874"
            ".088 3.745.26 5.611.118 1.24.325 2.47.62 3.68.55 2.237 2.777 "
            "4.098 4.96 4.857 2.336.792 4.849.923 7.256.38.265-.061.527"
            "-.132.786-.213.585-.184 1.27-.39 1.774-.753a.057.057 0 0 0 "
            ".023-.043v-1.809a.052.052 0 0 0-.02-.041.053.053 0 0 0-.046"
            "-.01 20.282 20.282 0 0 1-4.709.545c-2.73 0-3.463-1.284-3.674"
            "-1.818a5.593 5.593 0 0 1-.319-1.433.053.053 0 0 1 .066-.054c"
            "1.517.363 3.072.546 4.632.546.376 0 .75 0 1.125-.01 1.57-.044"
            " 3.224-.124 4.768-.422.038-.008.077-.015.11-.024 2.435-.464 "
            "4.753-1.92 4.989-5.604.008-.145.03-1.52.03-1.67.002-.512.167"
            "-3.63-.024-5.545zm-3.748 9.195h-2.561V8.29c0-1.309-.55-1.976"
            "-1.67-1.976-1.23 0-1.846.79-1.846 2.35v3.403h-2.546V8.663c0"
            "-1.56-.617-2.35-1.848-2.35-1.112 0-1.668.668-1.67 1.977v6.218"
            "H4.822V8.102c0-1.31.337-2.35 1.011-3.12.696-.77 1.608-1.164 "
            "2.74-1.164 1.311 0 2.302.5 2.962 1.498l.638 1.06.638-1.06c.66"
            "-.999 1.65-1.498 2.96-1.498 1.13 0 2.043.395 2.74 1.164.675"
            ".77 1.012 1.81 1.012 3.12z"
        ),
    },
    "bluesky": {
        "name": "Bluesky",
        "rel": "me noopener",
        "handle": lambda url: "@" + _last_segment(url).removesuffix(".bsky.social"),
        "icon": (
            "M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561"
            " 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 "
            "6.479.815 2.736 3.713 3.66 6.383 3.364.136-.02.275-.039.415"
            "-.056-.138.022-.276.04-.415.056-3.912.58-7.387 2.005-2.83 "
            "7.078 5.013 5.19 6.87-1.113 7.823-4.308.953 3.195 2.05 9.271 "
            "7.733 4.308 4.267-4.308 1.172-6.498-2.74-7.078a8.741 8.741 0 "
            "0 1-.415-.056c.14.017.279.036.415.056 2.67.297 5.568-.628 "
            "6.383-3.364.246-.828.624-5.79.624-6.478 0-.69-.139-1.861-.902"
            "-2.204-.659-.298-1.664-.62-4.3 1.24C16.046 4.748 13.087 8.687 "
            "12 10.8z"
        ),
    },
    "twitter": {
        "name": "X / Twitter",
        "rel": "noopener",
        "handle": _at,
        "icon": (
            "M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231"
            "-5.401 6.231H2.748l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm"
            "-1.161 17.52h1.833L7.084 4.126H5.117z"
        ),
    },
    "instagram": {
        "name": "Instagram",
        "rel": "noopener",
        "handle": _at,
        "icon": (
            "M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c"
            "-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905"
            ".131 5.775.072 7.053.012 8.333 0 8.74 0 12c0 3.259.014 3.668"
            ".072 4.948.058 1.28.261 2.148.558 2.913.306.788.717 1.459 "
            "1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499"
            " 2.913.558C8.333 23.988 8.74 24 12 24c3.259 0 3.668-.014 "
            "4.948-.072 1.28-.058 2.148-.261 2.913-.558.788-.306 1.459-.718"
            " 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499"
            "-1.636.558-2.913.06-1.28.072-1.687.072-4.947 0-3.259-.014"
            "-3.667-.072-4.947-.06-1.277-.262-2.149-.558-2.913-.306-.789"
            "-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765"
            "-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c"
            "3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562"
            ".217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 "
            "1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 "
            "4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 "
            "1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413"
            "-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074"
            "-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379"
            "-.899-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235"
            "-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861"
            ".061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419"
            ".81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 "
            "1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162"
            " 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 "
            "6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4"
            "-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm6.406-11.845c"
            "-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 "
            "1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"
        ),
    },
    "linkedin": {
        "name": "LinkedIn",
        "rel": "noopener",
        # LinkedIn profile URLs are /in/username — strip the /in/ segment
        "handle": lambda url: _last_segment(url),
        "icon": (
            "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037"
            "-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h"
            ".046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 "
            "5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0"
            "-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 "
            "1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v"
            "11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227"
            ".792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 "
            ".774 23.2 0 22.222 0h.003z"
        ),
    },
    "facebook": {
        "name": "Facebook",
        "rel": "noopener",
        "handle": _last_segment,
        "icon": (
            "M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 "
            "4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0"
            "-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v"
            "2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 "
            "3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
        ),
    },
    "youtube": {
        "name": "YouTube",
        "rel": "noopener",
        "handle": _at,
        "icon": (
            "M23.495 6.205a3.007 3.007 0 0 0-2.088-2.088c-1.87-.501-9.396"
            "-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 0 0 .527 "
            "6.205a31.247 31.247 0 0 0-.522 5.805 31.247 31.247 0 0 0 .522"
            " 5.783 3.007 3.007 0 0 0 2.088 2.088c1.868.502 9.396.502 "
            "9.396.502s7.506 0 9.396-.502a3.007 3.007 0 0 0 2.088-2.088 "
            "31.247 31.247 0 0 0 .5-5.783 31.247 31.247 0 0 0-.5-5.805z"
            "M9.609 15.601V8.408l6.264 3.602z"
        ),
    },
}


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
    website_names = {}
    site_theme = "obsidian"
    default_theme = "system"
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

    ui_translations = {}

    # ---- Pass 1: scan ALL .md files — build dataview_index + candidates ----
    candidates = []
    candidates_base = []  # (.base files with website: true)
    candidates_canvas = []  # (.canvas files with "website": true)
    url_index = {}  # slugify(title) → url_path, used to resolve wiki-links
    dataview_index = {}  # filepath → dataview context (all vault notes)

    for root, dirs, files in os.walk(VAULT_PATH):
        dirs[:] = [d for d in dirs if d.lower() != "templates"]
        for f in files:
            if f.endswith(".base"):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, encoding="utf-8") as fh:
                        text = fh.read()
                except OSError as e:
                    print(f"Skipping {filepath}: {e}", file=sys.stderr)
                    continue
                base_config = parse_base_config(text, filepath)
                if not base_config.get("website"):
                    continue
                stem = f[:-5]  # strip .base
                title = base_config.get("title") or stem
                slug = slugify(str(base_config.get("slug") or title))
                section = _section_from_filepath(filepath)
                url_path = ("/" + section + "/" + slug) if section else ("/" + slug)
                url_index[slugify(title).lower()] = url_path
                url_index[slugify(stem).lower()] = url_path
                url_index[slug.lower()] = url_path
                candidates_base.append(
                    (filepath, f, base_config, title, slug, section, url_path)
                )
                continue

            if f.endswith(".canvas"):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, encoding="utf-8") as fh:
                        data = json.load(fh)
                except Exception:
                    continue
                if not data.get("website"):
                    continue
                stem = f[:-7]  # strip .canvas
                title = data.get("title") or stem
                slug = slugify(str(data.get("slug") or title))
                section = _section_from_filepath(filepath)
                url_path = ("/" + section + "/" + slug) if section else ("/" + slug)
                url_index[slugify(title).lower()] = url_path
                url_index[slugify(stem).lower()] = url_path
                url_index[slug.lower()] = url_path
                candidates_canvas.append(
                    (filepath, f, data, title, slug, section, url_path)
                )
                continue

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

            # Detect translation-table notes (don't need website: true)
            if (metadata.get("type") or "").strip().lower() == "translations":
                note_lang = str(metadata.get("lang") or "").strip().lower()
                if not note_lang:
                    print(
                        f"WARNING: translation note {filepath} skipped "
                        f"(missing lang:).",
                        file=sys.stderr,
                    )
                    continue
                # Prefer a fenced ```yaml block in the body over the
                # legacy strings: frontmatter dict.
                strings_raw = None
                yaml_block = re.search(
                    r"^```yaml\s*\n(.*?)^```",
                    md,
                    re.MULTILINE | re.DOTALL,
                )
                if yaml_block:
                    try:
                        strings_raw = yaml.safe_load(yaml_block.group(1))
                    except yaml.YAMLError as exc:
                        print(
                            f"WARNING: translation note {filepath} — "
                            f"YAML block parse error: {exc}",
                            file=sys.stderr,
                        )
                elif isinstance(metadata.get("strings"), dict):
                    strings_raw = metadata["strings"]
                if isinstance(strings_raw, dict):
                    if note_lang in ui_translations:
                        print(
                            f"WARNING: duplicate translation note for lang "
                            f"'{note_lang}' in {filepath} — overwriting.",
                            file=sys.stderr,
                        )
                    ui_translations[note_lang] = {
                        str(k): str(v) for k, v in strings_raw.items()
                    }
                else:
                    print(
                        f"WARNING: translation note {filepath} skipped "
                        f"(no valid yaml block or strings: dict found).",
                        file=sys.stderr,
                    )
                continue

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
                                section, url_path, lang, base_url_path,
                                base_stem.lower()))

    # ---- Pass 2: render markdown with resolved wiki-links + dataview ----
    for (filepath, f, metadata, md, title, slug,
         section, url_path, lang, base_url_path, base_stem) in candidates:

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
            "base_stem": base_stem,
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
            if section == "":
                website_names[lang] = title
            if section == "" and lang == default_lang:
                website_name = title
                show_search = bool(metadata.get("show_search"))
                show_tags = bool(metadata.get("show_tags"))
                site_theme = _resolve_theme(
                    metadata.get("theme"), filepath
                )
                _dt = str(metadata.get("default_theme") or "system").lower()
                default_theme = _dt if _dt in {"dark", "light", "system"} else "system"
                social_links = []
                for key, network in _SOCIAL_REGISTRY.items():
                    url = metadata.get(key)
                    if not url or not isinstance(url, str):
                        continue
                    url = url.strip()
                    if not url.startswith("http"):
                        continue
                    try:
                        handle = network["handle"](url)
                    except Exception:
                        handle = url
                    social_links.append({
                        "name": network["name"],
                        "icon": network["icon"],
                        "handle": handle,
                        "url": url,
                        "rel": network["rel"],
                    })
            section_routes[section_url] = {
                "type": "homepage",
                "post": post_data,
                "lang": lang,
            }
        else:
            all_posts[url_path] = post_data

    # ---- Pass 3: render .base database views ----
    for (filepath, f, base_config, title, slug, section, url_path) in candidates_base:
        html = render_base_view(base_config, dataview_index)
        date = _parse_date(base_config.get("date"), filepath)
        raw_tags = base_config.get("tags") or []
        try:
            tags = sorted(str(t).lower() for t in raw_tags)
        except Exception:
            tags = []
        author_raw = base_config.get("author")
        if isinstance(author_raw, str):
            author = [author_raw] if author_raw.strip() else []
        elif isinstance(author_raw, list):
            author = [str(a) for a in author_raw if a]
        else:
            author = []
        section_url = ("/" + section) if section else "/"
        summary = base_config.get("summary") or ""
        post_data = {
            "url_path": url_path,
            "base_url_path": url_path,
            "lang": default_lang,
            "section": section,
            "section_url": section_url,
            "slug": slug,
            "title": title,
            "date": date,
            "updated": None,
            "author": author,
            "html": html,
            "toc": "",
            "reading_time": 0,
            "post_type": "base",
            "tags": tags,
            "content": "",
            "summary": summary,
            "priority": float("inf"),
            "featured": bool(base_config.get("featured")),
            "banner": base_config.get("banner"),
            "banner_x": base_config.get("banner_x"),
            "banner_y": base_config.get("banner_y"),
            "metadata": base_config,
        }
        all_posts[url_path] = post_data
        print(f"Loaded base: {title} | {url_path}")

    # ---- Pass 4: render .canvas visual boards ----
    for (filepath, f, data, title, slug, section, url_path) in candidates_canvas:
        html = render_canvas(filepath, url_index)
        date = _parse_date(data.get("date"), filepath)
        raw_tags = data.get("tags") or []
        try:
            tags = sorted(str(t).lower() for t in raw_tags)
        except Exception:
            tags = []
        section_url = ("/" + section) if section else "/"
        post_data = {
            "url_path": url_path,
            "base_url_path": url_path,
            "lang": default_lang,
            "section": section,
            "section_url": section_url,
            "slug": slug,
            "title": title,
            "date": date,
            "updated": None,
            "author": [],
            "html": html,
            "toc": "",
            "reading_time": 0,
            "post_type": "canvas",
            "tags": tags,
            "content": "",
            "summary": data.get("summary") or "",
            "priority": float("inf"),
            "featured": bool(data.get("featured")),
            "banner": data.get("banner"),
            "banner_x": data.get("banner_x"),
            "banner_y": data.get("banner_y"),
            "metadata": data,
        }
        all_posts[url_path] = post_data
        print(f"Loaded canvas: {title} | {url_path}")

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

    # ---- Pass 2b: render private notes for authenticated guest access ----
    private_rendered = {}
    for _entry in dataview_index.values():
        _url = _entry.get("url_path")
        if not _url or _url in all_posts:
            continue
        _meta = _entry.get("metadata") or {}
        _note_type = (_meta.get("type") or "").strip().lower()
        if _note_type in ("translations", "homepage", "listing"):
            continue
        try:
            with open(_entry["filepath"], encoding="utf-8") as _fh:
                _text = _fh.read()
        except OSError:
            continue
        _, _md = parse_frontmatter(_text, _entry["filepath"])
        _html, _toc = render_markdown(
            _md, _entry["filepath"], url_index, dataview_index, _meta
        )
        _section = _entry.get("section") or ""
        _section_url = ("/" + _section) if _section else "/"
        _word_count = len(re.sub(r"<[^>]+>", "", _html).split())
        _author_raw = _meta.get("author")
        if isinstance(_author_raw, str):
            _author = [_author_raw] if _author_raw.strip() else []
        elif isinstance(_author_raw, list):
            _author = [str(a) for a in _author_raw if a]
        else:
            _author = []
        private_rendered[_url] = {
            "url_path": _url,
            "base_url_path": _url,
            "lang": default_lang,
            "section": _section,
            "section_url": _section_url,
            "title": _entry["title"],
            "date": _parse_date(_meta.get("date"), _entry["filepath"]),
            "updated": _parse_date(
                _meta.get("updated") or _meta.get("modified"), _entry["filepath"]
            ),
            "author": _author,
            "html": _html,
            "toc": _toc,
            "reading_time": max(1, _word_count // 200),
            "post_type": _note_type or "post",
            "tags": _entry.get("tags", []),
            "content": re.sub(r"<[^>]+>", "", _html).lower(),
            "summary": _meta.get("summary") or _make_summary(_html),
            "banner": _meta.get("banner") or "",
            "banner_x": _meta.get("banner_x", 0.5),
            "banner_y": _meta.get("banner_y", 0.4),
            "metadata": _meta,
            "related": [],
        }

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
    # Section routes are keyed by their *section URL* (e.g. "/inkstone"), not
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
    return (all_posts, section_routes, website_name, site_theme, default_theme,
            dataview_index, private_routes, private_rendered, menu_posts,
            show_search, show_tags, all_tags, icon_overrides, default_lang,
            available_langs, lang_groups, social_links, website_names,
            ui_translations)


# =========================================
# AUTO RELOAD
# =========================================

def force_reload():
    """Reset scan timestamps so maybe_reload() reloads on the next request."""
    global LAST_SCAN_TIME, _last_check_time
    LAST_SCAN_TIME = 0
    _last_check_time = 0


def maybe_reload():
    global ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, WEBSITE_NAMES, SITE_THEME, \
        DEFAULT_THEME, DATAVIEW_INDEX, PRIVATE_ROUTES, PRIVATE_RENDERED, MENU_POSTS, \
        SHOW_SEARCH, SHOW_TAGS, ALL_TAGS, ICON_OVERRIDES, DEFAULT_LANG, AVAILABLE_LANGS, \
        LANG_GROUPS, SOCIAL_LINKS, UI_TRANSLATIONS, LAST_SCAN_TIME, _last_check_time

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
            (ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, SITE_THEME, DEFAULT_THEME,
             DATAVIEW_INDEX, PRIVATE_ROUTES, PRIVATE_RENDERED, MENU_POSTS,
             SHOW_SEARCH, SHOW_TAGS, ALL_TAGS, ICON_OVERRIDES,
             DEFAULT_LANG, AVAILABLE_LANGS, LANG_GROUPS,
             SOCIAL_LINKS, WEBSITE_NAMES, UI_TRANSLATIONS) = load_posts()
            LAST_SCAN_TIME = newest
    except Exception as e:
        print(f"Reload error (serving stale data): {e}", file=sys.stderr)
    finally:
        _reload_lock.release()
