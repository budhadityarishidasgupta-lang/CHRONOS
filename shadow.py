#!/usr/bin/env python3
"""
shadow.py — Shadow Swarm v3: The Claude-Native Predator
"""
import os
import sys
import json
import click
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from core.cli_engine import ClaudeCLIPredator
from core.security_guidance import scan_patterns

console = Console()
load_dotenv()

class ShadowPredator:
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir).resolve()
        self.engine = ClaudeCLIPredator()
        self.findings = []
        self.current_status = "Initializing..."

    def log(self, msg: str, style: str = "dim"):
        console.print(f"[{style}]{msg}[/{style}]")

    def run_security_guidance_hook(self):
        """Phase 0: Deep Pattern Hook (Official Anthropic Inspired)"""
        self.current_status = "Phase 0: Scanning Official Patterns..."
        hooks_found = 0
        for root, _, filenames in os.walk(self.target_dir):
            if ".git" in root or "venv" in root: continue
            for f in filenames:
                if f.endswith(".py"):
                    path = Path(root) / f
                    try:
                        findings = scan_patterns(path.read_text(), "python")
                        for finding in findings:
                            self.findings.append({
                                "type": "HOOK",
                                "severity": "CRITICAL",
                                "text": f"OFFICIAL PATTERN: {finding['content']}",
                                "location": f"{f}:{finding['line']}"
                            })
                            hooks_found += 1
                    except: pass
        return hooks_found

    def process_claude_telemetry(self, data: dict):
        """Processes real-time JSON telemetry from the Claude CLI Engine."""
        if data.get("type") == "assistant" and "message" in data:
            content = data["message"].get("content", [])
            for item in content:
                if item.get("type") == "text":
                    text = item.get("text", "").strip()
                    if "VULNERABILITY:" in text.upper():
                        # Extract finding logic
                        self.findings.append({
                            "type": "AI-RECON",
                            "severity": "HIGH",
                            "text": text[:100] + "...",
                            "location": "Deep Architectural Analysis"
                        })
        
        elif data.get("type") == "tool_use":
            self.current_status = f"Claude Tool Use: {data.get('name')}"

    def run_audit(self):
        """Launches the Full-Spectrum Claude-Native Audit."""
        # 1. Run the Hooks
        self.run_security_guidance_hook()

        # 2. Launch the Claude Predator
        adversarial_task = (
            "Perform a high-effort adversarial security audit of this repository. "
            "Think like a Red Team expert. Specifically look for: "
            "1. Logic leaks in session or auth flows. "
            "2. Insecure shell commands or untrusted data handling. "
            "3. Hardcoded secrets. "
            "If you find a vulnerability, execute a safe local PoC to prove it. "
            "Report findings starting with the keyword 'VULNERABILITY:'"
        )

        with Live(self.generate_table(), refresh_per_second=4) as live:
            self.engine.run_adversarial_audit(
                str(self.target_dir), 
                adversarial_task,
                on_data=lambda d: self.update_live(live, d)
            )
        
        self.report()

    def update_live(self, live, data):
        self.process_claude_telemetry(data)
        live.update(self.generate_table())

    def generate_table(self) -> Table:
        table = Table(title=f"🛡️ Shadow Swarm: Predator Dashboard - {self.current_status}", show_header=True, header_style="bold red")
        table.add_column("Type", width=12)
        table.add_column("Severity", width=10)
        table.add_column("Finding")
        table.add_column("Location")

        for f in self.findings:
            color = "red" if f["severity"] == "CRITICAL" or f["severity"] == "HIGH" else "yellow"
            table.add_row(f["type"], f"[{color}]{f['severity']}[/{color}]", f[ "text"], f["location"])
        
        return table

    def report(self):
        console.print(Panel.fit(
            "[bold red]🛡️ SHADOW SWARM: FINAL PREDATOR READOUT[/bold red]\n"
            "[dim]Audit Complete. Vulnerabilities Logged above.[/dim]",
            border_style="red"
        ))

@click.command()
@click.option("--target", "-t", default=".", help="Directory to scan")
def main(target):
    console.print(Panel.fit(
        "[bold red]🛡️ SHADOW SWARM v3 — CLAUDE-NATIVE PREDATOR[/bold red]\n"
        "[dim]Official Claude-CLI Powered Adversarial Auditor[/dim]",
        border_style="red"
    ))
    
    predator = ShadowPredator(target)
    predator.run_audit()

if __name__ == "__main__":
    main()
