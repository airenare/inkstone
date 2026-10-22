"""Integration tests for the dev-only /__inkstone/source-map endpoint."""
import pytest
from flask import Flask


@pytest.fixture(scope="module")
def dev_client():
    import app as inkstone_app
    dev_app = Flask("inkstone-dev-api-test")
    inkstone_app.register_dev_routes(dev_app)
    dev_app.config["TESTING"] = True
    return dev_app.test_client()


@pytest.fixture(scope="module")
def entries(dev_client):
    resp = dev_client.get("/__inkstone/source-map")
    assert resp.status_code == 200
    return {e["file"]: e for e in resp.get_json()["files"]}


def test_source_map_lists_published_note(entries):
    entry = entries["blog/simple_post.md"]
    assert entry["published"] is True
    assert entry["private"] is False
    assert entry["url"] == "/blog/simple-post"


def test_source_map_has_version(dev_client):
    data = dev_client.get("/__inkstone/source-map").get_json()
    assert isinstance(data["version"], str) and data["version"]


def test_source_map_unpublished_note_is_private_with_url(entries):
    entry = entries["blog/draft_note.md"]
    assert entry["published"] is False
    assert entry["private"] is True
    assert entry["has_own_token"] is False
    assert entry["url"] == "/blog/draft-note"


def test_source_map_unpublished_listing_has_null_url(entries):
    entry = entries["blog/Draft Index.md"]
    assert entry["published"] is False
    assert entry["private"] is False
    assert entry["url"] is None


def test_master_token_opens_unpublished_note(monkeypatch):
    import app as inkstone_app
    monkeypatch.setattr(inkstone_app, "ACCESS_TOKEN", "master-key")
    c = inkstone_app.app.test_client()
    resp = c.get("/blog/draft-note?token=master-key",
                 follow_redirects=True)
    assert resp.status_code == 200
    assert b"Not published." in resp.data


def test_source_map_private_note_flagged(entries):
    entry = entries["blog/secret_note.md"]
    assert entry["published"] is False
    assert entry["private"] is True
    assert entry["has_own_token"] is True
    assert entry["url"] == "/blog/secret-note"


def test_source_map_includes_homepage_and_listing(entries):
    assert entries["Homepage.md"]["url"] == "/"
    assert entries["Homepage.md"]["published"] is True
    assert entries["blog/Blog Index.md"]["url"] == "/blog"


def test_source_map_language_variant_url(entries):
    assert entries["blog/simple_post_RU.md"]["url"] == "/blog/simple-post/ru"


def test_source_map_base_and_canvas(entries):
    canvas = entries["blog/board__website.canvas"]
    assert canvas["published"] is True
    assert canvas["url"] == "/blog/board"
    base = entries["blog/table__website.base"]
    assert base["published"] is True
    assert base["url"] == "/blog/table"


def test_source_map_file_paths_are_relative_forward_slash(entries):
    for path in entries:
        assert not path.startswith("/")
        assert "\\" not in path
        assert ".." not in path.split("/")


def test_source_map_disabled_by_default(client):
    assert client.get("/__inkstone/source-map").status_code == 404
