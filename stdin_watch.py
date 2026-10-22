"""Exit the server when its stdin closes.

An editor integration (the Obsidian plugin) starts InkStone as a child with
a pipe on stdin and keeps it open. If the parent dies, even from a crash or
a force-quit, the OS closes the pipe and this watcher ends the server, so no
stray process is left behind. Enabled with INKSTONE_EXIT_ON_STDIN_EOF=1.

This module imports nothing from the rest of InkStone.
"""
import os
import sys
import threading


def watch_stdin(fd=None, on_eof=None):
    """Start a daemon thread that calls on_eof() once fd reaches EOF.

    fd defaults to sys.stdin; on_eof defaults to a hard os._exit(0), because
    the Flask reloader and its worker threads must not get a chance to hold
    the process open. Returns the thread, or None when there is no usable
    stdin. A read error counts as EOF: the pipe is gone either way.
    """
    if fd is None:
        try:
            fd = sys.stdin.fileno()
        except (AttributeError, ValueError, OSError):
            return None
    if on_eof is None:
        def on_eof():
            os._exit(0)

    def run():
        while True:
            try:
                data = os.read(fd, 4096)
            except OSError:
                break
            if not data:
                break
        on_eof()

    thread = threading.Thread(target=run, name="stdin-watch", daemon=True)
    thread.start()
    return thread
