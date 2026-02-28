import os
import yaml
import markdown
from flask import Flask, render_template, abort
from datetime import datetime
import dotenv

dotenv.load_dotenv()

VAULT_PATH = os.getenv("VAULT_PATH", "obsidian_vault")

BLOG_TAGS = {"blog", "website"}  # tags that qualify a post

app = Flask(__name__, template_folder="site/templates", static_folder="site/static")

def parse_markdown_file(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    metadata = {}
    markdown_text = text

    if text.startswith("---"):
        try:
            _, yaml_text, md_text = text.split("---", 2)
            metadata = yaml.safe_load(yaml_text) or {}
            markdown_text = md_text.strip()
        except Exception as e:
            print(f"Warning: Failed to parse YAML in {path}: {e}")
            # fallback: use empty metadata, but keep markdown_text

    # convert markdown to HTML
    html = markdown.markdown(
        markdown_text,
        extensions=["fenced_code", "tables", "toc", "codehilite"]
    )

    return metadata, html


def load_posts():
    posts = []

    for root, _, files in os.walk(VAULT_PATH):
        for fname in files:
            if not fname.endswith(".md"):
                continue

            full_path = os.path.join(root, fname)
            metadata, html = parse_markdown_file(full_path)

            tags = set(tag.lower() for tag in metadata.get("tags", []))

            # Only include posts with desired tags
            if BLOG_TAGS.isdisjoint(tags):
                continue

            slug = metadata.get("slug") or os.path.splitext(fname)[0]
            title = metadata.get("title", slug.replace("-", " ").title())
            date = metadata.get("date", "Unknown Date")

            # Convert date to proper type if necessary
            if isinstance(date, str):
                try:
                    date_obj = datetime.fromisoformat(date)
                except ValueError:
                    date_obj = None
            else:
                date_obj = date

            posts.append({
                "slug": slug,
                "title": title,
                "date": date_obj,
                "html": html,
                "metadata": metadata
            })

    # Sort by date descending
    posts.sort(key=lambda p: p["date"] or datetime.min, reverse=True)

    # Convert to {slug: post} for easy lookup
    return {post["slug"]: post for post in posts}


POSTS = load_posts()


@app.route("/")
def index():
    return render_template("index.html", posts=POSTS.values())


@app.route("/post/<slug>")
def post(slug):
    if slug not in POSTS:
        abort(404)
    return render_template("post.html", post=POSTS[slug])


if __name__ == "__main__":
    app.run(debug=True)