# AI-Powered-PDF-Document-Summarizer

Flask document-summary prototype with user accounts, file upload handling, text extraction, and saved summaries.

## Setup and repository reference

### Project structure

- [file_handler.py](file_handler.py)
- [instance](instance)
- [requirements.txt](requirements.txt)
- [requirements_check.py](requirements_check.py)
- [static](static)
- [summarizer.py](summarizer.py)
- [tempCodeRunnerFile.py](tempCodeRunnerFile.py)
- [templates](templates)
- [web_app.py](web_app.py)

### Getting started

```bash
git clone https://github.com/Raimal-Raja/AI-Powered-PDF-Document-Summarizer.git
cd AI-Powered-PDF-Document-Summarizer
```

Create and activate a virtual environment, then install the project dependencies:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r "requirements.txt"
```

Application entry point:

```bash
python web_app.py
```

### Configuration and limitations

Inspect project-specific configuration and dependencies before running. Runtime behavior was not exhaustively verified in this audit.

### Validation

Audit: 2026-10-08. Repository structure, setup instructions and description were reviewed. 7 existing Python files passed syntax checks; changed files and new regression tests were checked separately. Syntax checks do not establish full runtime correctness. External APIs, live scraping, GUI interaction, notebook training and production deployment were not comprehensively exercised.

### Repository description

The short GitHub description is provided in [REPOSITORY_DESCRIPTION.md](REPOSITORY_DESCRIPTION.md).

### Contributions

Describe the issue, reproduction steps, environment, and expected behavior when proposing a change. Keep generated environments, credentials, and unnecessary build artifacts out of new commits.

### License

No top-level license file was found during this review.
