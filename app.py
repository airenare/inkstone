import hashlib
import hmac
import html
import os
import subprocess
from datetime import datetime, timezone

from flask import Flask, render_template, abort, request, send_from_directory, \
    Response, redirect

import posts as post_store
from config import (
    VAULT_PATH, VERSION, WEBHOOK_SECRET,
    HIDE_ATTRIBUTION,
    GISCUS_REPO, GISCUS_REPO_ID, GISCUS_CATEGORY_ID,
)
from view_helpers import build_breadcrumbs, get_adjacent_posts, get_related, highlight


# =========================================
# APP
# =========================================

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static",
)


def _detect_current_lang(path):
    """Return the language code if the last path segment is a known non-default
    language code, otherwise return DEFAULT_LANG."""
    if not path or path == "/":
        return post_store.DEFAULT_LANG
    last = path.rstrip("/").rsplit("/", 1)[-1]
    if (last in post_store.AVAILABLE_LANGS
            and last != post_store.DEFAULT_LANG):
        return last
    return post_store.DEFAULT_LANG


def _resolve_icon_override(url_path):
    """Walk up the URL hierarchy to find the nearest icon/site_title override.

    Returns {"icon": str|None, "site_title": str|None} for the most specific
    ancestor (including the page itself) that has set either field, or both
    values None if no ancestor has set anything.
    """
    overrides = post_store.ICON_OVERRIDES
    # Check from most-specific (current URL) up to root "/"
    parts = url_path.rstrip("/").split("/")
    # Generate candidate paths from most- to least-specific
    candidates = []
    for i in range(len(parts), 0, -1):
        candidates.append("/".join(parts[:i]) or "/")
    candidates.append("/")
    for candidate in candidates:
        if candidate in overrides:
            ov = overrides[candidate]
            icon = ov.get("icon")
            st = ov.get("site_title")
            # Build icon URL: vault-relative path served via /attachments/
            # Absolute paths (e.g. /static/logo.svg) and full URLs used as-is;
            # relative paths are resolved via the /attachments/ route.
            if icon.startswith("/") or icon.startswith("http"):
                icon_url = icon
            else:
                icon_url = f"/attachments/{icon}"
            return {"header_icon": icon_url, "header_site_title": st}
    return {"header_icon": None, "header_site_title": None}


@app.context_processor
def inject_globals():
    current_lang = _detect_current_lang(request.path)
    multilingual = len(post_store.AVAILABLE_LANGS) > 1

    # Language-aware top-level nav sections — (url, label) tuples
    if not multilingual or current_lang == post_store.DEFAULT_LANG:
        top_sections = sorted(
            (url, route["post"].get("title", url.lstrip("/").title()))
            for url, route in post_store.SECTION_ROUTES.items()
            if url not in ("/", f"/{current_lang}")
            and url.count("/") == 1
            and route.get("lang", post_store.DEFAULT_LANG) == post_store.DEFAULT_LANG
        )
    else:
        # Non-default language: show sections at /{section}/{lang}
        top_sections = sorted(
            (url, route["post"].get("title", url.lstrip("/").title()))
            for url, route in post_store.SECTION_ROUTES.items()
            if route.get("lang") == current_lang
            and url.count("/") == 2
        )

    # Language-aware menu posts; fall back to default lang if none found
    lang_menu = [p for p in post_store.MENU_POSTS
                 if p.get("lang", post_store.DEFAULT_LANG) == current_lang]
    if not lang_menu and current_lang != post_store.DEFAULT_LANG:
        lang_menu = [p for p in post_store.MENU_POSTS
                     if p.get("lang", post_store.DEFAULT_LANG) == post_store.DEFAULT_LANG]

    # Language variants for the toggle: base_url → {lang: url}
    base_url = request.path.rstrip("/") or "/"
    if multilingual and current_lang != post_store.DEFAULT_LANG:
        base_url = base_url.rsplit("/", 1)[0] or "/"
    lang_variants = post_store.LANG_GROUPS.get(base_url, {}) if multilingual else {}

    icon_ctx = _resolve_icon_override(request.path)
    return {
        "website_name": post_store.WEBSITE_NAMES.get(current_lang) or post_store.WEBSITE_NAME,
        "nav_sections": top_sections,
        "menu_posts": lang_menu,
        "show_search": post_store.SHOW_SEARCH,
        "show_tags": post_store.SHOW_TAGS,
        "current_url": request.url,
        "canonical_url": request.base_url,
        "app_version": VERSION,
        "theme_css": f"theme-{post_store.SITE_THEME}.css",
        "header_icon": icon_ctx["header_icon"],
        "header_site_title": icon_ctx["header_site_title"],
        "current_lang": current_lang,
        "default_lang": post_store.DEFAULT_LANG,
        "available_langs": post_store.AVAILABLE_LANGS,
        "lang_variants": lang_variants,
        "hide_attribution": HIDE_ATTRIBUTION,
        "social_links": post_store.SOCIAL_LINKS,
        "giscus_config": {
            "repo": GISCUS_REPO,
            "repo_id": GISCUS_REPO_ID,
            "category_id": GISCUS_CATEGORY_ID,
        } if GISCUS_REPO and GISCUS_REPO_ID and GISCUS_CATEGORY_ID else None,
        "ui_strings": post_store.UI_TRANSLATIONS.get(current_lang, {}),
    }


