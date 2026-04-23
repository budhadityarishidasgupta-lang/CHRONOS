# Code Sentinel Audit

Shadow Swarm is a security-audit prototype that combines:

- regex-based detection of risky code patterns
- Anthropic-powered file review for higher-level security issues
- optional Claude CLI follow-up to try to verify serious findings

It is best treated as an experimental assistant for auditing your own codebases.

## What It Can Do

- scan Python, JavaScript, and TypeScript files for common dangerous patterns
- prioritize likely security-relevant files for AI review
- surface findings in a live Rich terminal dashboard
- optionally ask the Claude CLI to attempt proof-of-concept verification for severe findings

## Current Limits

- it is not a true multi-agent swarm; it is a single Python app orchestrating several audit steps
- AI review requires `ANTHROPIC_API_KEY`
- CLI proof mode requires the `claude` command on your `PATH`, or `CLAUDE_BIN` set explicitly
- findings are heuristic and should be reviewed by a human before acting on them

## Setup

### 1. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```env
ANTHROPIC_API_KEY=your_key_here
# Optional
ANTHROPIC_ORG_ID=your_org_or_project_id
CLAUDE_BIN=claude
```

## Usage

Scan a directory:

```bash
python shadow.py --target path/to/project
```

Scan a single file:

```bash
python shadow.py --target app/main.py
```

On Windows, if `python` is not on your `PATH`, use:

```powershell
py shadow.py --target .\some_project
```

## Smoke Test

Run the lightweight smoke test suite:

```bash
python -m unittest discover -s tests
```

On Windows:

```powershell
py -m unittest discover -s tests
```

## Suggested Workflow

1. Run a scan against a local project you own.
2. Review `HOOK` findings first because they identify concrete risky patterns.
3. Review `AI-BRAIN` findings for architecture or logic issues.
4. Treat `POC-PROVEN` output as a lead to validate manually, not final truth.
5. Fix confirmed issues and rerun the scan.

## License

MIT
