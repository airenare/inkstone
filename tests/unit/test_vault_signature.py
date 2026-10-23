import os
import time

import pytest

import posts
from posts import vault_signature


def write(path, text="x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def vault(tmp_path):
    write(tmp_path / "Home.md", "# Home")
    write(tmp_path / "blog" / "post.md", "# Post")
    write(tmp_path / "Overview__website.base", "views: []")
    write(tmp_path / "Board__website.canvas", "{}")
    return tmp_path


def test_stable_when_nothing_changes(vault):
    assert vault_signature(str(vault)) == vault_signature(str(vault))


def test_changes_when_a_note_is_edited(vault):
    before = vault_signature(str(vault))
    p = vault / "blog" / "post.md"
    p.write_text("# Post\nmore", encoding="utf-8")
    os.utime(p, (time.time() + 5, time.time() + 5))
    assert vault_signature(str(vault)) != before


def test_changes_when_a_note_is_added_deleted_or_renamed(vault):
    base = vault_signature(str(vault))
    write(vault / "new.md")
    added = vault_signature(str(vault))
    assert added != base
    (vault / "new.md").unlink()
    assert vault_signature(str(vault)) == base
    (vault / "Home.md").rename(vault / "Start.md")
    assert vault_signature(str(vault)) != base


def test_sees_base_and_canvas_files(vault):
    before = vault_signature(str(vault))
    p = vault / "Board__website.canvas"
    p.write_text('{"nodes": []}', encoding="utf-8")
    os.utime(p, (time.time() + 5, time.time() + 5))
    assert vault_signature(str(vault)) != before


@pytest.mark.parametrize(
    "rel",
    [
        ".obsidian/workspace.json",
        ".obsidian/plugins/x/data.json",
        ".git/index",
        ".git/refs/heads/main",
        ".claude/settings.json",
        ".DS_Store",
        "blog/.DS_Store",
        "_attachments/photo.png",
        "templates/Note Template.md",
        "Templates/Other.md",
        "notes.txt",
    ],
)
def test_ignores_files_that_do_not_affect_the_site(vault, rel):
    before = vault_signature(str(vault))
    target = vault / rel
    write(target, "changed")
    os.utime(target, (time.time() + 9, time.time() + 9))
    assert vault_signature(str(vault)) == before


def test_missing_vault_is_an_empty_signature(tmp_path):
    assert vault_signature(str(tmp_path / "nope")) == vault_signature(
        str(tmp_path / "also-nope")
    )


def test_maybe_reload_ignores_obsidian_and_git_churn(vault, monkeypatch):
    calls = []

    def fake_load_posts():
        calls.append(1)
        posts._last_signature = vault_signature(str(vault))
        return (None,) * 19

    monkeypatch.setattr(posts, "VAULT_PATH", str(vault))
    monkeypatch.setattr(posts, "load_posts", fake_load_posts)
    monkeypatch.setattr(posts, "_last_signature", vault_signature(str(vault)))
    monkeypatch.setattr(posts, "_last_check_time", 0.0)

    write(vault / ".obsidian" / "workspace.json", "{}")
    write(vault / ".git" / "index", "idx")
    posts.maybe_reload()
    assert calls == []

    monkeypatch.setattr(posts, "_last_check_time", 0.0)
    write(vault / "fresh.md", "# Fresh")
    posts.maybe_reload()
    assert calls == [1]
