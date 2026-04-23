"""
core/cli_engine.py - Advanced Claude Code CLI orchestration.
"""

import json
import os
import shutil
import subprocess
from typing import Callable, Optional


BREW_PATH = "/opt/homebrew/bin"
LOCAL_BIN = os.path.expanduser("~/.local/bin")


class ClaudeCLIPredator:
    def __init__(self, claude_bin: Optional[str] = None):
        self.env = os.environ.copy()

        path_entries = [BREW_PATH, LOCAL_BIN, self.env.get("PATH", "")]
        self.env["PATH"] = os.pathsep.join([entry for entry in path_entries if entry])
        self.claude_bin = claude_bin or self._detect_claude_binary()

    def _detect_claude_binary(self) -> Optional[str]:
        configured = os.environ.get("CLAUDE_BIN", "").strip()
        if configured:
            return configured
        return shutil.which("claude", path=self.env.get("PATH"))

    def run_adversarial_audit(
        self,
        target_dir: str,
        task: str,
        on_data: Optional[Callable[[dict], None]] = None,
    ):
        """
        Execute a non-interactive architectural audit using Claude CLI.
        """
        if not self.claude_bin:
            if on_data:
                on_data(
                    {
                        "type": "error",
                        "message": "Claude CLI not found on PATH. Install it or set CLAUDE_BIN.",
                    }
                )
            return 127

        cmd = [
            self.claude_bin,
            "--print",
            "--verbose",
            "--dangerously-skip-permissions",
            "--output-format",
            "stream-json",
            task,
        ]

        process = subprocess.Popen(
            cmd,
            cwd=target_dir,
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        try:
            for line in iter(process.stdout.readline, ""):
                if not line:
                    break
                raw_line = line.strip()
                if not raw_line:
                    continue

                try:
                    data = json.loads(raw_line)
                    if on_data:
                        on_data(data)
                except json.JSONDecodeError:
                    if "error" in raw_line.lower() or "not found" in raw_line.lower():
                        if on_data:
                            on_data({"type": "error", "message": raw_line})
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            raise

        return process.returncode
