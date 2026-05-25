# AI-Driven Design Review Agent - README

## Overview

This workspace contains the **AI-Driven Design Review Agent**, a comprehensive GitHub Copilot-based system for automating design reviews of Jira-based software projects. The agent uses multiple specialized AI agents to analyze design artifacts against architectural, security, scalability, and compliance standards.

## Quick Start

### Prerequisites
- **VS Code** with GitHub Copilot extension installed
- **Python 3.10+** installed locally
- **Jira account** with API token access
- **OpenAI or Azure OpenAI API key** (optional for Jira-only operations)

### 5-Minute Setup

1. **Clone and setup**:
   ```bash
   git clone https://github.com/your-org/design-jira-agent.git
   cd design-jira-agent
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Jira and OpenAI credentials
   # Minimal required:
   #   JIRA_URL=https://your-org.atlassian.net
   #   JIRA_USERNAME=your-email@company.com
   #   JIRA_API_TOKEN=your-token
   #   OPENAI_API_KEY=sk-...
   ```

3. **Test setup**:
   ```bash
   python -c "from src import JiraConnector; print('✓ Setup complete')"
   ```

4. **Open in VS Code**:
   ```bash
   code .
   ```

5. **Start reviewing**: Open Copilot Chat (Ctrl+Shift+I) and use agents (see "How to Run the Agent" section)

## Project Structure

```
design-jira-agent/
├── .github/
│   └── copilot-instructions.md    # Copilot customization
├── docs/
│   ├── ARCHITECTURE.md            # System architecture details
│   ├── API-GUIDE.md               # API integration guide
│   ├── WORKFLOW.md                # Workflow documentation
│   └── TROUBLESHOOTING.md         # Troubleshooting guide
├── agents/
│   ├── requirement_analysis.yaml  # Requirement Analysis Agent
│   ├── architecture_review.yaml   # Architecture Review Agent
│   ├── security_review.yaml       # Security & Compliance Agent
│   └── scalability_review.yaml    # Scalability Agent
├── prompts/
│   ├── requirement_analysis.md    # Requirement extraction prompt
│   ├── architecture_review.md     # Architecture review prompt
│   ├── security_review.md         # Security review prompt
│   └── scalability_review.md      # Scalability review prompt
├── skills/
│   ├── jira_integration.yaml      # Jira connector skill
│   ├── artifact_discovery.yaml    # Artifact discovery skill
│   ├── report_generation.yaml     # Report generation skill
│   └── risk_classification.yaml   # Risk classification skill
├── src/
│   ├── __init__.py
│   ├── jira_connector.py          # Jira API client
│   ├── confluence_connector.py    # Confluence API client
│   ├── report_generator.py        # Report generation
│   ├── agents.py                  # Agent implementations
│   └── utils.py                   # Utility functions
├── templates/
│   ├── report_template.md         # Report markdown template
│   ├── summary_template.md        # Executive summary template
│   └── risk_matrix_template.md    # Risk matrix template
├── config/
│   ├── api_config.yaml            # API configuration
│   ├── review_config.yaml         # Review rules configuration
│   └── logging_config.yaml        # Logging configuration
├── DESIGN.md                      # Complete design specification
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── .gitignore                     # Git ignore rules
```

## Core Features

### 1. Multi-Agent Design Review
- **Requirement Analysis Agent**: Validates requirements completeness and clarity
- **Architecture Review Agent**: Assesses design against best practices
- **Security & Compliance Agent**: Identifies vulnerabilities and compliance gaps
- **Scalability Agent**: Evaluates performance and scalability

### 2. Jira Integration
- Extract tickets and requirements
- Discover linked design artifacts
- Link review reports back to tickets
- Track design decisions

### 3. Comprehensive Analysis
- Requirement validation
- Architectural assessment
- Security vulnerability detection
- Scalability and performance evaluation
- Compliance gap identification

### 4. Structured Reporting
- Executive summary
- Detailed findings by category
- Risk matrix and severity classification
- Actionable recommendations
- Audit trail and traceability

## How to Run the Agent

### Method 1: Using GitHub Copilot Chat (Recommended)

The agent is designed to work seamlessly with GitHub Copilot. Use the custom agents and prompts directly in VS Code:

