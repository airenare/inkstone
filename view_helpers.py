"""Pure view-layer utilities with no Flask dependency.

These helpers are called by app.py routes but have no dependency on Flask,
making them independently unit-testable.
"""
import html
import re


def build_breadcrumbs(url_path, post_title, section_routes, home_label="Home"):
    """Build breadcrumb list: [(label, url), ..., (current_title, None)]."""
    crumbs = [(home_label, "/")]
    parts = [p for p in url_path.split("/") if p]
    for i in range(len(parts) - 1):
        segment_url = "/" + "/".join(parts[: i + 1])
        if segment_url in section_routes:
            label = section_routes[segment_url]["post"]["title"]
        else:
            label = parts[i].replace("-", " ").replace("_", " ").title()
        crumbs.append((label, segment_url))
    crumbs.append((post_title, None))
    return crumbs


def get_adjacent_posts(post, all_posts):
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


def get_related(post, all_posts, max_results=4):
    """Return up to max_results related posts sorted by shared-tag count."""
    post_tags = set(post.get("tags") or [])
    post_section = post.get("section", "")
    scored = []
    post_base = post.get("base_url_path") or post["url_path"]
    for p in all_posts.values():
        if p["url_path"] == post["url_path"]:
            continue
        # skip language variants of the same post (same canonical base URL)
        if (p.get("base_url_path") or p["url_path"]) == post_base:
            continue
        shared = len(post_tags & set(p.get("tags") or []))
        same_section = int(p.get("section", "") == post_section)
        score = shared * 2 + same_section
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: (-x[0], -(x[1]["date"].timestamp()
                                         if x[1]["date"] else 0)))
    return [p for _, p in scored[:max_results]]


def highlight(text, query):
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
