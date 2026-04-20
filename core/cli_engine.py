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
            "--dangerously-skip-permissions",
            "--effort", "high",
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
                try:
                    data = json.loads(line)
                    if on_data:
                        on_data(data)
                except json.JSONDecodeError:
                    # Handle raw text or partial lines if any
                    pass
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            raise
        
        return process.returncode