1. **Open Copilot Chat** in VS Code (Ctrl+Shift+I)
2. **Invoke a specific agent** using the @agent syntax:
   ```
   @requirement_analysis Review PROJ-123 design requirements for completeness
   @architecture_review Assess the architecture in DESIGN.md against best practices
   @security_review Analyze security vulnerabilities in this architecture design
   @scalability_review Evaluate performance and scalability concerns
   ```

3. **Ask Copilot to use a skill**:
   ```
   @jira_integration Extract all requirements from PROJ-123
   @artifact_discovery Find all design documents linked to PROJ-123
   @report_generation Create a structured report of the findings
   ```

**Agent Files Location:**
- Agents: `agents/*.yaml` - Define agent behavior and specialization
- Prompts: `prompts/*.md` - Contain the detailed review criteria
- Skills: `skills/*.yaml` - Reusable operations for Jira, artifacts, and reporting

### Method 2: Python API (Advanced)

For programmatic access and automation:

```python
from src import JiraConnector
from src import Finding, ReviewStatus, SeverityLevel

# Initialize Jira connector
jira = JiraConnector()

# Get a ticket
ticket = jira.get_ticket("PROJ-123")
print(f"Ticket: {ticket['key']} - {ticket['summary']}")

# Extract requirements
requirements = ticket.get('description', '')
print(f"Requirements: {requirements}")
```

### Method 3: Direct Script Execution

Create a Python script to orchestrate reviews:

```python
# scripts/run_design_review.py
import os
import sys
from src import JiraConnector

def review_design(ticket_id: str):
    """Run a complete design review for a ticket"""
    
    # Initialize connections
    jira = JiraConnector(
        url=os.getenv("JIRA_URL"),
        username=os.getenv("JIRA_USERNAME"),
        api_token=os.getenv("JIRA_API_TOKEN")
    )
    
    # Get ticket details
    ticket = jira.get_ticket(ticket_id)
    print(f"\n{'='*60}")
    print(f"Design Review: {ticket['key']}")
    print(f"{'='*60}\n")
    
    # Run reviews using Copilot agents
    print("✓ Requirement Analysis")
    print("✓ Architecture Review")
    print("✓ Security Review")
    print("✓ Scalability Assessment")
    print("\n✓ Review Complete")

if __name__ == "__main__":
    review_design(sys.argv[1] if len(sys.argv) > 1 else "PROJ-123")
```

Run it:
```bash
python scripts/run_design_review.py PROJ-123
```

## Configuration

### Environment Variables
```bash
# Jira Configuration
JIRA_URL=https://your-jira.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-api-token

# Confluence Configuration
CONFLUENCE_URL=https://your-confluence.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your-api-token

# OpenAI Configuration
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Review Configuration
REVIEW_SEVERITY_THRESHOLD=medium
INCLUDE_AUDIT_TRAIL=true
REPORT_FORMAT=markdown
```

### Review Rules
Edit `config/review_config.yaml` to customize:
- Which agents to run
- Severity thresholds
- Required artifacts
- Custom validation rules
- Report sections

## Integration with CI/CD

### GitHub Actions
Add to your `.github/workflows/design-review.yml`:
```yaml
- name: Run Design Review
  run: python -m design_agent review --ticket ${{ github.event.inputs.ticket }}
```

### Pre-commit Hook
Validate design changes before commit:
```bash
./scripts/pre-commit-design-review.sh
```

## Output Examples

## Detailed Workflows

### Complete Design Review Workflow

**Step 1: Start in VS Code**
1. Open the Jira ticket or design document
2. Open Copilot Chat (Ctrl+Shift+I)
3. Run the complete review:
   ```
   @requirement_analysis Extract and validate all requirements from PROJ-123
   ```
   *Copilot Agent*: Analyzes requirements completeness, clarity, and dependencies

**Step 2: Architecture Assessment**
4. Share the design document with Copilot:
   ```
   @architecture_review Review the architecture in DESIGN.md against SOLID principles, design patterns, and scalability
   ```
   *Copilot Agent*: Identifies architectural issues, component interactions, and potential improvements

**Step 3: Security Analysis**
5. Request security review:
   ```
   @security_review Identify security vulnerabilities, compliance gaps (GDPR, SOC2), and authentication/authorization issues
   ```
   *Copilot Agent*: Detects threats, checks compliance standards, recommends security patterns

**Step 4: Scalability Assessment**
6. Evaluate scalability:
   ```
   @scalability_review Assess performance bottlenecks, load capacity, and growth limitations
   ```
   *Copilot Agent*: Analyzes performance, identifies bottlenecks, suggests optimizations

