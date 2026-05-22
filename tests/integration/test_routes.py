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
