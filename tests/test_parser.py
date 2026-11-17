import unittest
from pathlib import Path
from parser import LLMResumeParser, validate_against_schema, SchemaValidationError


class TestResumeParserStructuredOutputs(unittest.TestCase):
    def setUp(self):
        self.parser = LLMResumeParser(api_key=None)
        self.sample_text = Path("sample_resumes/sample_resume.txt").read_text(encoding="utf-8")

    def test_extract_name_skills_experience(self):
        result = self.parser.parse(self.sample_text)
        self.assertEqual(result["name"], "Ananya Sharma")
        self.assertEqual(result["email"], "ananya.sharma@techmail.com")
        self.assertIn("Python", result["skills"])
        self.assertIn("Function Calling", result["skills"])
        self.assertEqual(len(result["experience"]), 2)
        self.assertEqual(result["experience"][0]["role"], "Senior AI Engineer")
        self.assertEqual(result["total_years_experience"], 5.5)

    def test_json_schema_compliance(self):
        result = self.parser.parse(self.sample_text)
        is_valid, msg = validate_against_schema(result)
        self.assertTrue(is_valid, msg)

    def test_schema_rejects_missing_required_field(self):
        invalid_payload = {"name": "Test User", "skills": ["Python"]}
        is_valid, msg = validate_against_schema(invalid_payload)
        self.assertFalse(is_valid)
        self.assertIn("Missing required field", msg)

    def test_schema_rejects_extra_properties(self):
        valid = self.parser.parse(self.sample_text)
        valid["unapproved_field"] = "hallucinated"
        is_valid, msg = validate_against_schema(valid)
        self.assertFalse(is_valid)
        self.assertIn("Unexpected additional fields", msg)

    def test_empty_resume_raises_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse("   ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
