"""Checkpoints must round-trip non-ASCII text regardless of the OS locale.

On Windows the default text encoding is cp1252, so a checkpoint holding an
Arabic transcript used to die with UnicodeEncodeError('charmap', ...) at the
very end of a 45-minute ASR stage. Every read/write now pins utf-8.
"""
import json
import subprocess
import sys
from pathlib import Path


def test_checkpoint_roundtrip_non_ascii_without_utf8_mode(tmp_path, monkeypatch):
    # Run in a child interpreter with UTF-8 mode explicitly disabled so the
    # test bites on Windows (and on any locale that isn't utf-8).
    code = r"""
import json, os, sys
from pathlib import Path
os.environ["PUBLIKCLIP_HOME"] = sys.argv[1]
from publikclip_pipeline.jobs import queue
job = queue.create_job("file", "x.mp4", "{}")
data = {"segments": [{"text": "الحمد لله", "emoji": "😂"}]}
queue.write_checkpoint(job, "asr", 1, data)
back = queue.read_checkpoint(job, "asr", 1)
assert back == data, back
print("ok")
"""
    proc = subprocess.run(
        [sys.executable, "-X", "utf8=0", "-c", code, str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "ok"
    raw = next(tmp_path.rglob("asr.json")).read_bytes()
    assert "الحمد".encode("utf-8") in raw
