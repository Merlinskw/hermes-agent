"""Run the original (main) fixture's iex command with output to files; print timing + output."""
import os, shutil, subprocess, sys, time, tempfile
from pathlib import Path
root = Path(sys.argv[1]); label = sys.argv[2]
installer = root / "scripts" / "install.ps1"
tmp = Path(tempfile.mkdtemp(prefix="iexprobe-"))
home = tmp / "home"; (home / "hermes-agent").mkdir(parents=True)
(home / "hermes-agent" / "user-file").write_text("preserve me", encoding="utf-8")
tools = tmp / "tools"
for arch in ("x64", "arm64"):
    g = tools / f"git-2.53.0+3-win32-{arch}" / "cmd" / "git.exe"; g.parent.mkdir(parents=True); g.write_bytes(b"")
env = dict(os.environ, HERMES_HOME=str(home), HERMES_RUNTIME_DIR=str(tools))
cmd = f"iex (Get-Content -Raw -LiteralPath '{installer}'); Write-Output \"session alive: $LASTEXITCODE\""
out, err = tmp / "out.txt", tmp / "err.txt"
t0 = time.monotonic()
with open(out, "wb") as fo, open(err, "wb") as fe:
    p = subprocess.Popen([shutil.which("powershell"), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                         env=env, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL)
    try:
        rc = p.wait(timeout=400)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True); rc = "TIMEOUT"
el = time.monotonic() - t0
text = out.read_text(encoding="utf-8", errors="replace")
print(f"RESULT {label}: rc={rc} elapsed={el:.1f}s download={'installing git' in text} reinstall={'incomplete; reinstalling' in text} over60={el > 60}")
print("--- stdout ---"); print(text[-3000:]); print("--- stderr ---"); print(err.read_text(encoding="utf-8", errors="replace")[-1500:])
