"""
core/brain.py — Anthropic Deep-Audit Intelligence (ASYNCHRONOUS)
"""
import os
import json
import anthropic
import asyncio
from typing import List, Dict, Optional
from pathlib import Path

# The Security Brain
MODEL = "claude-3-5-sonnet-latest"

class SecurityBrain:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or os.environ.get("ANTHROPIC_API_KEY", "")).strip()
        self.org_id = os.environ.get("ANTHROPIC_ORG_ID", "e21999c6-2db6-417c-8a87-ed9bf84c1ab9").strip()
        self.client = anthropic.AsyncAnthropic(
            api_key=self.api_key,
            default_headers={
                "anthropic-organization-id": self.org_id,
                "anthropic-project-id": self.org_id  # Trying both for maximum compatibility
            }
        )

    async def audit_file(self, file_path: str, content: str) -> Optional[Dict]:
        """
        Sends a file to Claude 3.5 Sonnet for a deep security audit (Async).
        """
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
                messages=[{"role": "user", "content": prompt}]
            )
            raw_text = response.content[0].text
            # Strip markdown if present
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
                
            data = json.loads(raw_text)
            if data.get("status") == "safe":
                return None
            return data
        except Exception as e:
            return {"finding": f"AI Engine Error: {str(e)}", "severity": "ERROR", "error": True}
