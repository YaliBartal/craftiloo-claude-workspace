#!/usr/bin/env python3
"""
skill-runner.py — Production runner for Claude Code skills.

Replaces the old run-skill.sh bash script with proper configuration,
structured logging, timeout management, and git integration.

Usage:
    python3 skill-runner.py <skill-name> [--dry-run] [--no-git] [--verbose]

Exit codes:
    0 = success
    1 = skill execution failed
    2 = timeout
    3 = git operation failed
    4 = configuration error
    5 = lock conflict (another skill is running)
"""

import argparse
import datetime
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:
    print(json.dumps({
        "skill": "unknown",
        "status": "failed",
        "exit_code": 4,
        "error": "pyyaml not installed. Run: pip3 install pyyaml"
    }))
    sys.exit(4)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class SkillConfig:
    """Loads config.yaml, merges defaults with per-skill overrides."""

    def __init__(self, skill_name: str, config_path: str):
        self.skill_name = skill_name

        if not os.path.exists(config_path):
            raise ConfigError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            raw = yaml.safe_load(f)

        defaults = raw.get("defaults", {})
        skills = raw.get("skills", {})

        if skill_name not in skills:
            raise ConfigError(
                f"Skill '{skill_name}' not found in config.yaml. "
                f"Available: {', '.join(skills.keys())}"
            )

        skill = skills[skill_name]

        # Merge: skill overrides defaults
        self.workspace = skill.get("workspace", defaults.get("workspace", "/home/yali/workspace"))
        self.log_dir = skill.get("log_dir", defaults.get("log_dir", "/var/log/claude"))
        self.model = skill.get("model", defaults.get("model", "claude-sonnet-4-6"))
        self.max_turns = skill.get("max_turns", defaults.get("max_turns", 30))
        self.timeout_minutes = skill.get("timeout_minutes", defaults.get("timeout_minutes", 15))
        self.git_pull = skill.get("git_pull", defaults.get("git_pull", True))
        self.git_commit = skill.get("git_commit", defaults.get("git_commit", True))
        self.git_push = skill.get("git_push", defaults.get("git_push", True))
        self.git_add_paths = skill.get("git_add_paths", defaults.get("git_add_paths", ["outputs/"]))
        self.commit_prefix = skill.get("commit_prefix", defaults.get("commit_prefix", "auto"))
        self.env_file = skill.get("env_file", defaults.get("env_file", ""))
        self.lockfile = skill.get("lockfile", defaults.get("lockfile", "/tmp/claude-skill.lock"))
        self.min_gap_minutes = skill.get("min_gap_minutes", defaults.get("min_gap_minutes", 2))
        self.slack_channel = skill.get("slack_channel", "")
        self.allowed_tools = skill.get("allowed_tools", defaults.get("allowed_tools", []))

        # Prompt: skill-specific or default
        default_prompt = f"Run the {skill_name} skill."
        self.prompt = skill.get("prompt", default_prompt)
        self.prompt_suffix = defaults.get("prompt_suffix", "")

    def full_prompt(self) -> str:
        """Returns skill prompt + prompt_suffix."""
        return f"{self.prompt.strip()}\n\n{self.prompt_suffix.strip()}"

    def allowed_tools_str(self) -> str:
        """Returns comma-separated allowed tools string for --allowedTools."""
        return ",".join(self.allowed_tools)


class ConfigError(Exception):
    pass


# ---------------------------------------------------------------------------
# Run Lock
# ---------------------------------------------------------------------------

