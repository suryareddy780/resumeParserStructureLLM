import argparse
import json
import sys
from pathlib import Path
from parser import LLMResumeParser


def main():
    arg_parser = argparse.ArgumentParser(
        description="Resume Parser - Structured JSON Output via LLM Function Calling"
    )
    arg_parser.add_argument(
        "--file",
        type=str,
        default="sample_resumes/sample_resume.txt",
        help="Path to raw resume .txt file"
    )
    arg_parser.add_argument(
        "--out",
        type=str,
        default="",
        help="Optional output path to save extracted JSON"
    )
    args = arg_parser.parse_args()

    resume_path = Path(args.file)
    if not resume_path.exists():
        print(f"Error: Resume file not found at '{resume_path}'", file=sys.stderr)
        sys.exit(1)

    resume_text = resume_path.read_text(encoding="utf-8")
    parser = LLMResumeParser()
    mode = "LIVE OPENAI FUNCTION CALLING" if parser.api_key else "OFFLINE STRUCTURED SIMULATION"

    print("=" * 64)
    print(f"  LLM RESUME PARSER | MODE: {mode}")
    print(f"  Source File: {resume_path}")
    print("=" * 64)

    result = parser.parse(resume_text)
    formatted_json = json.dumps(result, indent=2)
    print(formatted_json)

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(formatted_json, encoding="utf-8")
        print(f"\nSaved structured JSON output to: {out_path}")


if __name__ == "__main__":
    main()
