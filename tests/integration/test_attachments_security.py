import pytest

import app as app_module
import posts

SERVED = [
    "_attachments/pic.png",
    "blog/_attachments/photo.JPG",
    "_attachments/clip.mp4",
    "_attachments/song.mp3",
    "_attachments/paper.pdf",
    "_attachments/icon.svg",
]

BLOCKED = [
    ".git/config",
    ".git/HEAD",
    ".git/index",
    ".obsidian/workspace.json",
    ".obsidian/plugins/x/README.md",
    ".claude/settings.json",
    ".claude/diagram.png",
    "_attachments/.hidden.png",
    "draft.md",
    "CLAUDE.md",
    "blog/post.md",
    "Overview.base",
    "Board.canvas",
    "readme.txt",
    "data.json",
    ".env",
    "noextension",
    "_attachments/archive.zip",
    "script.py",
]


@pytest.fixture
def vault(tmp_path, monkeypatch):
    for rel in SERVED + BLOCKED:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"content-of-" + rel.encode())
    monkeypatch.setattr(app_module, "VAULT_PATH", str(tmp_path))
    return tmp_path


@pytest.mark.parametrize("rel", SERVED)
def test_media_files_are_served(client, vault, rel):
    r = client.get("/attachments/" + rel)
    assert r.status_code == 200
    assert r.data == b"content-of-" + rel.encode()


@pytest.mark.parametrize("rel", BLOCKED)
def test_everything_else_is_not_served(client, vault, rel):
    r = client.get("/attachments/" + rel)
    assert r.status_code == 404
    assert b"content-of-" not in r.data


@pytest.mark.parametrize(
    "url",
    [
        "/attachments/%2egit/config",
        "/attachments/.git%2fconfig",
        "/attachments/_attachments/../.git/config",
        "/attachments/../app.py",
        "/attachments//.git/config",
    ],
)
def test_encoded_and_traversal_tricks_are_blocked(client, vault, url):
    r = client.get(url)
    assert r.status_code in (301, 308, 404)
    follow = client.get(url, follow_redirects=True)
    assert follow.status_code == 404
    assert b"content-of-" not in follow.data


def test_load_posts_ignores_notes_in_hidden_folders(tmp_path, monkeypatch):
    def note(rel, text):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    note("Home.md", "---\nwebsite: true\ntitle: Home\ntype: homepage\n---\nHi\n")
    note("blog/hello.md", "---\nwebsite: true\ntitle: Hello\n---\nPublic\n")
    note(".claude/notes.md", "---\ntitle: Agent notes\n---\nSECRET-AGENT-TEXT\n")
    note(".obsidian/plugins/x/README.md", "---\ntitle: Plugin readme\n---\nX\n")
    monkeypatch.setattr(posts, "VAULT_PATH", str(tmp_path))
    result = posts.load_posts()
    all_posts, private_routes = result[0], result[6]
    urls = set(all_posts) | set(private_routes)
    assert "/blog/hello" in urls
    assert not any("agent-notes" in u or "plugin-readme" in u for u in urls)
