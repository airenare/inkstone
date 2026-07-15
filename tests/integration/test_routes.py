"""Integration tests for Flask routes using the fixture vault."""


def test_homepage_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_blog_listing_200(client):
    resp = client.get("/blog")
    assert resp.status_code == 200
    assert b"Simple Post" in resp.data


def test_simple_post_200(client):
    resp = client.get("/blog/simple-post")
    assert resp.status_code == 200
    assert b"Simple Post" in resp.data


def test_post_with_dataview_200(client):
    resp = client.get("/blog/dataview-post")
    assert resp.status_code == 200
    assert b'class="dataview"' in resp.data


def test_post_dataview_inline_not_in_code_block(client):
    """`= this.title` inside a fenced code block must appear as literal code."""
    resp = client.get("/blog/dataview-post")
    html = resp.data.decode()
    assert "`= this.title`" in html


def test_unknown_route_404(client):
    resp = client.get("/this-does-not-exist")
    assert resp.status_code == 404


def test_404_uses_error_page_class(client):
    """404 page must use class="error-page", not class="private-note"."""
    resp = client.get("/this-does-not-exist")
    html = resp.data.decode()
    assert 'class="error-page"' in html
    assert 'class="private-note"' not in html


def test_search_returns_results(client):
    resp = client.get("/search?q=simple")
    assert resp.status_code == 200
    # highlighted_title wraps the match in <mark>, so check the post URL instead
    assert b"/blog/simple-post" in resp.data


def test_search_no_results(client):
    resp = client.get("/search?q=zzznomatchxxx")
    assert resp.status_code == 200
    assert b"Simple Post" not in resp.data


def test_nav_hidden_section_not_in_nav(client):
    """Sections with nav_hidden: true must not appear in the top nav."""
    resp = client.get("/")
    assert resp.status_code == 200
    # The title must not appear in the nav rendered on the homepage
    assert b"Hidden Section" not in resp.data


def test_nav_hidden_section_still_routable(client):
    """nav_hidden only hides from nav — the section must still load."""
    resp = client.get("/hidden")
    assert resp.status_code == 200
    assert b"Hidden Section" in resp.data


def test_menu_order_section_not_duplicated_in_nav(client):
    """A section with menu_order must appear only once (in menu_posts, not nav_sections)."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert html.count(">Blog<") == 1


def test_menu_order_listing_links_to_section_url(client):
    """A type:listing page with menu_order must link to /section, not /section/section."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert 'href="/blog"' in html
    assert 'href="/blog/blog"' not in html


def test_dataview_table_listing_file_link(client):
    """TABLE file.link for a listing page must point to /section, not /section/slug."""
    resp = client.get("/blog/dataview-post")
    assert resp.status_code == 200
    html = resp.data.decode()
    # The Blog listing page is at /blog; its file.link must NOT be /blog/blog
    assert 'href="/blog"' in html
    assert 'href="/blog/blog"' not in html


def test_canvas_embed_renders_in_post(client):
    """![[embed_canvas]] in a post must render an inline canvas-embed div."""
    resp = client.get("/blog/dataview-post")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert 'class="canvas-embed"' in html
    assert "![[embed_canvas]]" not in html


def test_skip_to_content_link_present(client):
    """Every page must include a skip-to-content link and a matching main landmark."""
    resp = client.get("/blog/simple-post")
    html = resp.data.decode()
    assert 'class="skip-to-content"' in html
    assert 'id="main-content"' in html


def test_search_tag_filter_has_label(client):
    """The tag filter <select> on the search page must have an associated <label>."""
    resp = client.get("/search")
    html = resp.data.decode()
    assert 'for="tag-filter"' in html
    assert 'id="tag-filter"' in html


def test_post_date_has_datetime_attribute(client):
    """Post meta dates must be wrapped in <time datetime='YYYY-MM-DD'>."""
    resp = client.get("/blog/simple-post")
    html = resp.data.decode()
    assert '<time datetime="2026-01-15"' in html


def test_post_nav_has_directional_labels(client):
    """Post prev/next nav uses chronological convention: Previous=older, Next=newer."""
    # simple-post (Jan 15) is the oldest post — it has no previous but has a
    # "Next post" link pointing to the newer dataview-post (Jan 20).
    resp = client.get("/blog/simple-post")
    html = resp.data.decode()
    assert "Next post" in html
    assert "Previous post" not in html


def test_search_empty_state_shows_tag_suggestions(client):
    """A search with no results must show the tag suggestions block."""
    resp = client.get("/search?q=zzznomatchxxx")
    html = resp.data.decode()
    assert 'class="search-suggestions"' in html
    # Fixture post has tags [test, python] so at least one must appear
    assert 'href="/tag/test"' in html or 'href="/tag/python"' in html


def test_https_canonical_url_behind_proxy(client):
    """Canonical URL must use https:// when X-Forwarded-Proto is https."""
    resp = client.get(
        "/",
        headers={"X-Forwarded-Proto": "https", "Host": "antonbakulin.com"},
    )
    assert resp.status_code == 200
    html = resp.data.decode()
    assert 'href="https://antonbakulin.com/"' in html


def test_robots_txt_returns_200(client):
    resp = client.get("/robots.txt")
    assert resp.status_code == 200
    assert resp.content_type == "text/plain; charset=utf-8"


def test_robots_txt_allows_ai_crawlers(client):
    text = client.get("/robots.txt").data.decode()
    for bot in ("GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot"):
        assert f"User-agent: {bot}" in text
        idx = text.index(f"User-agent: {bot}")
        snippet = text[idx: idx + 40]
        assert "Disallow" not in snippet


def test_robots_txt_references_sitemap(client):
    text = client.get("/robots.txt").data.decode()
    assert "Sitemap:" in text
    assert "sitemap.xml" in text


def test_llms_txt_returns_200(client):
    resp = client.get("/llms.txt")
    assert resp.status_code == 200
    assert resp.content_type == "text/plain; charset=utf-8"


def test_llms_txt_contains_site_name(client):
    text = client.get("/llms.txt").data.decode()
    assert text.startswith("# ")


def test_llms_txt_contains_posts_section(client):
    text = client.get("/llms.txt").data.decode()
    assert "## Posts" in text


def test_llms_txt_contains_feed_link(client):
    text = client.get("/llms.txt").data.decode()
    assert "/feed.xml" in text


def test_homepage_has_rss_autodiscovery_link(client):
    resp = client.get("/")
    html = resp.data.decode()
    assert 'type="application/rss+xml"' in html
    assert 'href="/feed.xml"' in html


def test_post_has_meta_description(client):
    resp = client.get("/blog/simple-post")
    html = resp.data.decode()
    assert '<meta name="description"' in html


def test_homepage_has_meta_description(client):
    resp = client.get("/")
    html = resp.data.decode()
    assert '<meta name="description"' in html


def test_blog_listing_has_meta_description(client):
    resp = client.get("/blog")
    html = resp.data.decode()
    assert '<meta name="description"' in html
