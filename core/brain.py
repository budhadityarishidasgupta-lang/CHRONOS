"""
core/brain.py - Anthropic Deep-Audit Intelligence (asynchronous).
"""

import json
import os
from typing import Dict, Optional

try:
    import anthropic
except ImportError:  # pragma: no cover - handled at runtime
    anthropic = None


MODEL = "claude-3-5-sonnet-latest"


class SecurityBrain:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or os.environ.get("ANTHROPIC_API_KEY", "")).strip()
        self.org_id = os.environ.get("ANTHROPIC_ORG_ID", "").strip()
        self.client = None

        if anthropic is not None and self.api_key:
            default_headers = {}
            if self.org_id:
                default_headers["anthropic-organization-id"] = self.org_id
                default_headers["anthropic-project-id"] = self.org_id

            self.client = anthropic.AsyncAnthropic(
                api_key=self.api_key,
                default_headers=default_headers or None,
            )

    async def audit_file(self, file_path: str, content: str) -> Optional[Dict]:
        """
        Send a file to Claude for a deep security audit and parse JSON output.
        """
        if anthropic is None:
            return {
                "finding": "Anthropic SDK is not installed. Install dependencies before running AI audits.",
                "severity": "ERROR",
                "error": True,
            }

        if not self.api_key or self.client is None:
            return {
                "finding": "ANTHROPIC_API_KEY is not configured, so AI audits are disabled.",
                "severity": "ERROR",
                "error": True,
            }

        prompt = f"""You are a Red Team Security Expert.
Analyze this file for 'Logic Leaks', 'Auth Vulnerabilities', or 'Insecure Architecture'.
File Path: {file_path}

Code Content:
{content}

If you find a vulnerability, summarize it and the potential impact.
Return JSON ONLY:
{{
  "finding": "string",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "impact": "string",
  "logic_leak": boolean,
  "poc_hint": "Briefly describe how to prove this if possible"
}}
If no vulnerability is found, return {{"status": "safe"}}.
"""
        try:
            response = await self.client.messages.create(
                model=MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = response.content[0].text
            if "```json" in raw_text:
                raw_text = raw_text.split("```json", 1)[1].split("```", 1)[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```", 1)[1].split("```", 1)[0].strip()

            data = json.loads(raw_text)
            if data.get("status") == "safe":
                return None
            return data
        except Exception as exc:
            return {
                "finding": f"AI engine error: {str(exc)}",
                "severity": "ERROR",
                "error": True,
            }
