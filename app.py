from flask import Flask, render_template, abort, request, send_from_directory, redirect, url_for

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
    return {"website_name": post_store.WEBSITE_NAME}


# =========================================
# ROUTES
# =========================================

@app.route("/")
def index():
    post_store.maybe_reload()
    if not post_store.HOMEPAGE:
        return redirect(url_for("blog"))
    return render_template("index.html", homepage=post_store.HOMEPAGE)


@app.route("/blog")
def blog():
    post_store.maybe_reload()
    featured = sorted(
        [p for p in post_store.POSTS.values() if p["featured"]],
        key=lambda x: (x["priority"], -(x["date"].timestamp() if x["date"] else 0)),
    )
    regular = [p for p in post_store.POSTS.values() if not p["featured"]]
    return render_template("blog.html", featured=featured, regular=regular)


@app.route("/blog/<slug>")
def post(slug):
    post_store.maybe_reload()
    if slug not in post_store.POSTS:
        abort(404)
    return render_template("post.html", post=post_store.POSTS[slug])


@app.route("/post/<slug>")
def post_redirect(slug):
    return redirect(url_for("post", slug=slug), 301)


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
            p for p in post_store.POSTS.values()
            if q in p["title"].lower() or q in p["content"]
        ]
    return render_template("search.html", posts=results, query=q)


# =========================================
# START
# =========================================

if __name__ == "__main__":
    post_store.POSTS, post_store.HOMEPAGE, post_store.WEBSITE_NAME = post_store.load_posts()
    app.run("127.0.0.1", 8000, debug=True)
