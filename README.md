# Emergent Thought — Documentation App

*Making documentation easier — like technology is supposed to.*

A free, offline-first desktop app for logging homeschool sessions toward Missouri's annual hour requirement (RSMo 167.012). All data stays on your machine. No internet. No accounts. No data collection.

Download

⬇ Download EmergentThought.exe — no install, no Python needed. Just double-click and go.

Building it yourself or contributing? See Quick Start — Run from source below.
---

## Quick Start — Windows Desktop App (recommended, for distributing to other families)

This builds a real `.exe` — double-click, native window opens, no terminal, no browser, no Python required to *run* it.

```
1. Install Python 3.10+ if you don't already have it: python.org/downloads
2. Open this folder in Command Prompt / PowerShell
3. Run:  build_windows.bat
4. Wait for it to finish — this only needs to be done once, on one machine
5. Your finished app is at:  dist\EmergentThought.exe
```

Copy `EmergentThought.exe` anywhere — a USB stick, a shared drive, an email attachment — and hand it to another homeschool family. They just double-click it. Nothing else to install.

Each family's data is saved automatically to `%APPDATA%\EmergentThought\et_docs.db` on their own machine, and persists across restarts.

---

## Quick Start — Run from source (for development / testing changes)

```bash
# 1. Install dependencies (one time)
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart

# 2. Run
python -m uvicorn main:app --host 127.0.0.1 --port 8000

# 3. Open your browser
# http://localhost:8000
```

Or use the included launcher:

```bash
python run.py
```

This mode still opens in your browser and requires Python installed — use the `.exe` build above for distributing to non-technical users.

---

## What it does

- **Session logging** — date, subject, duration, notes
- **Live timer** — start/pause/reset; auto-pauses after 15 minutes of inactivity
- **Missouri compliance tracking** — 1000hr annual total, 600hr core subject requirement
- **Session history** — view and delete sessions; hours by subject
- **PDF export** — coming in next build

---

## Data

- **Running from source:** data is stored in `et_docs.db` (SQLite) in the same folder as the app.
- **Running the .exe:** data is stored in `%APPDATA%\EmergentThought\et_docs.db` on the user's machine — this survives the app being closed, updated, or moved.

**Back this file up.** The developer collects nothing and cannot recover lost data.

---

## License

MIT. Free to use, modify, and distribute. You are responsible for your own data backups. No warranty. No data is collected, transmitted, or stored anywhere except your own machine.

---

## Missouri Law Reference

- RSMo 167.012 — Home school definition and requirements
- RSMo 167.031 — Compulsory attendance
- Annual requirement: 1000 hours total, 600 in core subjects (Reading, Language Arts, Mathematics, Social Studies, Science)
- Documentation standard: "written or credible evidence equivalent" to a plan book or diary

---

## Build Roadmap

1. ✅ **Documentation App** — this app
2. 🔜 **Curriculum Pack** — Ray's Arithmetic, McGuffey's Readers, public domain texts
3. 🔜 **Reasoning/Logic Courses** — Socratic AI evaluation
