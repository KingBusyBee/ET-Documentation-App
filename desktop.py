"""
Emergent Thought Documentation App — Desktop Launcher (Windows)

Runs the existing FastAPI app (main.py) in a background thread and opens
it inside a native desktop window using pywebview — no terminal, no browser
tab, no manual "start the server" step for the parent.

This file does not change main.py or database.py at all. It just wraps them.
"""
import threading
import time
import socket
import sys
import os

import uvicorn
import webview

PORT = 8000
HOST = "127.0.0.1"


def get_base_dir():
    """Works both when run as a normal .py file and when frozen by PyInstaller."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # PyInstaller temp extraction dir
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
os.chdir(BASE_DIR)

# main.py resolves its own template/static paths relative to itself via
# os.path.dirname(os.path.abspath(__file__)), so chdir'ing here is enough —
# no changes needed to main.py or database.py.
sys.path.insert(0, BASE_DIR)


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, port)) != 0


def find_free_port(start: int) -> int:
    port = start
    while not port_is_free(port):
        port += 1
    return port


def run_server(port: int):
    from main import app  # imported here so BASE_DIR/sys.path is set first
    uvicorn.run(app, host=HOST, port=port, log_level="warning")


def wait_for_server(port: int, timeout: float = 10.0):
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((HOST, port)) == 0:
                return True
        time.sleep(0.1)
    return False


def main():
    port = find_free_port(PORT)

    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    wait_for_server(port)

    webview.create_window(
        "Emergent Thought — Documentation App",
        f"http://{HOST}:{port}",
        width=1100,
        height=800,
        min_size=(800, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
