from pathlib import Path
import shutil
import subprocess
import sys


ORCHESTRATOR_DIR = Path(__file__).resolve().parent
REPO_PATH = Path(r"C:\programing\SFML\CtrlKine-AMR")
TASK_DIR = ORCHESTRATOR_DIR / "tasks"
TASK_FILE = TASK_DIR / "NEXT_PLAN.md"
PHASE_DIR = TASK_DIR / "phases"
PHASE_FILES = (
    PHASE_DIR / "ARCHITECTURE.md",
    PHASE_DIR / "UI_REFACTOR.md",
    PHASE_DIR / "LIDAR_360.md",
    PHASE_DIR / "VERIFICATION.md",
)

CODEX_PATH = shutil.which("codex.cmd")

if CODEX_PATH is None:
    raise RuntimeError("codex.cmd was not found on PATH")


# Validate the complete task package before starting any Codex run. Only the
# master plan is sent in the initial prompt; phase files remain on disk and
# are exposed to Codex through --add-dir for on-demand reading.
required_task_files = (TASK_FILE, *PHASE_FILES)
missing_task_files = [path for path in required_task_files if not path.is_file()]
if missing_task_files:
    print("Missing required task files. Stop.")
    for path in missing_task_files:
        print(f"- {path}")
    sys.exit(1)


def run_git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=REPO_PATH,
        text=True,
        check=True,
    )


# 1. Verify that the target repository is clean before Codex starts.
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


# 2. Read only the master plan. Phase work packages are intentionally not
# copied into the target repository or embedded in this prompt.
task = TASK_FILE.read_text(encoding="utf-8")
phase_paths = "\n".join(f"- {path}" for path in PHASE_FILES)

codex_prompt = f"""
Master Plan:
{task}

Phase work packages:
The following phase files are available for on-demand reading through the
additional directory granted to this Codex run. Read a phase file only when
the Master Plan routes you to it:
{phase_paths}

Do not copy these phase files into the target repository. Do not modify the
orchestrator task package.

Execution rules:

- Modify only files required by the task.
- Perform the requested build/tests.
- Update docs/agent/STATUS.md.
- Do NOT run git add, git commit, or git push.
- Git finalization is handled by the external orchestrator.
"""


# 3. Run Codex. Passing an argv list lets Python handle Windows argument
# boundaries and quoting, including any future spaces in the phase path.
codex_args = [
    CODEX_PATH,
    "exec",
    "-m",
    "gpt-5.6-sol",
    "-c",
    'model_reasoning_effort="high"',
    "--sandbox",
    "workspace-write",
    "--add-dir",
    str(PHASE_DIR),
    "-",
]

print("=== Running Codex ===")
print(subprocess.list2cmdline(codex_args))

result = subprocess.run(
    codex_args,
    cwd=REPO_PATH,
    input=codex_prompt,
    text=True,
    encoding="utf-8",
)

if result.returncode != 0:
    print("Codex failed. Stop.")
    sys.exit(result.returncode)


# 4. Verify Codex changes before orchestrator-owned Git finalization.
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


# 5. The orchestrator owns Git finalization.
print("=== Commit ===")

run_git("add", "-A")
run_git("commit", "-m", "Complete orchestrated task")

print("=== Push ===")

run_git("push")

print("=== Done ===")
