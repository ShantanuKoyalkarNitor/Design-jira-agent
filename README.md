# Jira Design Review Agent

This project reviews Jira tickets with a small group of AI agents and saves the results as JSON, Markdown, and text files.

It checks:

- Requirements extraction
- Design document quality
- Security gaps
- Scalability concerns

## What You Need

Install these first:

- Python 3.10 or newer
- `pip`
- Access to the Jira project you want to review
- A Jira email or username and API token
- One LLM provider, such as OpenAI or Ollama

Optional, but useful:

- Git
- VS Code

## Install

### 1. Create a virtual environment

PowerShell on Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Python packages

```bash
pip install -r requirements.txt
```

If you want to use a local Ollama model, install Ollama separately and make sure the Ollama server is running.

## Set Up Environment

Copy `.env.example` to `.env`, then fill in your own values.

### Required values

```bash
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
```

### Choose one LLM provider

OpenAI:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini
```

Google Gemini:

```bash
LLM_PROVIDER=google
GOOGLE_API_KEY=your-google-api-key
GOOGLE_MODEL=gemini-2.5-flash-lite
```

Ollama:

```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

Mistral:

```bash
LLM_PROVIDER=mistral
MISTRAL_API_KEY=your-mistral-key
MISTRAL_MODEL=mistral-large
```

If you do not set `LLM_PROVIDER`, the runner starts in offline fallback mode.

## How To Run

The main script is `run_all_agents.py`.

### Review one Jira ticket

Use one ticket ID if the same ticket contains both the requirements and the design:

```bash
python run_all_agents.py PROJ-123
```

### Review two Jira tickets

Use two ticket IDs if the requirements and the design live in different tickets:

```bash
python run_all_agents.py PROJ-123 PROJ-124
```

### What happens when it runs

The agent runs these steps in order:

1. Read the requirement ticket
2. Read the design ticket
3. Review the design against the requirements
4. Check security
5. Check scalability
6. Save the report files

## Output Files

Each run creates three files in the project folder:

- `review_results_<requirement>_vs_<design>_<timestamp>.json`
- `review_results_<requirement>_vs_<design>_<timestamp>.md`
- `review_results_<requirement>_vs_<design>_<timestamp>.txt`

## What The Agents Do

| Agent | Purpose |
| --- | --- |
| `requirement_analysis` | Pulls out the important requirements from the Jira ticket |
| `design_document_review` | Checks whether the design covers the requirements well |
| `design_security_review` | Looks for security problems and missing controls |
| `design_scalability_review` | Looks for performance and scaling risks |

## Simple Troubleshooting

### Jira ticket not found

- Check the ticket ID
- Check `JIRA_URL`
- Make sure your Jira user can open that project

### Login or auth error

- Recheck `JIRA_USERNAME`
- Recheck `JIRA_API_TOKEN`
- Make sure the Jira API token is still valid

### LLM error

- Check `LLM_PROVIDER`
- Make sure the matching API key is set
- If you are using Ollama, confirm the local server is running

### Missing Python package

- Run `pip install -r requirements.txt` again inside the virtual environment

## Project Files

- `run_all_agents.py` - main command-line entry point
- `src/run_agent.py` - runs each agent and parses results
- `src/jira_connector.py` - reads Jira tickets
- `src/llm_factory.py` - creates the selected LLM provider
- `agents/` - YAML config for each agent
- `prompts/` - prompt text used by each agent
- `config/` - API and review configuration

## Quick Example

```bash
python run_all_agents.py SK101-13 SK101-10
```

This will review the design ticket `SK101-10` using the requirements from `SK101-13`.