# =========================================
# ROUTES
# =========================================

@app.route("/webhook", methods=["POST"])
def vault_webhook():
    if WEBHOOK_SECRET:
        sig = request.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(
            WEBHOOK_SECRET.encode(), request.data, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            abort(403)
    else:
        print("WARNING: /webhook called but WEBHOOK_SECRET is not set.", flush=True)

    if os.path.isdir(os.path.join(VAULT_PATH, ".git")):
        try:
            result = subprocess.run(
                ["git", "-C", VAULT_PATH, "pull", "--ff-only"],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode != 0:
                print(f"git pull failed: {result.stderr}", flush=True)
                return Response(result.stderr, status=500)
            print(f"git pull: {result.stdout.strip()}", flush=True)
        except subprocess.TimeoutExpired:
            return Response("git pull timed out", status=500)

    post_store.force_reload()
    return Response("ok", status=200)


@app.route("/attachments/<path:path>")
def attachments(path):
    return send_from_directory(VAULT_PATH, path)


# Favicon: vault root overrides (favicon.ico / favicon.png / favicon.svg),
# falling back to the built-in OnyxFolio defaults in frontend/static/.
_FAVICON_CANDIDATES = ["favicon.ico", "favicon.png", "favicon.svg"]

# Map each route to the static fallback filename and MIME type
_FAVICON_DEFAULTS = {
    "/favicon.ico": ("favicon.ico", "image/x-icon"),
    "/favicon.png": ("favicon-32.png", "image/png"),
    "/favicon.svg": ("logo.svg", "image/svg+xml"),
}


@app.route("/favicon.ico")
@app.route("/favicon.png")
@app.route("/favicon.svg")
def favicon():
    for name in _FAVICON_CANDIDATES:
        vault_favicon = os.path.join(VAULT_PATH, name)
        if os.path.isfile(vault_favicon):
            return send_from_directory(VAULT_PATH, name)
    # Default: serve the matching built-in asset with the correct MIME type
    static_name, mime = _FAVICON_DEFAULTS[request.path]
    return send_from_directory(app.static_folder, static_name, mimetype=mime)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


def _build_rss_xml(title, link, description, posts, base):
    """Build a complete RSS XML string from a filtered, sorted post list."""
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for p in posts:
        pub = p["date"].strftime("%a, %d %b %Y %H:%M:%S +0000") if p["date"] else ""
        post_link = base + p["url_path"]
        items.append(
            f"    <item>\n"
            f"      <title>{html.escape(p['title'])}</title>\n"
            f"      <link>{post_link}</link>\n"
            f"      <guid>{post_link}</guid>\n"
            f"      <pubDate>{pub}</pubDate>\n"
            f"      <description>{html.escape(p['summary'])}</description>\n"
            f"    </item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        f"    <title>{html.escape(title)}</title>\n"
        f"    <link>{link}</link>\n"
        f"    <description>{html.escape(description)}</description>\n"
        f"    <lastBuildDate>{now}</lastBuildDate>\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>"
    )


@app.route("/feed.xml")
def rss_feed():
    post_store.maybe_reload()
    posts = sorted(
        post_store.ALL_POSTS.values(),
        key=lambda p: p["date"] or datetime.min,
        reverse=True,
    )[:20]
    base = request.url_root.rstrip("/")
    xml = _build_rss_xml(
        post_store.WEBSITE_NAME, base + "/", post_store.WEBSITE_NAME, posts, base
    )
    return Response(xml, mimetype="application/rss+xml")


@app.route("/<path:section>/feed.xml")
def section_rss_feed(section):
    post_store.maybe_reload()
    section = section.strip("/")
    section_url = "/" + section
    if section_url not in post_store.SECTION_ROUTES:
        abort(404)
    section_title = post_store.SECTION_ROUTES[section_url]["post"]["title"]
    posts = sorted(
        [p for p in post_store.ALL_POSTS.values()
         if p["section"] == section
         or p["section"].startswith(section + "/")],
        key=lambda p: p["date"] or datetime.min,
        reverse=True,
    )[:20]
    base = request.url_root.rstrip("/")
    feed_title = f"{section_title} \u2014 {post_store.WEBSITE_NAME}"
    xml = _build_rss_xml(
        feed_title, base + section_url, feed_title, posts, base
    )
    return Response(xml, mimetype="application/rss+xml")


@app.route("/tags")
def tags_index():
    post_store.maybe_reload()
    tag_counts = {}
    for p in post_store.ALL_POSTS.values():
        for tag in p.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    tags = sorted(tag_counts.items())
    return render_template("labels.html", labels=tags)


@app.route("/sitemap.xml")
def sitemap():
    post_store.maybe_reload()
    base = request.url_root.rstrip("/")
    locs = [base + "/"]
    for url in sorted(post_store.SECTION_ROUTES):
        if url != "/":
            locs.append(base + url)
    for url in sorted(post_store.ALL_POSTS):
        locs.append(base + url)
    url_tags = "\n".join(
        f"  <url><loc>{loc}</loc></url>" for loc in locs
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + url_tags
        + "\n</urlset>"
    )
    return Response(xml, mimetype="application/xml")



@app.route("/tag/<tag>")
def tag_archive(tag):
    post_store.maybe_reload()
    tag_lower = tag.lower()
    posts = sorted(
        (p for p in post_store.ALL_POSTS.values()
         if tag_lower in p.get("tags", [])),
        key=lambda p: p["date"] or datetime.min,
        reverse=True,
    )
    if not posts:
        abort(404)
    # Build per-post prev/next within this tag (older ← / → newer)
    nav = {}
    for i, p in enumerate(posts):
        nav[p["url_path"]] = {
            "prev": posts[i + 1] if i + 1 < len(posts) else None,  # older
            "next": posts[i - 1] if i > 0 else None,               # newer
        }
    return render_template("tag.html", tag=tag, posts=posts, tag_nav=nav)


@app.route("/search")
def search():
    post_store.maybe_reload()
    q = request.args.get("q", "").strip()
    label_filter = request.args.get("tag", "").strip().lower()

    all_tags = post_store.ALL_TAGS

    results = []
    if q or label_filter:
        q_lower = q.lower()
        for p in post_store.ALL_POSTS.values():
            if label_filter and label_filter not in p.get("tags", []):
                continue
            if q_lower and q_lower not in p["title"].lower() \
                    and q_lower not in p["content"]:
                continue
            results.append({
                **p,
                "highlighted_title": highlight(p["title"], q),
                "highlighted_summary": highlight(p["summary"], q),
            })

    return render_template(
        "search.html",
        posts=results,
        query=q,
        selected_tag=label_filter,
        all_tags=all_tags,
    )


def _page_theme_css(post):
    """Return theme_css for a page if it overrides the site theme, else None."""
    raw = post.get("metadata", {}).get("theme")
    if not raw:
        return None
    return f"theme-{post_store._resolve_theme(raw, post.get('url_path', ''))}.css"


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    post_store.maybe_reload()

    url_path = "/" + path if path else "/"

    # 1. Section routes (homepage or listing)
    if url_path in post_store.SECTION_ROUTES:
        route = post_store.SECTION_ROUTES[url_path]

        if route["type"] == "listing":
            section = route["section"]
            if section:
                section_posts = [
                    p for p in post_store.ALL_POSTS.values()
                    if p["section"] == section
                    or p["section"].startswith(section + "/")
                ]
            else:
                section_posts = list(post_store.ALL_POSTS.values())

            # Deduplicate: for each logical post, show the version matching the
            # listing's language. Falls back to DEFAULT_LANG if no match.
            _route_lang = route.get("lang", post_store.DEFAULT_LANG)
            _by_base = {}
            for _p in section_posts:
                _base = _p.get("base_url_path") or _p["url_path"]
                _by_base.setdefault(_base, {})[_p.get("lang", post_store.DEFAULT_LANG)] = _p
            _deduped = []
            for _base, _versions in _by_base.items():
                if _route_lang in _versions:
                    _deduped.append(_versions[_route_lang])
                elif post_store.DEFAULT_LANG in _versions:
                    _deduped.append(_versions[post_store.DEFAULT_LANG])
                else:
                    _deduped.append(next(iter(_versions.values())))
            section_posts = _deduped

            section_posts.sort(
                key=lambda x: x["date"] or datetime.min, reverse=True
            )
            featured = sorted(
                [p for p in section_posts if p["featured"]],
                key=lambda x: (
                    x["priority"],
                    -(x["date"].timestamp() if x["date"] else 0),
                ),
            )
            regular = [p for p in section_posts if not p["featured"]]

            page_size = 20
            page = max(1, request.args.get("page", 1, type=int))
            total_pages = max(1, (len(regular) + page_size - 1) // page_size)
            page = min(page, total_pages)
            regular_page = regular[(page - 1) * page_size: page * page_size]

            extra = {}
            if page_theme := _page_theme_css(route["post"]):
                extra["theme_css"] = page_theme
            return render_template(
                "listing.html",
                featured=featured,
                regular=regular_page,
                listing=route["post"],
                page=page,
                total_pages=total_pages,
                **extra,
            )

        else:  # homepage
            extra = {}
            if page_theme := _page_theme_css(route["post"]):
                extra["theme_css"] = page_theme
            return render_template("index.html", homepage=route["post"], **extra)

    # 2. Regular posts
    if url_path in post_store.ALL_POSTS:
        post = post_store.ALL_POSTS[url_path]
        back_url = "/" + post["section"] if post["section"] else "/"
        template = "book.html" if post.get("post_type") == "book" else "post.html"
        breadcrumbs = build_breadcrumbs(url_path, post["title"], post_store.SECTION_ROUTES)
        related = post.get("related", [])
        prev_post, next_post = get_adjacent_posts(post, post_store.ALL_POSTS)
        extra = {}
        if page_theme := _page_theme_css(post):
            extra["theme_css"] = page_theme
        return render_template(
            template, post=post, back_url=back_url,
            breadcrumbs=breadcrumbs, related=related,
            prev_post=prev_post, next_post=next_post,
            **extra,
        )

    # 3. Private note placeholder
    if url_path in post_store.PRIVATE_ROUTES:
        entry = post_store.PRIVATE_ROUTES[url_path]
        parent = url_path.rsplit("/", 1)[0]
        back_url = parent if parent else "/"
        return render_template("private.html", entry=entry, back_url=back_url)

    # 4. Multilingual fallbacks (only when multiple languages are configured)
    if len(post_store.AVAILABLE_LANGS) > 1:
        last_seg = url_path.rstrip("/").rsplit("/", 1)[-1]
        base = url_path.rstrip("/").rsplit("/", 1)[0] or "/"

        # 4a. Requested a lang variant that has no translation → redirect to default
        if (last_seg in post_store.AVAILABLE_LANGS
                and last_seg != post_store.DEFAULT_LANG
                and (base in post_store.ALL_POSTS
                     or base in post_store.SECTION_ROUTES)):
            return redirect(base, 302)

        # 4b. Base URL exists only in non-default languages → "not translated" page
        if url_path in post_store.LANG_GROUPS:
            variants = post_store.LANG_GROUPS[url_path]
            if post_store.DEFAULT_LANG not in variants and variants:
                return render_template(
                    "not_translated.html",
                    lang_variants=variants,
                    current_lang=post_store.DEFAULT_LANG,
                    default_lang=post_store.DEFAULT_LANG,
                ), 200

    abort(404)


# =========================================
# START
# =========================================

if __name__ == "__main__":
    (
        post_store.ALL_POSTS,
        post_store.SECTION_ROUTES,
        post_store.WEBSITE_NAME,
        post_store.SITE_THEME,
        post_store.DATAVIEW_INDEX,
        post_store.PRIVATE_ROUTES,
        post_store.MENU_POSTS,
        post_store.SHOW_SEARCH,
        post_store.SHOW_TAGS,
        post_store.ALL_TAGS,
        post_store.ICON_OVERRIDES,
        post_store.DEFAULT_LANG,
        post_store.AVAILABLE_LANGS,
        post_store.LANG_GROUPS,
        post_store.SOCIAL_LINKS,
        post_store.WEBSITE_NAMES,
        post_store.UI_TRANSLATIONS,
    ) = post_store.load_posts()
    app.run("127.0.0.1", 8000, debug=True)
