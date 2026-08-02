"""
Emergent Thought Documentation App — Launcher
Run: python run.py
Then open http://localhost:8000 in your browser.
"""
import subprocess, sys, webbrowser, time, os

PORT = 8000
URL  = f"http://localhost:{PORT}"

print(f"\n  Emergent Thought Documentation App")
print(f"  {'─'*36}")
print(f"  Starting on {URL}")
print(f"  Press Ctrl+C to stop.\n")

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app",
     "--host", "127.0.0.1", "--port", str(PORT), "--reload"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
)
time.sleep(1.5)
webbrowser.open(URL)

try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    print("\n  App stopped.\n")
