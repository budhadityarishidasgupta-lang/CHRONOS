#!/usr/bin/env python3
"""
shadow.py — Shadow Swarm v4.4: High-Speed Hybrid Predator
"""
import os
import sys
import json
import click
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from core.cli_engine import ClaudeCLIPredator
from core.security_guidance import scan_patterns
from core.brain import SecurityBrain

console = Console()
load_dotenv()

class ShadowPredator:
    def __init__(self, target: str):
        target_path = Path(target).resolve()
        self.target_dir = target_path if target_path.is_dir() else target_path.parent
        self.target_file = target_path if target_path.is_file() else None
        
        self.cli_engine = ClaudeCLIPredator()
        self.brain = SecurityBrain()
        self.findings = []
        self.logs = []
        self.current_status = "Initializing..."
        self.max_ai_audit_files = 50
        self.semaphore = None # Initialized in run_audit

    def add_log(self, msg: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {msg}")
        if len(self.logs) > 15: self.logs.pop(0)

    def run_security_guidance_hook(self):
        """Phase 0: Deep Pattern Hook (Regex)"""
        self.current_status = "Phase 0: Scanning Official Patterns..."
        self.add_log("Launching Fast Pattern Sweep...")
        for root, _, filenames in os.walk(self.target_dir):
            if any(x in root for x in [".git", "venv", "node_modules"]): continue
            for f in filenames:
                if f.endswith((".py", ".ts", ".js")):
                    path = Path(root) / f
                    lang = "python" if f.endswith(".py") else "typescript"
                    try:
                        content = path.read_text()
                        findings = scan_patterns(content, lang)
                        for finding in findings:
                            self.findings.append({
                                "type": "HOOK",
                                "severity": "CRITICAL",
                                "text": f"PATTERN HIT: {finding['content']}",
                                "location": f"{f}:{finding['line']}"
                            })
                    except: pass

    async def audit_single_file(self, path: Path):
        """Async worker to audit a single file with the Deep Brain."""
        async with self.semaphore:
            self.add_log(f"🧠 Auditing: {path.name}...")
            try:
                content = path.read_text()
                if len(content) > 10000: content = content[:10000]
                
                finding = await self.brain.audit_file(str(path), content)
                if finding and "finding" in finding:
                    self.findings.append({
                        "type": "AI-BRAIN",
                        "severity": finding["severity"],
                        "text": f"RECON: {finding['finding']}",
                        "location": f"{path.name}"
                    })
                    self.add_log(f"🚩 FOUND: {finding['finding'][:30]}...")
                    
                    if finding["severity"] in ["CRITICAL", "HIGH"]:
                        await self.verify_with_cli_async(path, finding["finding"])
            except Exception as e:
                self.add_log(f"❌ Error in {path.name}: {str(e)[:40]}")

    async def verify_with_cli_async(self, path: Path, vuln: str):
        """Dispatches the CLI predator (Note: CLI is currently synchronous, but we wrap it)."""
        self.add_log(f"💥 CLAUDE-CLI DISPATCHED: proving {path.name}...")
        # Since the cli_engine is currently sync, we run it in an executor
        loop = asyncio.get_event_loop()
        task = f"Prove vulnerability in {path.name}: {vuln}. Start response with 'POC-RESULT:'"
        
        def poc_callback(data: dict):
            if data.get("type") == "assistant" and "message" in data:
                content = data["message"].get("content", [])
                for item in content:
                    if item.get("type") == "text" and "POC-RESULT:" in item["text"]:
                        self.findings.append({
                            "type": "POC-PROVEN",
                            "severity": "CRITICAL",
                            "text": item["text"].split("POC-RESULT:")[1].strip()[:100],
                            "location": path.name
                        })

        await loop.run_in_executor(None, self.cli_engine.run_adversarial_audit, str(self.target_dir), task, poc_callback)

    async def run_audit(self):
        """Main Async Audit Loop."""
        self.semaphore = asyncio.max_ai_audit_files = 50
        self.semaphore = asyncio.Semaphore(5)
        
        layout = Layout()
        layout.split_row(
            Layout(name="dashboard", ratio=2),
            Layout(name="log", ratio=1)
        )

        with Live(layout, refresh_per_second=4) as live:
            # 1. Regex Hooks
            self.run_security_guidance_hook()
            self.current_status = "Phase 1: Deep Brain Parallel Recon..."
            
            # 2. Gather AI Audit Tasks
            priority_keywords = ["auth", "security", "hook", "exec", "shell", "logic", "api"]
            all_files = []
            for root, _, filenames in os.walk(self.target_dir):
                if any(x in root for x in [".git", "venv", "node_modules"]): continue
                for f in filenames:
                    if f.endswith((".py", ".ts", ".js")):
                        all_files.append(Path(root) / f)

            all_files.sort(key=lambda p: any(k in p.name.lower() for k in priority_keywords), reverse=True)
            subset = all_files[:self.max_ai_audit_files]
            
            tasks = [self.audit_single_file(p) for p in subset]
            
            # Use periodic layout updates while gathering
            while tasks:
                done, tasks = await asyncio.wait(tasks, timeout=0.1, return_when=asyncio.FIRST_COMPLETED)
                layout["dashboard"].update(self.generate_table())
                layout["log"].update(self.generate_log_panel())

            self.current_status = "Audit Complete."
            layout["dashboard"].update(self.generate_table())
            layout["log"].update(self.generate_log_panel())

    def generate_table(self) -> Table:
        table = Table(title=f"🛡️ SHADOW SWARM: {self.current_status}", show_header=True, header_style="bold red")
        table.add_column("Type", width=12)
        table.add_column("Severity", width=10)
        table.add_column("Finding")
        table.add_column("Location")
        for f in self.findings:
            color = "red" if f["severity"] in ["CRITICAL", "HIGH"] else "yellow"
            if f["severity"] == "ERROR": color = "blue"
            table.add_row(f["type"], f"[{color}]{f['severity']}[/{color}]", f["text"][:60], f["location"])
        return table

    def generate_log_panel(self) -> Panel:
        log_text = Text.from_markup("\n".join(self.logs))
        return Panel(log_text, title="🛰️ PREDATOR FEED", border_style="dim")

@click.command()
@click.option("--target", "-t", default=".", help="Directory to scan")
def main(target):
    predator = ShadowPredator(target)
    asyncio.run(predator.run_audit())

if __name__ == "__main__":
    main()
