import html
import re
from datetime import datetime, timezone

from flask import Flask, render_template, abort, request, send_from_directory, \
    Response

import posts as post_store
from config import VAULT_PATH, VERSION


# =========================================
# APP
# =========================================

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static",
)


@app.context_processor
def inject_globals():
    # Top-level sections (direct children of root that have a section route)
    top_sections = sorted(
        url for url in post_store.SECTION_ROUTES
        if url != "/" and url.count("/") == 1
    )
    return {
        "website_name": post_store.WEBSITE_NAME,
        "nav_sections": top_sections,
        "menu_posts": post_store.MENU_POSTS,
        "show_search": post_store.SHOW_SEARCH,
        "show_labels": post_store.SHOW_LABELS,
        "current_url": request.url,
        "canonical_url": request.base_url,
        "app_version": VERSION,
    }


# =========================================
# ROUTES
# =========================================

@app.route("/attachments/<path:path>")
def attachments(path):
    return send_from_directory(VAULT_PATH, path)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.route("/feed.xml")
def rss_feed():
    post_store.maybe_reload()
    posts = sorted(
        post_store.ALL_POSTS.values(),
        key=lambda p: p["date"] or datetime.min,
        reverse=True,
    )[:20]
    base = request.url_root.rstrip("/")
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for p in posts:
        pub = ""
        if p["date"]:
            pub = p["date"].strftime("%a, %d %b %Y %H:%M:%S +0000")
        link = base + p["url_path"]
        items.append(
            f"    <item>\n"
            f"      <title>{html.escape(p['title'])}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <guid>{link}</guid>\n"
            f"      <pubDate>{pub}</pubDate>\n"
            f"      <description>"
            f"{html.escape(p['summary'])}"
            f"</description>\n"
            f"    </item>"
        )
    site_title = html.escape(post_store.WEBSITE_NAME)
    site_link = base + "/"
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        f"    <title>{site_title}</title>\n"
        f"    <link>{site_link}</link>\n"
        f"    <description>{site_title}</description>\n"
        f"    <lastBuildDate>{now}</lastBuildDate>\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>"
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
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for p in posts:
        pub = p["date"].strftime("%a, %d %b %Y %H:%M:%S +0000") if p["date"] else ""
        link = base + p["url_path"]
        items.append(
            f"    <item>\n"
            f"      <title>{html.escape(p['title'])}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <guid>{link}</guid>\n"
            f"      <pubDate>{pub}</pubDate>\n"
            f"      <description>{html.escape(p['summary'])}</description>\n"
            f"    </item>"
        )
    feed_title = html.escape(
        f"{section_title} \u2014 {post_store.WEBSITE_NAME}"
    )
    site_link = base + section_url
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        f"    <title>{feed_title}</title>\n"
        f"    <link>{site_link}</link>\n"
        f"    <description>{feed_title}</description>\n"
        f"    <lastBuildDate>{now}</lastBuildDate>\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>"
    )
    return Response(xml, mimetype="application/rss+xml")


@app.route("/labels")
def labels_index():
    post_store.maybe_reload()
    label_counts = {}
    for p in post_store.ALL_POSTS.values():
        for label in p.get("labels", []):
            label_counts[label] = label_counts.get(label, 0) + 1
    labels = sorted(label_counts.items())
    return render_template("labels.html", labels=labels)


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


def _build_breadcrumbs(url_path, post_title):
    """Build breadcrumb list: [(label, url), ..., (current_title, None)]."""
    crumbs = [("Home", "/")]
    parts = [p for p in url_path.split("/") if p]
    for i in range(len(parts) - 1):
        segment_url = "/" + "/".join(parts[: i + 1])
        if segment_url in post_store.SECTION_ROUTES:
            label = post_store.SECTION_ROUTES[segment_url]["post"]["title"]
        else:
            label = parts[i].replace("-", " ").title()
        crumbs.append((label, segment_url))
    crumbs.append((post_title, None))
    return crumbs


def _get_adjacent_posts(post, all_posts):
    """Return (prev_post, next_post) ordered by date within the same section.

    prev = older post (lower date), next = newer post (higher date).
    Posts without a date are excluded from ordering.
    """
    section = post["section"]
    ordered = sorted(
        [p for p in all_posts.values()
         if p["section"] == section and p["date"]],
        key=lambda p: p["date"],
    )
    idx = next(
        (i for i, p in enumerate(ordered)
         if p["url_path"] == post["url_path"]),
        None,
    )
    if idx is None:
        return None, None
    prev_post = ordered[idx - 1] if idx > 0 else None
    next_post = ordered[idx + 1] if idx < len(ordered) - 1 else None
    return prev_post, next_post


