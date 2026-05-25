# Quick Start Guide

Get up and running with the AI-Driven Design Review Agent in 10 minutes.

## Prerequisites

- Python 3.10 or higher
- Pip or conda package manager
- Jira account with API access
- OpenAI API key (or Azure OpenAI)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/design-jira-agent.git
cd design-jira-agent
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n design-review python=3.10
conda activate design-review
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your credentials
# JIRA_URL=https://your-org.atlassian.net
# JIRA_API_TOKEN=your-token
# OPENAI_API_KEY=sk-...
```

### 5. Run Your First Review

```bash
# Python script
python -m src review PROJ-123

# Or using CLI
python src/cli.py review PROJ-123

# Or using Python API
python -c "
from src import DesignReviewAgent
agent = DesignReviewAgent()
report = agent.review_design('PROJ-123')
print(report)
"
```

## Common Tasks

### Review a Design Document

```python
from src import DesignReviewAgent

agent = DesignReviewAgent()
report = agent.review_design(
    jira_ticket="PROJ-123",
    design_documents=["path/to/design.md"],
    artifact_urls=["https://confluence/page"]
)

# Save report
with open(f"reports/{report.ticket_id}-review.md", "w") as f:
    f.write(report.generate_markdown())
```

### Extract Requirements Only

```python
from src.agents import RequirementAnalysisAgent

agent = RequirementAnalysisAgent()
requirements = agent.analyze_requirements(
    ticket_id="PROJ-123"
)

print(f"Found {len(requirements)} requirements")
for req in requirements:
    print(f"- {req['id']}: {req['statement']}")
```

### Generate Security Report

```python
from src.agents import SecurityReviewAgent

agent = SecurityReviewAgent()
findings = agent.review_security(
    design_doc="architecture.md",
    compliance_standards=["GDPR", "SOC2"]
)

for finding in findings:
    print(f"[{finding['severity']}] {finding['vulnerability']}")
```

### Review via REST API

```bash
# Start the API server
python src/api.py --port 8000

# Make a review request
curl -X POST http://localhost:8000/api/reviews \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "ticket_id": "PROJ-123",
    "design_documents": ["url1"],
    "artifact_urls": ["url2"]
  }'
```

## Troubleshooting

### Authentication Errors

```
Error: 401 Unauthorized from Jira
```

**Solution**: Verify your API token and username in `.env`

```bash
# Test Jira connection
python -c "
from src.jira_connector import JiraConnector
jira = JiraConnector()
ticket = jira.get_ticket('DEMO-1')
print('Connection successful!')
"
```

### OpenAI API Errors

```
Error: Rate limit exceeded
```

**Solution**: Check your API quota and consider using batch requests

```bash
# Enable batch mode in config
BATCH_REQUESTS=true
```

### Missing Dependencies

```
ModuleNotFoundError: No module named 'openai'
```

**Solution**: Reinstall dependencies

```bash
pip install --upgrade -r requirements.txt
```

## Next Steps

1. **Explore Documentation**: Read [DESIGN.md](../DESIGN.md) for complete specification
2. **Configure Custom Rules**: Edit `config/custom_rules.yaml`
3. **Set Up CI/CD**: See [WORKFLOW.md](WORKFLOW.md) for integration examples
4. **Join Community**: Contribute improvements and share feedback

## Useful Commands

```bash
# Run tests
pytest

# Run with debug logging
DEBUG=true python src/cli.py review PROJ-123

# Run with specific agents only
python src/cli.py review PROJ-123 --agents security,architecture

# Generate sample report
python src/cli.py generate-sample-report

# Validate configuration
python src/cli.py validate-config

# List recent reviews
python src/cli.py list-reviews

# Export findings as CSV
python src/cli.py export PROJ-123 --format csv
```

## Configuration Files

- `.env`: Environment variables (credentials, API keys)
- `config/api_config.yaml`: API connectivity settings
- `config/review_config.yaml`: Review rules and criteria
- `config/custom_rules.yaml`: Domain-specific rules (if enabled)

## Getting Help

- **Documentation**: See [docs/](../docs/) folder
- **Issues**: Report on GitHub Issues
- **Discussions**: Join GitHub Discussions
- **Email**: [REDACTED_EMAIL_ADDRESS_5]

---

**Status**: Ready to use  
**Last Updated**: May 24, 2026
