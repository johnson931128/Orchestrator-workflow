from pathlib import Path
import shutil
import subprocess
import sys

ORCHESTRATOR_DIR = Path(__file__).parent
REPO_PATH = Path(r"C:\programing\SFML\CtrlKine-AMR")
TASK_FILE = ORCHESTRATOR_DIR / "tasks" / "NEXT_PLAN.md"

CODEX_PATH = shutil.which("codex.cmd")

if CODEX_PATH is None:
    raise RuntimeError("找不到 codex.cmd")


def run_git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=REPO_PATH,
        text=True,
        check=True,
    )


# 1. 開始前確認 repo 是乾淨的
status = subprocess.run(
    ["git", "status", "--porcelain"],
    cwd=REPO_PATH,
    text=True,
    capture_output=True,
    check=True,
)

if status.stdout.strip():
    print("Repository is not clean. Stop.")
    print(status.stdout)
    sys.exit(1)


# 2. 讀取 task
task = TASK_FILE.read_text(encoding="utf-8")

codex_prompt = f"""
{task}

Execution rules:

- Modify only files required by the task.
- Perform the requested build/tests.
- Update docs/agent/STATUS.md.
- Do NOT run git add, git commit, or git push.
- Git finalization is handled by the external orchestrator.
"""


# 3. 呼叫 Codex
codex_command = subprocess.list2cmdline(
    [
        CODEX_PATH,
        "exec",
        "-m",
        "gpt-5.6-sol",
        "-c",
        'model_reasoning_effort="high"',
        "--sandbox",
        "workspace-write",
        "-",
    ]
)

print("=== Running Codex ===")

result = subprocess.run(
    codex_command,
    cwd=REPO_PATH,
    input=codex_prompt,
    text=True,
    encoding="utf-8",
    shell=True,
)

if result.returncode != 0:
    print("Codex failed. Stop.")
    sys.exit(result.returncode)


# 4. 確認 Codex 真的有修改東西
status = subprocess.run(
    ["git", "status", "--porcelain"],
    cwd=REPO_PATH,
    text=True,
    capture_output=True,
    check=True,
)

if not status.stdout.strip():
    print("Codex completed but repository has no changes.")
    sys.exit(0)

print("=== Changes ===")
print(status.stdout)


# 5. Orchestrator 負責 Git
print("=== Commit ===")

run_git("add", "-A")
run_git("commit", "-m", "Complete orchestrated task")

print("=== Push ===")

run_git("push")

print("=== Done ===")