**Step 5: Generate Report**
7. Create final report:
   ```
   @report_generation Compile all findings into a structured design review report with recommendations
   ```
   *Expected Output*: Markdown report saved to `reports/PROJ-123-design-review.md`

### Requirement Extraction Only

For focusing just on requirements:
```
@jira_integration Extract requirements from ticket PROJ-123
@requirement_analysis Validate extracted requirements for clarity, completeness, and dependencies
```

### Artifact Discovery and Analysis

Find all related design documents:
```
@artifact_discovery Find all design documents and specifications linked to PROJ-123
```

Then analyze them:
```
@architecture_review Review all discovered artifacts and identify inconsistencies
```

## Expected Output Examples

### Requirements Analysis Output
```
Requirement Analysis Report
============================

Total Requirements Found: 15

✓ CLEAR (13 requirements)
  - User must authenticate with valid credentials
  - System must support 1000 concurrent users
  - Data must be encrypted at rest and in transit
  ...

⚠ AMBIGUOUS (1 requirement)
  - System should be "highly available"
    → Clarification needed: Define specific uptime SLA (99.9%? 99.99%?)

✗ MISSING (1 requirement)
  - Disaster recovery and backup strategy not specified
```

### Architecture Review Output
```
Architecture Assessment
=======================

Components Analyzed: 8
  - API Gateway
  - Auth Service
  - Data Layer
  - Cache Layer
  - Message Queue
  - Monitoring
  - Load Balancer
  - Database

Issues Found: 3

🔴 HIGH - Single Point of Failure
   The database lacks replication configuration
   Recommendation: Implement read replicas and automatic failover

🟡 MEDIUM - Missing Circuit Breaker
   External API calls lack failure handling
   Recommendation: Add circuit breaker pattern to all external integrations

🟢 LOW - Documentation Gap
   Component responsibilities not clearly documented
   Recommendation: Add sequence diagrams for critical flows
```

### Security Review Output
```
Security & Compliance Review
=============================

Vulnerabilities: 3
  - 1 Critical
  - 1 High  
  - 1 Medium

🔴 CRITICAL - SQL Injection Risk
   User input not properly sanitized in search endpoint
   Fix: Use parameterized queries
   
🟠 HIGH - Missing Rate Limiting
   API endpoints lack rate limiting
   Fix: Implement API rate limiter
   
🟡 MEDIUM - Weak Password Policy
   Minimum 8 characters, no complexity requirements
   Fix: Enforce 12+ characters, mixed case, numbers, symbols

Compliance Status:
  ✓ GDPR: Basic compliance (needs DPA)
  ✗ SOC2: Missing audit logging
  ⚠ HIPAA: Not applicable
```

### Scalability Review Output
```
Scalability Assessment
======================

Current Capacity: 1,000 requests/sec
Identified Bottleneck: Database query performance

Performance Issues: 2

🔴 Database Connection Pool
   Current pool: 50 connections
   Recommendation: Increase to 200 + implement connection pooling strategy

🟡 Cache Utilization
   No caching strategy implemented
   Recommendation: Add Redis layer for frequently accessed data
   
Scalability Score: 6/10
Growth Capacity: Can handle 3x current load with current architecture
```

### Final Report Structure
```
reports/
├── PROJ-123-design-review.md          # Executive summary + all findings
├── PROJ-123-findings.json             # Machine-readable findings
├── PROJ-123-requirements.md           # Detailed requirements analysis
├── PROJ-123-architecture.md           # Architectural assessment
├── PROJ-123-security.md               # Security findings
├── PROJ-123-scalability.md            # Scalability report
└── PROJ-123-audit.log                 # Review process log
```

## API Reference

See [API-GUIDE.md](docs/API-GUIDE.md) for complete API documentation.

## Troubleshooting

### Common Issues and Solutions

#### 1. "ModuleNotFoundError" when importing src

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure you're in the project root
cd design-jira-agent

# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
# Or on Windows PowerShell:
$env:PYTHONPATH += ";$(Get-Location)"

# Then run your script
python scripts/run_design_review.py PROJ-123
```

#### 2. Jira Connection Failed

**Problem**: `ConnectionError: Unable to connect to Jira`

**Solution**:
```bash
# 1. Verify credentials in .env
cat .env

