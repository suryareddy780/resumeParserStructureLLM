# LLM Resume Parser (Structured Outputs & Function Calling)

Extracts candidate **Name**, **Contact Info**, **Skills**, and **Work Experience** from unstructured resume text into a strictly validated **JSON Schema** using LLM Function Calling / Structured Outputs.

## Project Structure
```text
resume-parser-structured-llm/
├── app.py                              # CLI entrypoint for parsing resumes to JSON
├── parser.py                           # LLM Function Calling client + JSON Schema validator
├── schema.py                           # Strict JSON Schema & OpenAI/Gemini tool definition
├── sample_resumes/
│   └── sample_resume.txt               # Sample unstructured candidate resume
├── tests/
│   └── test_parser.py                  # Unit tests for extraction & schema enforcement
├── requirements.txt                    # Zero third-party dependencies (Python 3.8+ stdlib)
├── .gitignore
└── README.md
```

## Usage
```bash
# 1. Run automated unit tests
python -m unittest discover -s tests -v

# 2. Parse sample resume (offline simulation mode - works out of the box)
python app.py --file sample_resumes/sample_resume.txt --out parsed_resume.json

# 3. Optional: Use live OpenAI Function Calling API
set OPENAI_API_KEY=sk-your-key-here
python app.py --file sample_resumes/sample_resume.txt
```
