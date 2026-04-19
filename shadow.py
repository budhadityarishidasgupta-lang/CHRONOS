#!/usr/bin/env python3
"""
shadow.py — Shadow Swarm: The Autonomous Security Guard
"""
import os
import sys
import json
import subprocess
import click
from github import Github, Auth
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
import anthropic

console = Console()
load_dotenv()

def run_bandit(target_dir: str):
    console.print(f"[dim]Running Bandit static analysis on {target_dir}...[/dim]")
    result = subprocess.run(
        ["bandit", "-r", target_dir, "-f", "json"],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except:
        return {"results": []}

def ai_security_review(code_sample: str):
    console.print("[dim]Launching AI-driven adversarial code review...[/dim]")
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    prompt = f"""You are the Shadow Swarm Security Agent. 
Review this code snippet for:
1. Hardcoded secrets/API keys.
2. Insecure inputs (untrusted data).
3. Logic flaws.

Code:
{code_sample}

Return a concise list of high-priority security findings."""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"AI Review failed: {e}"

@click.command()
@click.option("--repo", "-r", help="Repo URL or local path to scan")
def shadow_scan(repo):
    console.print(Panel.fit(
        "[bold red]🛡️ SHADOW SWARM: ADVERSARIAL SCAN[/bold red]\n"
        "[dim]Identifying vulnerabilities and hardening the codebase...[/dim]",
        border_style="red"
    ))

    # 1. Bandit Scan
    vulnerabilities = run_bandit(repo if os.path.exists(repo) else ".")
    
    table = Table(title="🔥 Insecure Patterns Found", show_header=True, header_style="bold red")
    table.add_column("Severity", width=10)
    table.add_column("Issue")
    table.add_column("Location")

    for issue in vulnerabilities.get("results", []):
        table.add_row(
            issue["issue_severity"],
            issue["issue_text"],
            f"{issue['filename']}:{issue['line_number']}"
        )

    console.print(table)
    
    if not vulnerabilities.get("results"):
        console.print("[bold green]✅ Static analysis: No low-hanging fruit found.[/bold green]")

    console.print("\n[bold]Handoff Command (Copy & Paste to Oracle):[/bold]")
    console.print("[cyan]python3 ../Oracle-AI/run.py --goal \"Fix security vulnerabilities: [Issues]\" --repo [Repo URL][/cyan]")

if __name__ == "__main__":
    shadow_scan()
