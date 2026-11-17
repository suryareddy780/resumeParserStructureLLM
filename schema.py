"""Strict JSON Schema definitions for Resume Extraction (LLM Structured Outputs / Function Calling)."""

RESUME_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Full legal or preferred name of the candidate."
        },
        "email": {
            "type": ["string", "null"],
            "description": "Primary email address if present."
        },
        "phone": {
            "type": ["string", "null"],
            "description": "Contact phone number if present."
        },
        "skills": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of technical, domain, and soft skills extracted from the resume."
        },
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "Job title or position."},
                    "company": {"type": "string", "description": "Company or organization name."},
                    "duration": {"type": "string", "description": "Employment date range or duration."},
                    "highlights": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Key responsibilities and measurable achievements."
                    }
                },
                "required": ["role", "company", "duration", "highlights"],
                "additionalProperties": False
            },
            "description": "Chronological work experience entries."
        },
        "total_years_experience": {
            "type": "number",
            "description": "Estimated total years of professional experience."
        }
    },
    "required": ["name", "email", "phone", "skills", "experience", "total_years_experience"],
    "additionalProperties": False
}

# Function Calling / Tool Declaration format compatible with OpenAI & Gemini APIs
EXTRACT_RESUME_TOOL = {
    "type": "function",
    "function": {
        "name": "save_parsed_resume",
        "description": "Extracts structured candidate details (name, skills, experience) from raw resume text into a validated JSON schema.",
        "parameters": RESUME_EXTRACTION_SCHEMA
    }
}
