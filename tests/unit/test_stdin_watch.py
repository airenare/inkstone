import os
import subprocess
import sys
import threading
from pathlib import Path

from stdin_watch import watch_stdin

ROOT = Path(__file__).resolve().parents[2]


def test_calls_on_eof_when_write_end_closes():
    r, w = os.pipe()
    done = threading.Event()
    watch_stdin(r, on_eof=done.set)
    assert not done.wait(0.2)
    os.close(w)
    assert done.wait(2)
    os.close(r)


def test_data_on_stdin_does_not_trigger_exit():
    r, w = os.pipe()
    done = threading.Event()
    watch_stdin(r, on_eof=done.set)
    os.write(w, b"hello")
    assert not done.wait(0.2)
    os.close(w)
    assert done.wait(2)
    os.close(r)


def test_returns_none_without_a_usable_stdin(monkeypatch):
    class NoFd:
        def fileno(self):
            raise ValueError("no fd")

    monkeypatch.setattr(sys, "stdin", NoFd())
    assert watch_stdin(on_eof=lambda: None) is None


def test_real_process_exits_when_its_stdin_closes():
    code = (
        "import time; from stdin_watch import watch_stdin;"
        " watch_stdin(); time.sleep(30)"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", code],
        cwd=ROOT,
        stdin=subprocess.PIPE,
    )
    try:
        assert proc.poll() is None
        proc.stdin.close()
        assert proc.wait(timeout=10) == 0
    finally:
        if proc.poll() is None:
            proc.kill()
