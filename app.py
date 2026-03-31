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


# =========================================
# ROUTES
# =========================================

@app.route("/")
def index():
    post_store.maybe_reload()
    return render_template("index.html", posts=post_store.POSTS.values())


@app.route("/post/<slug>")
def post(slug):
    post_store.maybe_reload()
    if slug not in post_store.POSTS:
        abort(404)
    return render_template("post.html", post=post_store.POSTS[slug])


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
    post_store.POSTS = post_store.load_posts()
    app.run("127.0.0.1", 8000, debug=True)
