# AntiShlop Security Agent

AI-powered security analysis agent for code files.

## Installation

```bash
pip install antishlopcli
```

## Usage

```bash
# Analyze a single file (recommended)
antishlop /path/to/file.py

# Analyze entire directory (not recommended - slow and huge reports)
antishlop /path/to/project

# Save report to JSON
antishlop file.py -o report.json
```

## Features

- **AI Security Agent**: Uses GPT-4.1 agent to detect vulnerabilities
- **15+ Security Tools**: SQL injection, XSS, path traversal, crypto issues, and more
- **Live Token Counter**: Shows real-time LLM token usage during analysis
- **Reflection System**: Agent automatically performs deeper analysis when needed
- **Multiple Languages**: Python, JavaScript, Ruby, Go, PHP, Java, C/C++, C#

## Output

- Real-time analysis progress with token counter
- Color-coded terminal output
- Detailed vulnerability reports
- JSON export for CI/CD integration

## Performance

**Important**: Analyze files individually. Directory analysis will be very slow and generate unreadable reports.

```bash
# Recommended
antishlop src/auth.py
antishlop src/database.py

# Not recommended (slow, huge report)
antishlop src/
```

## Requirements

- Python 3.8+
- OpenAI API key (set as OPENAI_API_KEY environment variable)