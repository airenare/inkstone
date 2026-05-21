"""Integration tests for /feed.xml and /sitemap.xml."""


def test_feed_xml_200(client):
    resp = client.get("/feed.xml")
    assert resp.status_code == 200
    assert b"xml" in resp.content_type.encode()


def test_feed_has_items(client):
    resp = client.get("/feed.xml")
    assert b"<item>" in resp.data


def test_sitemap_200(client):
    resp = client.get("/sitemap.xml")
    assert resp.status_code == 200


def test_sitemap_has_urls(client):
    resp = client.get("/sitemap.xml")
    assert b"<url>" in resp.data