class RunLock:
    """File-based lock to prevent concurrent skill runs.
    Also enforces min_gap_minutes between runs."""

    def __init__(self, lockfile: str, min_gap_minutes: int):
        self.lockfile = lockfile
        self.min_gap_minutes = min_gap_minutes
        self._fd = None

    def acquire(self) -> bool:
        """Try to acquire lock. Returns False if locked or gap not met."""
        import fcntl

        # Check gap: if lockfile exists and was recently modified, wait
        if os.path.exists(self.lockfile):
            mtime = os.path.getmtime(self.lockfile)
            age_minutes = (time.time() - mtime) / 60
            if age_minutes < self.min_gap_minutes:
                return False

        try:
            self._fd = open(self.lockfile, "w")
            fcntl.flock(self._fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Write PID and skill name for debugging
            self._fd.write(f"{os.getpid()}\n")
            self._fd.flush()
            return True
        except (OSError, IOError):
            if self._fd:
                self._fd.close()
                self._fd = None
            return False

    def release(self):
        """Release the lock."""
        import fcntl

        if self._fd:
            try:
                fcntl.flock(self._fd.fileno(), fcntl.LOCK_UN)
                self._fd.close()
            except (OSError, IOError):
                pass
            self._fd = None

    def __enter__(self):
        if not self.acquire():
            raise LockError("Could not acquire lock")
        return self

    def __exit__(self, *args):
        self.release()


class LockError(Exception):
    pass


# ---------------------------------------------------------------------------
# Git Manager
# ---------------------------------------------------------------------------

class GitManager:
    """Handles git pull/commit/push with proper error handling."""

    def __init__(self, workspace: str, add_paths: list):
        self.workspace = workspace
        self.add_paths = add_paths

    def _run(self, cmd: list, **kwargs) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            cwd=self.workspace,
            capture_output=True,
            text=True,
            timeout=60,
            **kwargs,
        )

    def current_sha(self) -> str:
        """Get current HEAD SHA."""
        try:
            r = self._run(["git", "rev-parse", "--short", "HEAD"])
            return r.stdout.strip() if r.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def pull(self) -> dict:
        """git pull --ff-only origin master."""
        sha_before = self.current_sha()
        result = {"success": False, "output": "", "sha_before": sha_before}

        try:
            r = self._run(["git", "pull", "--ff-only", "origin", "master"])
            result["output"] = r.stdout + r.stderr
            if r.returncode == 0:
                result["success"] = True
            else:
                # Try regular pull as fallback
                r2 = self._run(["git", "pull", "origin", "master"])
                result["output"] += "\n" + r2.stdout + r2.stderr
                result["success"] = r2.returncode == 0
        except subprocess.TimeoutExpired:
            result["output"] = "Git pull timed out after 60s"
        except Exception as e:
            result["output"] = str(e)

        return result

    def commit_and_push(self, skill_name: str, commit_prefix: str) -> dict:
        """Stage files, commit, push. Returns commit info."""
        result = {
            "success": False,
            "sha_after": "unknown",
            "files_changed": [],
            "output": "",
        }

        try:
            # Stage specified paths
            for path in self.add_paths:
                self._run(["git", "add", path])

            # Check if there are staged changes
            diff_check = self._run(["git", "diff", "--staged", "--quiet"])
            if diff_check.returncode == 0:
                # Nothing to commit
                result["success"] = True
                result["output"] = "No changes to commit"
                result["sha_after"] = self.current_sha()
                return result

            # Get list of changed files
            diff_names = self._run(["git", "diff", "--staged", "--name-only"])
            result["files_changed"] = diff_names.stdout.strip().split("\n") if diff_names.stdout.strip() else []

            # Commit
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            msg = f"{commit_prefix}: {skill_name} {date_str}"
            commit_r = self._run(["git", "commit", "-m", msg])
            result["output"] = commit_r.stdout + commit_r.stderr

            if commit_r.returncode != 0:
                result["output"] = f"Commit failed: {commit_r.stderr}"
                return result

            result["sha_after"] = self.current_sha()

            # Push
            push_r = self._run(["git", "push", "origin", "master"])
            result["output"] += "\n" + push_r.stdout + push_r.stderr

            if push_r.returncode != 0:
                result["output"] += "\nPush failed (commit was local only)"
                # Still mark success since commit worked
                result["success"] = True
                return result

            result["success"] = True

        except subprocess.TimeoutExpired:
            result["output"] = "Git operation timed out"
        except Exception as e:
            result["output"] = str(e)

        return result


# ---------------------------------------------------------------------------
# Structured Logger
# ---------------------------------------------------------------------------