def _get_related(post, all_posts, max_results=4):
    """Return up to max_results related posts sorted by shared-label count."""
    post_labels = set(post.get("labels") or [])
    post_section = post.get("section", "")
    scored = []
    for p in all_posts.values():
        if p["url_path"] == post["url_path"]:
            continue
        shared = len(post_labels & set(p.get("labels") or []))
        same_section = int(p.get("section", "") == post_section)
        score = shared * 2 + same_section
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: (-x[0], -(x[1]["date"].timestamp()
                                         if x[1]["date"] else 0)))
    return [p for _, p in scored[:max_results]]


def _highlight(text, query):
    """HTML-escape text, then wrap query matches in <mark>."""
    if not text:
        return ""
    escaped = html.escape(text)
    if not query:
        return escaped
    return re.sub(
        "(" + re.escape(html.escape(query)) + ")",
        r"<mark>\1</mark>",
        escaped,
        flags=re.IGNORECASE,
    )


@app.route("/label/<label>")
def label_archive(label):
    post_store.maybe_reload()
    label_lower = label.lower()
    posts = sorted(
        (p for p in post_store.ALL_POSTS.values()
         if label_lower in p.get("labels", [])),
        key=lambda p: p["date"] or datetime.min,
        reverse=True,
    )
    if not posts:
        abort(404)
    return render_template("label.html", label=label, posts=posts)


@app.route("/search")
def search():
    post_store.maybe_reload()
    q = request.args.get("q", "").strip()
    label_filter = request.args.get("label", "").strip().lower()

    all_labels = sorted(set().union(
        *(p["labels"] for p in post_store.ALL_POSTS.values())
    ))

    results = []
    if q or label_filter:
        q_lower = q.lower()
        for p in post_store.ALL_POSTS.values():
            if label_filter and label_filter not in p.get("labels", []):
                continue
            if q_lower and q_lower not in p["title"].lower() \
                    and q_lower not in p["content"]:
                continue
            results.append({
                **p,
                "highlighted_title": _highlight(p["title"], q),
                "highlighted_summary": _highlight(p["summary"], q),
            })

    return render_template(
        "search.html",
        posts=results,
        query=q,
        selected_label=label_filter,
        all_labels=all_labels,
    )


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

            return render_template(
                "listing.html",
                featured=featured,
                regular=regular_page,
                listing=route["post"],
                page=page,
                total_pages=total_pages,
            )

        else:  # homepage
            return render_template("index.html", homepage=route["post"])

    # 2. Regular posts
    if url_path in post_store.ALL_POSTS:
        post = post_store.ALL_POSTS[url_path]
        back_url = "/" + post["section"] if post["section"] else "/"
        template = (
            "book.html" if "📚book" in post.get("tags", set()) else "post.html"
        )
        breadcrumbs = _build_breadcrumbs(url_path, post["title"])
        related = _get_related(post, post_store.ALL_POSTS)
        prev_post, next_post = _get_adjacent_posts(post, post_store.ALL_POSTS)
        return render_template(
            template, post=post, back_url=back_url,
            breadcrumbs=breadcrumbs, related=related,
            prev_post=prev_post, next_post=next_post,
        )

    # 3. Private note placeholder
    if url_path in post_store.PRIVATE_ROUTES:
        entry = post_store.PRIVATE_ROUTES[url_path]
        parent = url_path.rsplit("/", 1)[0]
        back_url = parent if parent else "/"
        return render_template("private.html", entry=entry, back_url=back_url)

    abort(404)


# =========================================
# START
# =========================================

if __name__ == "__main__":
    (
        post_store.ALL_POSTS,
        post_store.SECTION_ROUTES,
        post_store.WEBSITE_NAME,
        post_store.DATAVIEW_INDEX,
        post_store.PRIVATE_ROUTES,
        post_store.MENU_POSTS,
        post_store.SHOW_SEARCH,
        post_store.SHOW_LABELS,
    ) = post_store.load_posts()
    app.run("127.0.0.1", 8000, debug=True)
