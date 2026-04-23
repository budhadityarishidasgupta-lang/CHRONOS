#!/usr/bin/env python3
"""
shadow.py - CHRONOS repo review runner.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.brain import SecurityBrain
from core.cli_engine import ClaudeCLIPredator
from core.security_guidance import scan_patterns


load_dotenv()


class ShadowPredator:
    def __init__(self, target: str, max_files: int = 50):
        target_path = Path(target).resolve()
        self.target_dir = target_path if target_path.is_dir() else target_path.parent
        self.target_file = target_path if target_path.is_file() else None

        self.cli_engine = ClaudeCLIPredator()
        self.brain = SecurityBrain()
        self.findings = []
        self.logs = []
        self.current_status = "Initializing..."
        self.max_ai_audit_files = max_files
        self.semaphore = None

    def add_log(self, msg: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {msg}")
        if len(self.logs) > 15:
            self.logs.pop(0)

    def run_security_guidance_hook(self):
        """Phase 0: deep pattern hook (regex)."""
        self.current_status = "Phase 0: Scanning official patterns..."
        self.add_log("Launching fast pattern sweep...")
        for root, _, filenames in os.walk(self.target_dir):
            if any(x in root for x in [".git", "venv", "node_modules"]):
                continue
            for filename in filenames:
                if not filename.endswith((".py", ".ts", ".js")):
                    continue

                path = Path(root) / filename
                if filename.endswith(".py"):
                    lang = "python"
                elif filename.endswith(".js"):
                    lang = "javascript"
                else:
                    lang = "typescript"

                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    findings = scan_patterns(content, lang)
                except OSError as exc:
                    self.add_log(f"Error reading {path.name}: {str(exc)[:40]}")
                    continue

                for finding in findings:
                    self.findings.append(
                        {
                            "type": "HOOK",
                            "severity": "CRITICAL",
                            "text": f"PATTERN HIT: {finding['content']}",
                            "location": f"{filename}:{finding['line']}",
                        }
                    )

    async def audit_single_file(self, path: Path):
        """Async worker to audit a single file with the deep brain."""
        async with self.semaphore:
            self.add_log(f"Auditing: {path.name}...")
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if len(content) > 10000:
                    content = content[:10000]

                finding = await self.brain.audit_file(str(path), content)
                if finding and "finding" in finding:
                    self.findings.append(
                        {
                            "type": "AI-BRAIN",
                            "severity": finding["severity"],
                            "text": f"RECON: {finding['finding']}",
                            "location": path.name,
                        }
                    )
                    self.add_log(f"Found: {finding['finding'][:30]}...")

                    if finding["severity"] in ["CRITICAL", "HIGH"]:
                        await self.verify_with_cli_async(path, finding["finding"])
            except Exception as exc:
                self.add_log(f"Error in {path.name}: {str(exc)[:40]}")

    async def verify_with_cli_async(self, path: Path, vuln: str):
        """Dispatch the CLI predator from an executor."""
        self.add_log(f"Claude CLI dispatched: proving {path.name}...")
        loop = asyncio.get_running_loop()
        task = f"Prove vulnerability in {path.name}: {vuln}. Start response with 'POC-RESULT:'"

        def poc_callback(data: dict):
            if data.get("type") == "assistant" and "message" in data:
                content = data["message"].get("content", [])
                for item in content:
                    if item.get("type") == "text" and "POC-RESULT:" in item["text"]:
                        self.findings.append(
                            {
                                "type": "POC-PROVEN",
                                "severity": "CRITICAL",
                                "text": item["text"].split("POC-RESULT:", 1)[1].strip()[:100],
                                "location": path.name,
                            }
                        )
            elif data.get("type") == "error":
                self.findings.append(
                    {
                        "type": "CLI-ERROR",
                        "severity": "ERROR",
                        "text": data.get("message", "Claude CLI failed."),
                        "location": path.name,
                    }
                )

        await loop.run_in_executor(
            None,
            self.cli_engine.run_adversarial_audit,
            str(self.target_dir),
            task,
            poc_callback,
        )

    def collect_candidate_files(self):
        if self.target_file and self.target_file.suffix in {".py", ".ts", ".js"}:
            return [self.target_file]

        priority_keywords = ["auth", "security", "hook", "exec", "shell", "logic", "api"]
        all_files = []
        for root, _, filenames in os.walk(self.target_dir):
            if any(x in root for x in [".git", "venv", "node_modules"]):
                continue
            for filename in filenames:
                if filename.endswith((".py", ".ts", ".js")):
                    all_files.append(Path(root) / filename)

        all_files.sort(
            key=lambda path: any(keyword in path.name.lower() for keyword in priority_keywords),
            reverse=True,
        )
        return all_files[:self.max_ai_audit_files]

    async def run_audit(self):
        """Main async audit loop."""
        if not self.target_dir.exists():
            raise click.ClickException(f"Target path does not exist: {self.target_dir}")

        self.semaphore = asyncio.Semaphore(5)

        layout = Layout()
        layout.split_row(
            Layout(name="dashboard", ratio=2),
            Layout(name="log", ratio=1),
        )

        with Live(layout, refresh_per_second=4):
            self.add_log(f"Review target: {self.target_dir}")
            self.run_security_guidance_hook()
            self.current_status = "Phase 1: Deep brain parallel recon..."

            candidate_files = self.collect_candidate_files()
            if not candidate_files:
                self.current_status = "No supported source files found."
                layout["dashboard"].update(self.generate_table())
                layout["log"].update(self.generate_log_panel())
                return

            tasks = {
                asyncio.create_task(self.audit_single_file(path))
                for path in candidate_files
            }

            while tasks:
                _, pending = await asyncio.wait(
                    tasks,
                    timeout=0.1,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                layout["dashboard"].update(self.generate_table())
                layout["log"].update(self.generate_log_panel())
                tasks = pending

            self.current_status = "Audit complete."
            layout["dashboard"].update(self.generate_table())
            layout["log"].update(self.generate_log_panel())

    def generate_table(self) -> Table:
        table = Table(
            title=f"CHRONOS REPO REVIEW: {self.current_status}",
            show_header=True,
            header_style="bold red",
        )
        table.add_column("Type", width=12)
        table.add_column("Severity", width=10)
        table.add_column("Finding")
        table.add_column("Location")
        for finding in self.findings:
            color = "red" if finding["severity"] in ["CRITICAL", "HIGH"] else "yellow"
            if finding["severity"] == "ERROR":
                color = "blue"
            table.add_row(
                finding["type"],
                f"[{color}]{finding['severity']}[/{color}]",
                finding["text"][:60],
                finding["location"],
            )
        return table

    def generate_log_panel(self) -> Panel:
        log_text = Text.from_markup("\n".join(self.logs))
        return Panel(log_text, title="REVIEW FEED", border_style="dim")


@click.command()
@click.option("--target", "-t", default=".", help="Directory or file to scan")
@click.option("--max-files", default=50, show_default=True, type=int, help="Maximum files to send to AI review")
def main(target, max_files):
    predator = ShadowPredator(target, max_files=max_files)
    asyncio.run(predator.run_audit())


if __name__ == "__main__":
    main()
