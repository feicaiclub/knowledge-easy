#!/usr/bin/env python3
"""Start the local review room; reuse an already-running matching project."""
import argparse
import json
from pathlib import Path
import shutil
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

from project import atomic_json

BASE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir", nargs="?")
    ap.add_argument("--project")
    ap.add_argument("--port", type=int, default=8798)
    ap.add_argument("--restart", action="store_true")
    args = ap.parse_args()
    specified = args.project or args.project_dir or os.environ.get("LAZY_STUDIO_PROJECT")
    if specified:
        root = Path(specified).resolve()
    else:
        root = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / "review/studio.json").is_file()), None)
        if root is None:
            sys.exit("Run this from a film project, or pass --project <directory>.")
    if not (root / "review/studio.json").is_file():
        sys.exit("Register a review revision with project.py before starting Studio.")
    missing = [name for name in ("ffmpeg", "ffprobe") if not shutil.which(name)]
    if missing:
        sys.exit("Missing " + ", ".join(missing) + ". Use this Skill’s run.sh or run.ps1 to prepare dependencies.")
    url = f"http://127.0.0.1:{args.port}"
    try:
        with urllib.request.urlopen(url + "/api/project", timeout=1) as response:
            existing = json.load(response)
        if existing.get("feedback_path") != str(root / "review/feedback.jsonl"):
            sys.exit(f"Port {args.port} belongs to another project. Choose a different --port.")
        if not args.restart:
            print(url)
            return
        record = json.loads((root / "review/server.json").read_text())
        if Path(record["project"]).resolve() != root or Path(record["script"]).resolve() != BASE / "studio.py":
            sys.exit("The running server was started elsewhere and has not been stopped.")
        if os.name != "nt":
            command = subprocess.check_output(["ps", "-p", str(record["pid"]), "-o", "command="], text=True)
            if str(BASE / "studio.py") not in command or str(root) not in command:
                sys.exit("The process identity does not match. It has not been stopped.")
        os.kill(record["pid"], signal.SIGTERM)
        for _ in range(30):
            try:
                urllib.request.urlopen(url + "/api/project", timeout=.2).close()
                time.sleep(.1)
            except (urllib.error.URLError, OSError):
                break
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        pass
    log = (root / "review/server.log").open("ab")
    child = subprocess.Popen([sys.executable, str(BASE / "studio.py"), "--project", str(root), "--port", str(args.port)],
                             stdout=log, stderr=log, start_new_session=True)
    for _ in range(100):
        if child.poll() is not None:
            sys.exit(f"Startup failed. See {root / 'review/server.log'}")
        try:
            with urllib.request.urlopen(url + "/api/project", timeout=.5) as response:
                ready = json.load(response)
            if ready.get("feedback_path") == str(root / "review/feedback.jsonl"):
                atomic_json(root / "review/server.json", {"pid": child.pid, "port": args.port, "url": url,
                                                          "project": str(root), "script": str(BASE / 'studio.py')})
                print(url)
                return
        except (urllib.error.URLError, OSError):
            time.sleep(.1)
    sys.exit("Startup did not complete. See review/server.log.")


if __name__ == "__main__":
    main()
