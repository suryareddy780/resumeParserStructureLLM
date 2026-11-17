import json
import os
import re
import urllib.request
from typing import Any, Dict, List, Tuple
from schema import RESUME_EXTRACTION_SCHEMA, EXTRACT_RESUME_TOOL


class SchemaValidationError(Exception):
    """Raised when LLM output fails JSON Schema validation."""


def validate_against_schema(data: Dict[str, Any], schema: Dict[str, Any] = RESUME_EXTRACTION_SCHEMA) -> Tuple[bool, str]:
    """Lightweight strict JSON Schema validator (zero external dependencies)."""
    if not isinstance(data, dict):
        return False, "Root output must be a JSON object."

    required_keys = schema.get("required", [])
    for key in required_keys:
        if key not in data:
            return False, f"Missing required field: '{key}'"

    if schema.get("additionalProperties") is False:
        allowed = set(schema["properties"].keys())
        extra = set(data.keys()) - allowed
        if extra:
            return False, f"Unexpected additional fields: {sorted(extra)}"

    if not isinstance(data["name"], str) or not data["name"].strip():
        return False, "'name' must be a non-empty string."

    if data["email"] is not None and not isinstance(data["email"], str):
        return False, "'email' must be string or null."

    if data["phone"] is not None and not isinstance(data["phone"], str):
        return False, "'phone' must be string or null."

    if not isinstance(data["skills"], list) or not all(isinstance(s, str) for s in data["skills"]):
        return False, "'skills' must be an array of strings."

    if not isinstance(data["experience"], list):
        return False, "'experience' must be an array of objects."

    exp_required = {"role", "company", "duration", "highlights"}
    for idx, item in enumerate(data["experience"]):
        if not isinstance(item, dict):
            return False, f"experience[{idx}] must be an object."
        missing = exp_required - set(item.keys())
        if missing:
            return False, f"experience[{idx}] missing fields: {sorted(missing)}"
        if not isinstance(item["highlights"], list) or not all(isinstance(h, str) for h in item["highlights"]):
            return False, f"experience[{idx}].highlights must be an array of strings."

    if not isinstance(data["total_years_experience"], (int, float)):
        return False, "'total_years_experience' must be a number."

    return True, "Valid"


class LLMResumeParser:
    """
    Resume Parser using LLM API Structured Outputs & Function Calling.
    Supports live OpenAI-compatible endpoints (when OPENAI_API_KEY is set)
    and an offline deterministic Function-Calling simulator for local testing.
    """

    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

    def _call_live_llm_function(self, resume_text: str) -> Dict[str, Any]:
        """Calls LLM Chat Completions API forcing Function Calling / Structured Output."""
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert HR Resume Parser. Extract candidate name, contact info, skills, and work experience accurately by calling save_parsed_resume."
                },
                {"role": "user", "content": f"Parse the following resume:\n\n{resume_text}"}
            ],
            "tools": [EXTRACT_RESUME_TOOL],
            "tool_choice": {"type": "function", "function": {"name": "save_parsed_resume"}},
            "temperature": 0.0
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            tool_calls = body["choices"][0]["message"]["tool_calls"]
            arguments_json = tool_calls[0]["function"]["arguments"]
            return json.loads(arguments_json)

    def _simulate_llm_function_call(self, resume_text: str) -> Dict[str, Any]:
        """Deterministic fallback simulating LLM Function Calling JSON output."""
        lines = [ln.strip() for ln in resume_text.strip().splitlines() if ln.strip()]
        name = lines[0] if lines else "Unknown Candidate"

        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text)
        phone_match = re.search(r"(\+?\d[\d\s\-()]{8,16}\d)", resume_text)

        skills: List[str] = []
        for line in lines:
            if line.lower().startswith("skills:"):
                raw_skills = line.split(":", 1)[1]
                skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
                break

        experience: List[Dict[str, Any]] = []
        in_exp = False
        current_role = None

        for line in lines:
            low = line.lower()
            if low.startswith("experience"):
                in_exp = True
                continue
            if low.startswith("education") or low.startswith("skills:"):
                if in_exp and current_role:
                    experience.append(current_role)
                    current_role = None
                in_exp = False
                continue

            if in_exp:
                if "|" in line and not line.startswith("-"):
                    if current_role:
                        experience.append(current_role)
                    parts = [p.strip() for p in line.split("|")]
                    current_role = {
                        "role": parts[0] if len(parts) > 0 else "Role",
                        "company": parts[1] if len(parts) > 1 else "Company",
                        "duration": parts[2] if len(parts) > 2 else "N/A",
                        "highlights": []
                    }
                elif line.startswith("-") and current_role is not None:
                    current_role["highlights"].append(line.lstrip("- ").strip())

        if current_role:
            experience.append(current_role)

        years_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*years", resume_text, re.IGNORECASE)
        total_years = float(years_match.group(1)) if years_match else float(len(experience) * 2)

        return {
            "name": name,
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(1).strip() if phone_match else None,
            "skills": skills,
            "experience": experience,
            "total_years_experience": total_years
        }

    def parse(self, resume_text: str) -> Dict[str, Any]:
        """Extracts resume fields via LLM Function Calling & validates against JSON Schema."""
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text cannot be empty.")

        if self.api_key:
            structured_output = self._call_live_llm_function(resume_text)
        else:
            structured_output = self._simulate_llm_function_call(resume_text)

        is_valid, err = validate_against_schema(structured_output)
        if not is_valid:
            raise SchemaValidationError(f"LLM output failed JSON Schema check: {err}")

        return structured_output
