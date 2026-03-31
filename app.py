from datetime import datetime

from flask import Flask, render_template, abort, request, send_from_directory

import posts as post_store
from config import VAULT_PATH


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
    }


# =========================================
# ROUTES
# =========================================

@app.route("/attachments/<path:path>")
def attachments(path):
    return send_from_directory(VAULT_PATH, path)


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
        return render_template("post.html", post=post, back_url=back_url)

    # 3. Private note placeholder
    if url_path in post_store.PRIVATE_ROUTES:
        entry = post_store.PRIVATE_ROUTES[url_path]
        return render_template("private.html", entry=entry)

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
    ) = post_store.load_posts()
    app.run("127.0.0.1", 8000, debug=True)