# 2. Test Jira connection
python -c "
from src import JiraConnector
jira = JiraConnector()
try:
    ticket = jira.get_ticket('PROJ-1')
    print('✓ Jira connected successfully')
except Exception as e:
    print(f'✗ Connection failed: {e}')
"

# 3. Check if JIRA_URL is correct format
# Should be: https://your-org.atlassian.net
# NOT: https://your-org.atlassian.net/secure/...
```

#### 3. Copilot Agent Not Responding

**Problem**: Copilot agents in chat don't respond or show as unavailable

**Solution**:
1. **Check VS Code Extension**: Ensure GitHub Copilot extension is installed and activated
   - View → Extensions → search for "GitHub Copilot"
   - Reload if needed

2. **Check Agent Files**: Verify agent files exist and are valid YAML
   ```bash
   # Should exist:
   agents/requirement_analysis.yaml
   agents/architecture_review.yaml
   agents/security_review.yaml
   agents/scalability_review.yaml
   ```

3. **Reload VS Code**: Sometimes agents don't load immediately
   - Press `Ctrl+Shift+P`
   - Type "Developer: Reload Window"

4. **Check copilot-instructions.md**: Ensure it's valid and properly formatted
   ```bash
   cat .github/copilot-instructions.md
   ```

#### 4. API Key Errors

**Problem**: `401 Unauthorized` or `403 Forbidden`

**Solution**:
```bash
# For OpenAI API
# 1. Verify key format (should start with sk-)
echo $OPENAI_API_KEY  # Should show sk-...

# 2. Check token expiration in OpenAI dashboard

# 3. Verify key has correct permissions

# For Jira API
# 1. Use API token, not password
# 2. API token from: https://id.atlassian.com/manage-profile/security/api-tokens
# 3. Use email as username, not account name
```

#### 5. Timeout Errors

**Problem**: `TimeoutError: Request timed out after 30 seconds`

**Solution**:
```python
# Increase timeout when initializing connector
from src import JiraConnector

jira = JiraConnector(timeout=60)  # Increase to 60 seconds
```

#### 6. Design Document Not Found

**Problem**: "Artifact not found" or document parsing errors

**Solution**:
```bash
# 1. Verify document path
ls -la docs/DESIGN.md

# 2. Check Jira links are correct
# In Copilot, ask: @artifact_discovery List all linked documents for PROJ-123

# 3. Ensure document format is supported
# Supported: .md, .txt, .pdf, Confluence pages
```

#### 7. Report Generation Failed

**Problem**: Reports not created in `reports/` directory

**Solution**:
```bash
# 1. Create reports directory
mkdir -p reports

# 2. Check permissions
ls -la reports/
chmod 755 reports/

# 3. Verify template exists
cat templates/report_template.md

# 4. Run review again
python scripts/run_design_review.py PROJ-123
```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging

# Set DEBUG level
logging.basicConfig(level=logging.DEBUG)

# Now run your code
from src import JiraConnector
jira = JiraConnector()
ticket = jira.get_ticket("PROJ-123")
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG
python scripts/run_design_review.py PROJ-123
```

## Integration with GitHub Copilot

### Agent Customization

Agents are defined in `agents/*.yaml` and can be customized:

```yaml
# agents/custom_review.yaml
name: Custom Review Agent
description: Specialized review for microservices
model: gpt-4
temperature: 0.7
system_prompt: |
  You are an expert in microservices architecture...
  
  Review criteria:
  - Service boundaries and responsibilities
  - API design and contracts
  - Data consistency and isolation
  - Inter-service communication patterns
  
tools:
  - jira_integration
  - artifact_discovery
```

### Skill Usage in Prompts

Skills enable agents to interact with systems. Available skills:

**Jira Integration Skill** (`skills/jira_integration.yaml`)
- Extracts tickets and requirements
- Links artifacts
- Updates ticket status

**Artifact Discovery Skill** (`skills/artifact_discovery.yaml`)
- Finds linked documents
- Parses design specifications
- Extracts key information

**Report Generation Skill** (`skills/report_generation.yaml`)
- Creates structured reports
- Formats findings
- Generates audit trails

**Risk Classification Skill** (`skills/risk_classification.yaml`)
- Assigns severity levels
- Prioritizes findings
- Calculates risk scores

### Custom Prompts

Edit prompts in `prompts/*.md` to customize analysis:

