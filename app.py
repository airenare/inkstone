import hashlib
import hmac
import html
import os
import subprocess
from collections import Counter
from datetime import datetime, timezone

from flask import Flask, render_template, abort, request, send_from_directory, \
    Response, redirect, session
from werkzeug.middleware.proxy_fix import ProxyFix

import posts as post_store
from config import (
    VAULT_PATH, VERSION, WEBHOOK_SECRET,
    HIDE_ATTRIBUTION,
    GISCUS_REPO, GISCUS_REPO_ID, GISCUS_CATEGORY_ID,
    ACCESS_TOKEN, SECRET_KEY,
    vault_attachment_href,
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
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = SECRET_KEY


def _is_unlocked(url_path):
    """True if the session grants access to this specific private note.

    Access is granted either by a per-note token (stored as a list of
    unlocked URL paths in the session) or by the global ACCESS_TOKEN master
    key (stored as a single boolean flag).
    """
    if session.get("inkstone_access"):
        return True
    return url_path in session.get("inkstone_unlocked", [])


def _detect_current_lang(path):
    """Return the language code if the last path segment is a known non-default
    language code, otherwise return DEFAULT_LANG."""
    route = post_store.SECTION_ROUTES.get(path)
    if route and route.get("lang"):
        return route.get("lang")
    post = post_store.ALL_POSTS.get(path)
    if post and post.get("lang"):
        return post.get("lang")

    if not path or path == "/":
        return post_store.DEFAULT_LANG
    last = path.rstrip("/").rsplit("/", 1)[-1]
    if (last in post_store.AVAILABLE_LANGS
            and last != post_store.DEFAULT_LANG):
        return last
    # Utility routes (/search, /tags) carry lang as a query param
    lang_param = request.args.get("lang", "")
    if (lang_param in post_store.AVAILABLE_LANGS
            and lang_param != post_store.DEFAULT_LANG):
        return lang_param
    return post_store.DEFAULT_LANG


def _resolve_icon_override(url_path):
    """Walk up the URL hierarchy collecting per-field overrides independently.

    Each field (icon+site_title pair, show_search, show_tags) is taken from
    the most-specific ancestor that set it. Returns None for fields not set
    anywhere in the hierarchy.
    """
    overrides = post_store.ICON_OVERRIDES
    parts = url_path.rstrip("/").split("/")
    candidates = []
    for i in range(len(parts), 0, -1):
        candidates.append("/".join(parts[:i]) or "/")
    candidates.append("/")

    header_icon = None
    header_site_title = None
    header_home_url = None
    show_search = None
    show_tags = None

    for candidate in candidates:
        if candidate not in overrides:
            continue
        ov = overrides[candidate]
        if header_site_title is None:
            icon = ov.get("icon") or ""
            st = ov.get("site_title")
            if icon or st:
                header_site_title = st
                header_home_url = candidate
                if icon:
                    # Absolute paths and full URLs used as-is; relative paths
                    # are resolved via /attachments/.
                    if icon.startswith("/") or icon.startswith("http"):
                        header_icon = icon
                    else:
                        header_icon = vault_attachment_href(icon)
        if show_search is None and ov.get("show_search") is not None:
            show_search = ov["show_search"]
        if show_tags is None and ov.get("show_tags") is not None:
            show_tags = ov["show_tags"]

    return {
        "header_icon": header_icon,
        "header_site_title": header_site_title,
        "header_home_url": header_home_url,
        "show_search": show_search,
        "show_tags": show_tags,
    }


@app.context_processor
def inject_globals():
    current_lang = _detect_current_lang(request.path)
    multilingual = len(post_store.AVAILABLE_LANGS) > 1
    icon_ctx = _resolve_icon_override(request.path)
    # section_root is "/" at the top level, or e.g. "/docs" inside a section
    # with its own site_title — used to scope nav to the active level.
    section_root = icon_ctx["header_home_url"] or "/"

    def _in_section(url, extra_depth=0):
        """True if url is a direct child of section_root at extra_depth levels down."""
        if section_root == "/":
            return url.count("/") == 1 + extra_depth
        return (
            url.startswith(section_root + "/")
            and url.count("/") == section_root.count("/") + 1 + extra_depth
        )

    # Nav sections scoped to the active section level
    if not multilingual or current_lang == post_store.DEFAULT_LANG:
        top_sections = sorted(
            (url, route["post"].get("title", url.lstrip("/").title()))
            for url, route in post_store.SECTION_ROUTES.items()
            if url not in ("/", f"/{current_lang}")
            and _in_section(url)
            and route.get("lang", post_store.DEFAULT_LANG) == post_store.DEFAULT_LANG
            and not (route["post"].get("metadata") or {}).get("nav_hidden")
            and (route["post"].get("metadata") or {}).get("menu_order") is None
        )
    else:
        # Non-default language: sections live one level deeper (/{section}/{lang})
        top_sections = sorted(
            (url, route["post"].get("title", url.lstrip("/").title()))
            for url, route in post_store.SECTION_ROUTES.items()
            if route.get("lang") == current_lang
            and _in_section(url, extra_depth=1)
            and not (route["post"].get("metadata") or {}).get("nav_hidden")
            and (route["post"].get("metadata") or {}).get("menu_order") is None
        )

    # Menu posts scoped to the active section level
    def _menu_in_section(p):
        url = p["url_path"]
        if section_root == "/":
            return url.count("/") == 1
        return url.startswith(section_root + "/")

    lang_menu = [p for p in post_store.MENU_POSTS
                 if p.get("lang", post_store.DEFAULT_LANG) == current_lang
                 and _menu_in_section(p)]
    if not lang_menu and current_lang != post_store.DEFAULT_LANG:
        lang_menu = [p for p in post_store.MENU_POSTS
                     if p.get("lang", post_store.DEFAULT_LANG) == post_store.DEFAULT_LANG
                     and _menu_in_section(p)]

    # Language variants for the toggle: resolve by URL match so translated
    # pages with custom slugs (no /{lang} suffix) still map to the right group.
    base_url = request.path.rstrip("/") or "/"
    if multilingual:
        for group_base, variants in post_store.LANG_GROUPS.items():
            if variants.get(current_lang) == base_url:
                base_url = group_base
                break
    lang_variants = post_store.LANG_GROUPS.get(base_url, {}) if multilingual else {}

    ui_strings = post_store.UI_TRANSLATIONS.get(current_lang, {})

    def localize_date(date_obj):
        if not date_obj:
            return ""
        month_en = date_obj.strftime("%B")
        month = ui_strings.get(month_en, month_en)
        fmt = ui_strings.get("date_format", "{month} {day}, {year}")
        return fmt.format(month=month, day=date_obj.day, year=date_obj.year)

    return {
        "website_name": post_store.WEBSITE_NAMES.get(current_lang) or post_store.WEBSITE_NAME,
        "nav_sections": top_sections,
        "menu_posts": lang_menu,
        "show_search": (icon_ctx["show_search"]
                        if icon_ctx["show_search"] is not None
                        else post_store.SHOW_SEARCH),
        "show_tags": (icon_ctx["show_tags"]
                      if icon_ctx["show_tags"] is not None
                      else post_store.SHOW_TAGS),
        "current_url": request.url,
        "canonical_url": request.base_url,
        "app_version": VERSION,
        "theme_css": f"theme-{post_store.SITE_THEME}.css",
        "site_default_theme": post_store.DEFAULT_THEME,
        "header_icon": icon_ctx["header_icon"],
        "header_site_title": icon_ctx["header_site_title"],
        "header_home_url": icon_ctx["header_home_url"],
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
        "ui_strings": ui_strings,
        "localize_date": localize_date,
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


# Favicon: _favicons/ subfolder in vault root overrides built-in defaults.
# Legacy vault-root favicon.ico / favicon.png also honoured for compat.
_FAVICON_ROUTES = {
    "/favicon.ico":                ("favicon.ico",                "image/x-icon"),
    "/favicon-16x16.png":         ("favicon-16x16.png",          "image/png"),
    "/favicon-32x32.png":         ("favicon-32x32.png",          "image/png"),
    "/apple-touch-icon.png":      ("apple-touch-icon.png",       "image/png"),
    "/android-chrome-192x192.png":("android-chrome-192x192.png", "image/png"),
    "/android-chrome-512x512.png":("android-chrome-512x512.png", "image/png"),
    "/site.webmanifest":          ("site.webmanifest",           "application/manifest+json"),
}


def _serve_favicon(filename, static_fallback, mime):
    """Serve from _favicons/ in vault, then vault root (compat), then static."""
    for base in [os.path.join(VAULT_PATH, "_favicons"), VAULT_PATH]:
        path = os.path.join(base, filename)
        if os.path.isfile(path):
            return send_from_directory(os.path.dirname(path), filename)
    return send_from_directory(app.static_folder, static_fallback, mimetype=mime)


@app.route("/favicon.ico")
@app.route("/favicon-16x16.png")
@app.route("/favicon-32x32.png")
@app.route("/apple-touch-icon.png")
@app.route("/android-chrome-192x192.png")
@app.route("/android-chrome-512x512.png")
@app.route("/site.webmanifest")
def favicon():
    filename, mime = _FAVICON_ROUTES[request.path]
    return _serve_favicon(filename, filename, mime)


@app.route("/favicon.svg")
def favicon_svg():
    for base in [os.path.join(VAULT_PATH, "_favicons"), VAULT_PATH]:
        path = os.path.join(base, "favicon.svg")
        if os.path.isfile(path):
            return send_from_directory(os.path.dirname(path), "favicon.svg",
                                       mimetype="image/svg+xml")
    return not_found(None)


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
    section = request.args.get("section", "").rstrip("/")
    tag_counts = {}
    for p in post_store.ALL_POSTS.values():
        if section and not p["url_path"].startswith(section + "/"):
            continue
        for tag in p.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    tags = sorted(tag_counts.items(), key=lambda x: x[0].lower())
    return render_template("labels.html", labels=tags, section=section)


@app.route("/robots.txt")
def robots_txt():
    base = request.url_root.rstrip("/")
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "# AI crawlers explicitly welcome\n"
        "User-agent: GPTBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: ClaudeBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: PerplexityBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: Google-Extended\n"
        "Allow: /\n"
        "\n"
        "User-agent: CCBot\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )
    return Response(content, mimetype="text/plain")


@app.route("/llms.txt")
def llms_txt():
    post_store.maybe_reload()
    base = request.url_root.rstrip("/")
    name = post_store.WEBSITE_NAME or "This Site"

    lines = [f"# {name}", ""]

    homepage = post_store.SECTION_ROUTES.get("/")
    if homepage and homepage.get("summary"):
        lines += [f"> {homepage['summary']}", ""]

    top_sections = [
        (url, route)
        for url, route in sorted(post_store.SECTION_ROUTES.items())
        if url != "/" and "/" not in url.lstrip("/")
    ]
    if top_sections:
        lines.append("## Sections")
        for url, route in top_sections:
            title = (
                route.get("title")
                or url.lstrip("/").replace("-", " ").title()
            )
            summary = route.get("summary") or ""
            entry = f"- [{title}]({base}{url})"
            if summary:
                entry += f": {summary}"
            lines.append(entry)
        lines.append("")

    posts = sorted(
        post_store.ALL_POSTS.values(),
        key=lambda p: p.get("date") or datetime.min,
        reverse=True,
    )[:20]
    if posts:
        lines.append("## Posts")
        for p in posts:
            title = p.get("title") or p["url_path"].split("/")[-1]
            url_path = p["url_path"]
            summary = p.get("summary") or ""
            entry = f"- [{title}]({base}{url_path})"
            if summary:
                entry += f": {summary}"
            lines.append(entry)
        lines.append("")

    lines.append("## Feeds")
    lines.append(f"- [RSS Feed]({base}/feed.xml): Full site RSS feed")
    lines.append("")

    return Response("\n".join(lines), mimetype="text/plain")


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
    section = request.args.get("section", "").rstrip("/")
    tag_lower = tag.lower()
    posts = sorted(
        (p for p in post_store.ALL_POSTS.values()
         if tag_lower in p.get("tags", [])
         and (not section or p["url_path"].startswith(section + "/"))),
        key=lambda p: p["date"] or datetime.min,
        reverse=True,
    )
    if not posts:
        abort(404)
    nav = {}
    for i, p in enumerate(posts):
        nav[p["url_path"]] = {
            "prev": posts[i + 1] if i + 1 < len(posts) else None,
            "next": posts[i - 1] if i > 0 else None,
        }
    return render_template("tag.html", tag=tag, posts=posts, tag_nav=nav,
                           section=section)


@app.route("/search")
def search():
    post_store.maybe_reload()
    q = request.args.get("q", "").strip()
    label_filter = request.args.get("tag", "").strip().lower()
    section = request.args.get("section", "").rstrip("/")

    candidate_posts = [
        p for p in post_store.ALL_POSTS.values()
        if not section or p["url_path"].startswith(section + "/")
    ]
    all_tags = sorted({tag for p in candidate_posts for tag in p.get("tags", [])})

    results = []
    if q or label_filter:
        q_lower = q.lower()
        for p in candidate_posts:
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

    tag_counts = Counter(
        tag for p in candidate_posts for tag in p.get("tags", [])
    )
    top_tags = [tag for tag, _ in tag_counts.most_common(8)]

    return render_template(
        "search.html",
        posts=results,
        query=q,
        selected_tag=label_filter,
        all_tags=all_tags,
        top_tags=top_tags,
        section=section,
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

        if route["type"] in ("listing", "feed"):
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

            if route["type"] == "feed":
                # Feed is a flat chronological stream — all posts, no featured split.
                # Posts without a date sort to the bottom (datetime.min fallback).
                feed_page_size = 20
                feed_page = max(1, request.args.get("page", 1, type=int))
                feed_total = max(
                    1,
                    (len(section_posts) + feed_page_size - 1) // feed_page_size,
                )
                feed_page = min(feed_page, feed_total)
                feed_posts = section_posts[
                    (feed_page - 1) * feed_page_size: feed_page * feed_page_size
                ]
                return render_template(
                    "feed.html",
                    posts=feed_posts,
                    listing=route["post"],
                    page=feed_page,
                    total_pages=feed_total,
                    **extra,
                )

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
        _ui = post_store.UI_TRANSLATIONS.get(_detect_current_lang(request.path), {})
        breadcrumbs = build_breadcrumbs(
            url_path, post["title"], post_store.SECTION_ROUTES,
            home_label=_ui.get("Home", "Home"),
        )
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

    # 3. Private note — placeholder, or full content for unlocked guests
    if url_path in post_store.PRIVATE_ROUTES:
        entry = post_store.PRIVATE_ROUTES[url_path]
        note_token = str(
            (entry.get("metadata") or {}).get("access_token") or ""
        )
        token_param = request.args.get("token", "")
        if token_param:
            note_match = (
                note_token
                and hmac.compare_digest(token_param, note_token)
            )
            master_match = (
                ACCESS_TOKEN
                and hmac.compare_digest(token_param, ACCESS_TOKEN)
            )
            if note_match:
                unlocked = list(session.get("inkstone_unlocked", []))
                if url_path not in unlocked:
                    unlocked.append(url_path)
                session["inkstone_unlocked"] = unlocked
                session.modified = True
                return redirect(url_path, 302)
            elif master_match:
                session["inkstone_access"] = True
                return redirect(url_path, 302)
        if _is_unlocked(url_path) and url_path in post_store.PRIVATE_RENDERED:
            post = post_store.PRIVATE_RENDERED[url_path]
            back_url = post["section_url"]
            _ui = post_store.UI_TRANSLATIONS.get(
                _detect_current_lang(request.path), {}
            )
            breadcrumbs = build_breadcrumbs(
                url_path, post["title"], post_store.SECTION_ROUTES,
                home_label=_ui.get("Home", "Home"),
            )
            return render_template(
                "post.html", post=post, back_url=back_url,
                breadcrumbs=breadcrumbs, related=[], prev_post=None, next_post=None,
            )
        parent = url_path.rsplit("/", 1)[0]
        back_url = parent if parent else "/"
        return render_template(
            "private.html", entry=entry, back_url=back_url,
            is_owner=bool(session.get("inkstone_access")),
        )

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
        post_store.DEFAULT_THEME,
        post_store.DATAVIEW_INDEX,
        post_store.PRIVATE_ROUTES,
        post_store.PRIVATE_RENDERED,
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