class StructuredLogger:
    """JSON logging to /var/log/claude/{skill}-{timestamp}.json"""

    def __init__(self, log_dir: str, skill_name: str):
        self.log_dir = log_dir
        self.skill_name = skill_name
        self.start_time = None
        self.duration = 0
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
        self.log_file = os.path.join(log_dir, f"{skill_name}-{self.timestamp}.json")
        self.latest_link = os.path.join(log_dir, f"{skill_name}-latest.json")

        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)

    def start(self):
        self.start_time = datetime.datetime.now(datetime.timezone.utc)

    def finish(self, exit_code: int, claude_output: str, git_info: dict, error: str = None, config: dict = None):
        finish_time = datetime.datetime.now(datetime.timezone.utc)
        self.duration = int((finish_time - self.start_time).total_seconds()) if self.start_time else 0

        status_map = {0: "success", 1: "failed", 2: "timeout", 3: "git_error", 4: "config_error", 5: "lock_conflict"}
        status = status_map.get(exit_code, "unknown")

        log_entry = {
            "skill": self.skill_name,
            "started_at": self.start_time.isoformat() if self.start_time else None,
            "finished_at": finish_time.isoformat(),
            "duration_seconds": self.duration,
            "exit_code": exit_code,
            "status": status,
            "git_sha_before": git_info.get("sha_before", ""),
            "git_sha_after": git_info.get("sha_after", ""),
            "files_changed": git_info.get("files_changed", []),
            "claude_output_length": len(claude_output) if claude_output else 0,
            "claude_output_tail": claude_output[-3000:] if claude_output else "",
            "error": error,
            "config": config or {},
        }

        # Write log file
        try:
            with open(self.log_file, "w") as f:
                json.dump(log_entry, f, indent=2)

            # Update latest symlink
            if os.path.exists(self.latest_link):
                os.remove(self.latest_link)
            os.symlink(self.log_file, self.latest_link)
        except Exception as e:
            # Don't fail the run because of logging
            print(f"Warning: could not write log: {e}", file=sys.stderr)

    def log_path(self) -> str:
        return self.log_file


# ---------------------------------------------------------------------------
# Environment Loader
# ---------------------------------------------------------------------------

def load_env(env_file: str):
    """Parse .env file into os.environ. Handles single-quoted values, comments, empty lines."""
    if not env_file or not os.path.exists(env_file):
        return

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Split on first =
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            # Strip surrounding quotes (single or double)
            if len(value) >= 2:
                if (value[0] == "'" and value[-1] == "'") or (value[0] == '"' and value[-1] == '"'):
                    value = value[1:-1]
            os.environ[key] = value


# ---------------------------------------------------------------------------
# Claude Execution
# ---------------------------------------------------------------------------