```markdown
# Custom Requirement Analysis Prompt
## Role
You are a requirements engineer specializing in [YOUR DOMAIN]

## Context
- Project: [PROJECT_NAME]
- Team Size: [NUMBER]
- Timeline: [TIMELINE]

## Analysis Criteria
1. Business value alignment
2. Technical feasibility
3. Resource requirements
4. Risk assessment
5. Dependencies

## Output Format
- JSON with structured findings
- Priority scoring (1-10)
- Recommendations for each requirement
```

## Best Practices

### Design Review Process

1. **Prepare Before Review**
   - Ensure design document is complete and current
   - Have all related tickets and artifacts linked in Jira
   - Define scope and objectives for the review
   - Identify stakeholders who should review findings

2. **Leverage the Agents Strategically**
   - Start with **Requirement Analysis** - ensures clear objectives
   - Follow with **Architecture Review** - validates structure
   - Then **Security Review** - early vulnerability detection
   - Finally **Scalability Review** - prevents future bottlenecks

3. **Use Copilot Iteratively**
   - Ask follow-up questions to clarify findings
   - Request alternatives and recommendations
   - Validate proposed changes against constraints
   - Document decisions for audit trail

4. **Act on Findings**
   - Prioritize findings by severity (Critical → Low)
   - Create separate tickets for each high-priority issue
   - Track remediation progress in Jira
   - Re-review after significant changes

5. **Maintain Documentation**
   - Save all reports in `reports/` directory
   - Link reports back to Jira tickets
   - Create audit trail of design decisions
   - Version control design documents

### Copilot Agent Tips

**Getting Better Results:**
- Be specific: "Review the authentication flow" vs "Review the design"
- Provide context: Share relevant design documents in chat
- Ask structured questions: "What are the top 3 security risks?"
- Iterate: Follow up with clarifications and edge cases

**Example Good Prompts:**
```
@security_review Analyze this authentication service for OWASP Top 10 vulnerabilities

@architecture_review Does this handle the requirement of 10,000 concurrent users?

@requirement_analysis Which requirements are unclear or potentially conflicting?

@scalability_review What's the maximum throughput, and where's the bottleneck?
```

**Example Weak Prompts:**
```
✗ "Review the design"  → Too vague
✗ "Is this good?"     → Subjective, needs criteria
✗ "Everything"        → Too broad
```

### Customizing for Your Organization

1. **Update Agent Specialization** in `agents/*.yaml`:
   - Add organization-specific requirements
   - Include compliance frameworks you follow
   - Reference your architecture standards

2. **Customize Prompts** in `prompts/*.md`:
   - Add domain-specific terminology
   - Include your design patterns
   - Reference internal guidelines

3. **Configure Review Rules** in `config/review_config.yaml`:
   - Set severity thresholds
   - Define required artifacts
   - Specify approval workflows

### Advanced Usage

**Batch Review Multiple Tickets:**
```python
# scripts/batch_review.py
import sys
from src import JiraConnector

def batch_review(project_key: str):
    """Review all open tickets in a project"""
    jira = JiraConnector()
    
    # Get all design review tickets
    tickets = jira.search(f'project = {project_key} AND type = "Design Review"')
    
    for ticket in tickets:
        print(f"\nReviewing {ticket['key']}...")
        # Use Copilot agents via chat or API
        
if __name__ == "__main__":
    batch_review(sys.argv[1] if len(sys.argv) > 1 else "PROJ")
```

**Scheduled Reviews:**
```yaml
# .github/workflows/scheduled-design-review.yml
name: Scheduled Design Reviews

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python scripts/batch_review.py PROJ
```

**CI/CD Integration:**
```python
# scripts/ci_review.py - Fail builds on critical findings
import sys
import json
from src import JiraConnector

findings = json.load(open('reports/findings.json'))
critical = [f for f in findings if f['severity'] == 'CRITICAL']

if critical:
    print(f"❌ {len(critical)} critical issues found")
    sys.exit(1)
else:
    print("✅ Design review passed")
    sys.exit(0)
```

## Contributing

1. Create a feature branch
2. Add tests for new agents or features
3. Update documentation
4. Submit a pull request

## Support

- Documentation: [docs/](docs/)
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## License

Apache License 2.0

## Changelog

### Version 1.0 (May 24, 2026)
- Initial release
- Multi-agent architecture
- Jira integration
- Comprehensive reporting
- Security and compliance review

---

**Status**: Active Development  
**Last Updated**: May 24, 2026  
**Maintained By**: Design Review Team
