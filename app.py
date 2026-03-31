import html
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
        "current_url": request.url,
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


@app.route("/search")
def search():
    post_store.maybe_reload()
    q = request.args.get("q", "").lower()
    results = []
    if q:
        results = [
            p for p in post_store.ALL_POSTS.values()
            if q in p["title"].lower() or q in p["content"]
        ]
    return render_template("search.html", posts=results, query=q)


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
            return render_template(
                "listing.html",
                featured=featured,
                regular=regular,
                listing=route["post"],
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
        return render_template(template, post=post, back_url=back_url)

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
    ) = post_store.load_posts()
    app.run("127.0.0.1", 8000, debug=True)
