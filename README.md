# CHRONOS

CHRONOS is a repo-review assistant for your local codebases. It combines:

- regex-based detection of risky code patterns
- Anthropic-powered file review for higher-level security issues
- optional Claude CLI follow-up to try to verify serious findings

It is best treated as an experimental reviewer for your own repositories, especially when you want a quick security-focused pass before or after changes.

## Best Use Cases

- review one of your own repos before pushing a branch
- run a quick security-oriented sweep on a newly cloned project
- inspect Python, JavaScript, or TypeScript code for risky patterns
- create a lightweight first-pass report before manual review

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

## Review Another Repo

This is the normal step-by-step workflow for using CHRONOS on one of your existing repos.

### 1. Keep CHRONOS in its own folder

Example local layout:

```text
C:\Projects\CHRONOS
C:\Projects\my-other-repo
```

### 2. Set up CHRONOS

From the CHRONOS folder:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Add your credentials

Copy `.env.example` to `.env`, then set:

- `ANTHROPIC_API_KEY`
- optional `ANTHROPIC_ORG_ID`
- optional `CLAUDE_BIN`

### 4. Point CHRONOS at the repo you want to review

Windows example:

```powershell
py shadow.py --target C:\path\to\your\repo
```

Single-file example:

```powershell
py shadow.py --target C:\path\to\your\repo\app\main.py
```

### 5. Read the findings in order

- `HOOK` means a concrete risky pattern matched
- `AI-BRAIN` means the model thinks there may be a vulnerability or design issue
- `POC-PROVEN` means the Claude CLI returned a proof-style result
- `CLI-ERROR` means the Claude CLI step was unavailable or failed

### 6. Fix, rerun, compare

Use CHRONOS as a repeated pass:

1. run review
2. inspect findings
3. patch your repo
4. rerun review

## CLI Usage

Scan a directory:

```bash
python shadow.py --target path/to/project
```

Scan a single file:

```bash
python shadow.py --target app/main.py
```

Review fewer files during a quick pass:

```bash
python shadow.py --target path/to/project --max-files 20
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

## Suggested Review Workflow

1. Run CHRONOS against a local project you own.
2. Review `HOOK` findings first because they identify concrete risky patterns.
3. Review `AI-BRAIN` findings for architecture or logic issues.
4. Treat `POC-PROVEN` output as a lead to validate manually, not final truth.
5. Fix confirmed issues and rerun the scan.

## Important Boundaries

- CHRONOS is strongest as a repo-review helper, not a final security authority.
- It currently focuses on Python, JavaScript, and TypeScript source files.
- It does not replace manual review, tests, or formal security assessment.

## License

MIT
