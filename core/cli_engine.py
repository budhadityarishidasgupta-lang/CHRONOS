"""
core/cli_engine.py — Advanced Claude Code CLI Orchestrator
"""
import os
import subprocess
import json
import threading
from typing import Optional, Callable
from pathlib import Path

# Common paths for node/claude on macOS
BREW_PATH = "/opt/homebrew/bin"
LOCAL_BIN = os.path.expanduser("~/.local/bin")

class ClaudeCLIPredator:
    def __init__(self, claude_bin: str = "/opt/homebrew/bin/claude"):
        self.claude_bin = claude_bin
        self.env = os.environ.copy()
        
        # Ensure brew path is prioritized for node discovery
        path = self.env.get("PATH", "")
        self.env["PATH"] = f"{BREW_PATH}:{LOCAL_BIN}:{path}"

    def run_adversarial_audit(self, target_dir: str, task: str, on_data: Optional[Callable[[dict], None]] = None):
        """
        Executes a non-interactive, high-effort architectural audit using Claude CLI.
        """
        # We use --print for non-interactive and --output-format stream-json for structured data
        cmd = [
            self.claude_bin,
            "--print",
            "--verbose",
            "--dangerously-skip-permissions",
            "--output-format", "stream-json",
            task
        ]

        process = subprocess.Popen(
            cmd,
            cwd=target_dir,
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        try:
            for line in iter(process.stdout.readline, ""):
                if not line: break
                raw_line = line.strip()
                if not raw_line: continue
                
                try:
                    data = json.loads(raw_line)
                    if on_data:
                        on_data(data)
                except json.JSONDecodeError:
                    # If it's not JSON, it's likely an error message or a progress log
                    if "error" in raw_line.lower() or "not found" in raw_line.lower():
                        if on_data:
                            on_data({"type": "error", "message": raw_line})
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            raise
        
        return process.returncode