def run_claude(config: SkillConfig, verbose: bool = False) -> tuple:
    """Execute claude CLI with timeout. Returns (exit_code, captured_output)."""

    cmd = [
        "claude",
        "-p", config.full_prompt(),
        "--max-turns", str(config.max_turns),
        "--output-format", "text",
        "--model", config.model,
    ]

    # Add allowed tools if configured
    tools_str = config.allowed_tools_str()
    if tools_str:
        cmd.extend(["--allowedTools", tools_str])

    timeout_seconds = config.timeout_minutes * 60

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=config.workspace,
        )

        output_lines = []
        start = time.time()

        # Read output line by line (allows verbose streaming)
        while True:
            # Check timeout
            elapsed = time.time() - start
            if elapsed > timeout_seconds:
                process.kill()
                process.wait(timeout=10)
                output_lines.append(f"\n--- TIMEOUT after {config.timeout_minutes} minutes ---")
                return 2, "\n".join(output_lines)

            line = process.stdout.readline()
            if line:
                output_lines.append(line.rstrip())
                if verbose:
                    print(line, end="", flush=True)
            elif process.poll() is not None:
                # Process finished
                break
            else:
                time.sleep(0.1)

        # Capture any remaining output
        remaining = process.stdout.read()
        if remaining:
            output_lines.append(remaining.rstrip())
            if verbose:
                print(remaining, end="", flush=True)

        exit_code = process.returncode
        output = "\n".join(output_lines)

        # Map claude exit codes: 0 = success, anything else = failure
        return (0 if exit_code == 0 else 1), output

    except FileNotFoundError:
        return 1, "Error: 'claude' command not found. Is Claude Code CLI installed and in PATH?"
    except Exception as e:
        return 1, f"Error running claude: {e}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run a Claude Code skill with config, logging, and git integration.",
        epilog="Exit codes: 0=success, 1=fail, 2=timeout, 3=git-error, 4=config-error, 5=lock-conflict",
    )
    parser.add_argument("skill", help="Skill name (must exist in config.yaml)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run without executing")
    parser.add_argument("--no-git", action="store_true", help="Skip git pull/commit/push")
    parser.add_argument("--verbose", action="store_true", help="Stream Claude output to terminal")
    parser.add_argument("--config", default=None, help="Path to config.yaml (default: auto-detect)")
    args = parser.parse_args()

    # Find config file
    if args.config:
        config_path = args.config
    else:
        # Look relative to this script's location
        script_dir = Path(__file__).parent
        config_path = str(script_dir / "config.yaml")

    # 1. Load config
    try:
        config = SkillConfig(args.skill, config_path)
    except ConfigError as e:
        error_json = {
            "skill": args.skill,
            "status": "failed",
            "exit_code": 4,
            "error": str(e),
        }
        print(json.dumps(error_json))
        sys.exit(4)

    # 2. Dry run mode
    if args.dry_run:
        print(f"=== DRY RUN: {args.skill} ===")
        print(f"Workspace:  {config.workspace}")
        print(f"Model:      {config.model}")
        print(f"Max turns:  {config.max_turns}")
        print(f"Timeout:    {config.timeout_minutes} min")
        print(f"Git:        pull={config.git_pull}, commit={config.git_commit}, push={config.git_push}")
        print(f"Add paths:  {config.git_add_paths}")
        print(f"Lock:       {config.lockfile}")
        print(f"Slack:      {config.slack_channel}")
        print(f"Log dir:    {config.log_dir}")
        print(f"Env file:   {config.env_file}")
        print(f"Tools:      {len(config.allowed_tools)} configured")
        print(f"\n--- Prompt ---")
        print(config.full_prompt()[:500])
        if len(config.full_prompt()) > 500:
            print(f"... ({len(config.full_prompt())} chars total)")
        sys.exit(0)

    # 3. Load environment
    load_env(config.env_file)

    # 4. Initialize logger
    logger = StructuredLogger(config.log_dir, args.skill)
    logger.start()

    git_info = {}
    exit_code = 0
    output = ""
    error_msg = None

    # 5. Acquire lock
    lock = RunLock(config.lockfile, config.min_gap_minutes)
    if not lock.acquire():
        error_msg = "Lock conflict: another skill is running or min gap not met"
        logger.finish(5, "", {}, error_msg, {"timeout": config.timeout_minutes, "max_turns": config.max_turns})
        summary = {
            "skill": args.skill,
            "status": "lock_conflict",
            "exit_code": 5,
            "duration_seconds": 0,
            "log_file": logger.log_path(),
            "error": error_msg,
        }
        print(json.dumps(summary))
        sys.exit(5)

    try:
        # 6. Git pull
        git = GitManager(config.workspace, config.git_add_paths)

        if config.git_pull and not args.no_git:
            git_info = git.pull()
            if not git_info["success"]:
                exit_code = 3
                error_msg = f"Git pull failed: {git_info.get('output', '')}"
                logger.finish(exit_code, "", git_info, error_msg)
                summary = {
                    "skill": args.skill,
                    "status": "git_error",
                    "exit_code": exit_code,
                    "duration_seconds": logger.duration,
                    "log_file": logger.log_path(),
                    "error": error_msg,
                }
                print(json.dumps(summary))
                sys.exit(exit_code)
        else:
            git_info = {"sha_before": git.current_sha()}

        # 7. Change to workspace
        os.chdir(config.workspace)

        # 8. Run Claude
        exit_code, output = run_claude(config, verbose=args.verbose)

        # 9. Git commit/push (only on success)
        if config.git_commit and not args.no_git and exit_code == 0:
            commit_info = git.commit_and_push(args.skill, config.commit_prefix)
            git_info.update(commit_info)
            if not commit_info["success"]:
                # Don't fail the whole run for a git push issue
                error_msg = f"Git commit/push issue: {commit_info.get('output', '')}"

        # 10. Write structured log
        run_config = {
            "timeout_minutes": config.timeout_minutes,
            "max_turns": config.max_turns,
            "model": config.model,
        }
        logger.finish(exit_code, output, git_info, error_msg, run_config)

        # 11. Print JSON summary to stdout (for n8n to capture)
        summary = {
            "skill": args.skill,
            "status": "success" if exit_code == 0 else ("timeout" if exit_code == 2 else "failed"),
            "exit_code": exit_code,
            "duration_seconds": logger.duration,
            "log_file": logger.log_path(),
            "files_changed": git_info.get("files_changed", []),
            "claude_output_tail": output[-2000:] if output else "",
        }
        if error_msg:
            summary["error"] = error_msg

        print(json.dumps(summary))
        sys.exit(exit_code)

    finally:
        lock.release()


if __name__ == "__main__":
    main()
