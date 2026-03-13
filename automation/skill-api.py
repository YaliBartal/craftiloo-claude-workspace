#!/usr/bin/env python3
"""
skill-api.py — Lightweight HTTP API for triggering skill-runner.py from n8n.

Runs on the host (not inside Docker). n8n calls this via HTTP Request nodes
instead of executeCommand nodes, since the n8n container doesn't have
python3 or claude installed.

Usage:
    python3 ~/workspace/automation/skill-api.py          # Start on port 5680
    python3 ~/workspace/automation/skill-api.py --port 5680

Endpoints:
    POST /run    — Run a skill.    Body: {"skill": "daily-market-intel", "flags": "--verbose"}
    POST /pull   — Git pull only.  Body: {} (no params needed)
    GET  /health — Health check.   Returns: {"status": "ok", "uptime": "..."}

n8n workflow calls:
    http://host.docker.internal:5680/run   (or http://172.17.0.1:5680/run from Docker)
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Lock

START_TIME = time.time()
RUNNER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill-runner.py")
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_SKILLS = {
    "daily-market-intel", "ppc-daily-health", "weekly-ppc-analysis",
    "ppc-tacos-optimizer", "ppc-portfolio-summary", "keyword-rank-optimizer",
    "ppc-bid-recommender", "ppc-search-term-harvester",
    "competitor-price-serp-tracker", "brand-analytics-weekly", "ppc-monthly-review",
    "ppc-agent", "ppc-agent-autonomous-tuesday", "ppc-agent-autonomous-friday",
}
ALLOWED_FLAGS = {"--dry-run", "--verbose", "--no-git"}

run_lock = Lock()


class SkillAPIHandler(BaseHTTPRequestHandler):

    def _send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_GET(self):
        if self.path == "/health":
            uptime = int(time.time() - START_TIME)
            self._send_json(200, {
                "status": "ok",
                "uptime_seconds": uptime,
                "runner": RUNNER_PATH,
            })
        elif self.path == "/syshealth":
            self._handle_syshealth()
        else:
            self._send_json(404, {"error": "Not found. Use GET /health, GET /syshealth, POST /run, or POST /pull"})

    def do_POST(self):
        try:
            body = self._read_body()
        except (json.JSONDecodeError, ValueError) as e:
            self._send_json(400, {"error": f"Invalid JSON: {e}"})
            return

        if self.path == "/run":
            self._handle_run(body)
        elif self.path == "/pull":
            self._handle_pull()
        else:
            self._send_json(404, {"error": "Not found. Use POST /run or POST /pull"})

    def _handle_run(self, body):
        skill = body.get("skill", "").strip()
        flags = body.get("flags", "").strip()

        # Validate skill name (prevent injection)
        if not skill or skill not in ALLOWED_SKILLS:
            self._send_json(400, {
                "error": f"Invalid skill: '{skill}'",
                "allowed": sorted(ALLOWED_SKILLS),
            })
            return

        # Validate flags
        flag_list = flags.split() if flags else []
        for f in flag_list:
            if f not in ALLOWED_FLAGS:
                self._send_json(400, {
                    "error": f"Invalid flag: '{f}'",
                    "allowed": sorted(ALLOWED_FLAGS),
                })
                return

        # Prevent concurrent runs
        if not run_lock.acquire(blocking=False):
            self._send_json(409, {
                "error": "Another skill is already running",
                "skill": skill,
            })
            return

        try:
            cmd = [sys.executable, RUNNER_PATH, skill] + flag_list
            self.log_message("Running: %s", " ".join(cmd))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 60 min hard limit (autonomous sessions need ~55 min)
                cwd=WORKSPACE,
            )

            # Try to parse structured output from skill-runner
            stdout = result.stdout.strip()
            try:
                output = json.loads(stdout.split("\n")[-1]) if stdout else {}
            except (json.JSONDecodeError, IndexError):
                output = {"raw_stdout": stdout[-500:] if stdout else ""}

            self._send_json(200, {
                "skill": skill,
                "exitCode": result.returncode,
                "status": "success" if result.returncode == 0 else "failed",
                "output": output,
                "stderr": result.stderr[-500:] if result.stderr else "",
            })

        except subprocess.TimeoutExpired:
            self._send_json(200, {
                "skill": skill,
                "exitCode": 2,
                "status": "timeout",
            })
        except Exception as e:
            self._send_json(500, {"error": str(e), "skill": skill})
        finally:
            run_lock.release()

    def _handle_syshealth(self):
        result = {"uptime_seconds": int(time.time() - START_TIME)}

        # Disk usage
        try:
            df_out = subprocess.check_output(
                ["df", "/", "--output=pcent"], text=True, timeout=5
            ).strip().split("\n")[-1].strip().rstrip("%")
            result["disk_pct"] = int(df_out)
        except Exception:
            result["disk_pct"] = None

        # Memory
        try:
            free_lines = subprocess.check_output(["free", "-m"], text=True, timeout=5).split("\n")
            parts = free_lines[1].split()
            total, used = int(parts[1]), int(parts[2])
            result["memory_pct"] = round(used / total * 100) if total > 0 else None
        except Exception:
            result["memory_pct"] = None

        # Load average
        try:
            with open("/proc/loadavg") as f:
                result["load_1m"] = float(f.read().split()[0])
        except Exception:
            result["load_1m"] = None

        # n8n health (HTTP)
        try:
            req = urllib.request.urlopen("http://localhost:5678/healthz", timeout=3)
            result["n8n_status"] = "up" if req.status == 200 else "down"
        except Exception:
            result["n8n_status"] = "down"

        # PostgreSQL (via docker ps)
        try:
            docker_out = subprocess.check_output(
                ["docker", "ps", "--filter", "name=postgres", "--format", "{{.Status}}"],
                text=True, timeout=5
            ).strip()
            result["postgres_status"] = "up" if "Up" in docker_out else "down"
        except Exception:
            result["postgres_status"] = "unknown"

        # Lock file staleness
        lockfile = "/tmp/claude-skill.lock"
        try:
            if os.path.exists(lockfile):
                age_min = round((time.time() - os.path.getmtime(lockfile)) / 60, 1)
                result["lock_file_stale_minutes"] = age_min
            else:
                result["lock_file_stale_minutes"] = None
        except Exception:
            result["lock_file_stale_minutes"] = None

        # Recent skill logs (last 24h)
        log_dir = "/var/log/claude"
        try:
            cutoff = time.time() - 86400
            logs = [
                f for f in os.listdir(log_dir)
                if f.endswith(".json") and os.path.getmtime(os.path.join(log_dir, f)) > cutoff
            ]
            result["skill_runs_24h"] = len(logs)
            failures = 0
            for log_file in logs[:50]:  # cap at 50 to avoid slowness
                try:
                    with open(os.path.join(log_dir, log_file)) as lf:
                        log_data = json.load(lf)
                        if log_data.get("exit_code", 0) != 0:
                            failures += 1
                except Exception:
                    pass
            result["skill_failures_24h"] = failures
        except Exception:
            result["skill_runs_24h"] = 0
            result["skill_failures_24h"] = 0

        self._send_json(200, result)

    def _handle_pull(self):
        try:
            result = subprocess.run(
                ["git", "pull", "--ff-only"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=WORKSPACE,
            )
            self._send_json(200, {
                "status": "success" if result.returncode == 0 else "failed",
                "exitCode": result.returncode,
                "output": result.stdout.strip(),
                "stderr": result.stderr.strip() if result.stderr else "",
            })
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def log_message(self, format, *args):
        sys.stderr.write(f"[skill-api] {self.log_date_time_string()} {format % args}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill runner HTTP API for n8n")
    parser.add_argument("--port", type=int, default=5680, help="Port to listen on (default: 5680)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), SkillAPIHandler)
    print(f"[skill-api] Listening on {args.host}:{args.port}")
    print(f"[skill-api] Runner: {RUNNER_PATH}")
    print(f"[skill-api] Workspace: {WORKSPACE}")
    print(f"[skill-api] Endpoints: POST /run, POST /pull, GET /health")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[skill-api] Shutting down")
        server.server_close()


if __name__ == "__main__":
    main()
