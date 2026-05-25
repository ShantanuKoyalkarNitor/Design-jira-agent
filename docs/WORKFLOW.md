# Workflow Documentation

## End-to-End Review Workflow

This document describes the complete workflow of the Design Review Agent from ticket submission to final report.

## 1. Initiation

### Trigger Points

The review process can be triggered by:

1. **Manual Trigger**
   ```bash
   python src/cli.py review PROJ-123
   ```

2. **CI/CD Pipeline**
   ```yaml
   - name: Design Review
     run: python -m design_agent review ${{ github.event.inputs.ticket }}
   ```

3. **Scheduled Review**
   ```bash
   # Cron job for daily reviews
   0 9 * * * python src/scheduler.py review --project PROJ
   ```

4. **Webhook Trigger**
   - Jira webhook on ticket creation
   - GitHub webhook on PR with design changes

### Input Parameters

```python
{
    "jira_ticket": "PROJ-123",
    "design_documents": ["url1", "url2"],
    "artifact_urls": ["url3"],
    "scope": "full|requirement|architecture|security|scalability",
    "severity_threshold": "high",
    "parallel_execution": true,
    "notify_on_complete": true
}
```

## 2. Data Extraction

### Extract from Jira

```
Jira Ticket
  ├─ Ticket ID & Summary
  ├─ Description
  ├─ Acceptance Criteria
  ├─ Custom Fields
  ├─ Issue Links
  └─ Attachments
```

**Actions**:
- Fetch ticket via REST API
- Parse description for requirements
- Extract acceptance criteria
- Discover linked design documents
- Retrieve project context

### Discover Artifacts

```
Design Artifacts
  ├─ Confluence Pages
  │   ├─ Design Document
  │   ├─ Architecture Diagram
  │   └─ API Specification
  ├─ GitHub Files
  │   ├─ README.md
  │   ├─ architecture/
  │   └─ api/
  └─ External URLs
      ├─ OpenAPI Spec
      └─ Diagrams
```

**Actions**:
- Discover linked documents
- Retrieve document content
- Parse specification files (OpenAPI, etc.)
- Cache artifact content

## 3. Analysis Phase

### Multi-Agent Analysis

Four specialized agents run in parallel:

#### Agent 1: Requirement Analysis
```
Input: Ticket description + acceptance criteria
Process:
  1. Extract all requirements
  2. Classify by type
  3. Validate clarity (0-100)
  4. Identify gaps
  5. Detect conflicts
Output: Structured requirements with clarity scores
```

#### Agent 2: Architecture Review
```
Input: Architecture documents + design decisions
Process:
  1. Review design against SOLID principles
  2. Validate design patterns
  3. Assess modularity
  4. Check scalability design
  5. Identify technical debt
Output: Architecture findings with severity levels
```

#### Agent 3: Security & Compliance
```
Input: Security requirements + API design
Process:
  1. Identify vulnerabilities
  2. Check data protection
  3. Validate authentication
  4. Assess compliance gaps
  5. Map to standards (GDPR, SOC2, etc.)
Output: Security findings with compliance status
```

#### Agent 4: Scalability Assessment
```
Input: Performance requirements + infrastructure design
Process:
  1. Estimate current capacity
  2. Identify bottlenecks
  3. Project growth scenarios
  4. Validate caching strategy
  5. Recommend scaling approach
Output: Capacity analysis with growth projections
```

### Execution Pattern

```
Agents run in parallel:
Agent 1 |━━━━━━━━━━━━━━━━━━━━━| → Findings A
Agent 2 |━━━━━━━━━━━━━━━━━━━━━| → Findings B
Agent 3 |━━━━━━━━━━━━━━━━━━━━━| → Findings C
Agent 4 |━━━━━━━━━━━━━━━━━━━━━| → Findings D
        ↓
     Aggregate Findings
        ↓
     Risk Classification
```

**Timeline**: ~60-120 seconds for complete analysis

## 4. Post-Processing

### Aggregate Findings

```python
findings = {
    "requirements": agent1_findings,
    "architecture": agent2_findings,
    "security": agent3_findings,
    "scalability": agent4_findings
}
```

### Risk Classification

Each finding is classified:

```json
{
  "severity": "critical|high|medium|low",
  "impact": "functional|performance|security|compliance",
  "priority": 1-100,
  "timeline": "immediate|short_term|medium_term|long_term",
  "effort": "low|medium|high|very_high"
}
```

### Generate Recommendations

For each finding:
1. Create specific, actionable recommendation
2. Estimate implementation effort
3. Specify prerequisites
4. Link to best practices
5. Provide implementation guidance

## 5. Report Generation

### Report Sections

1. **Executive Summary** (50-100 words)
   - Overview of findings
   - Critical issues count
   - Overall recommendation

2. **Requirements Analysis** (detailed)
   - Requirement clarity assessment
   - Gap analysis
   - Conflicting requirements

3. **Architecture Review** (detailed)
   - Component assessment
   - Pattern validation
   - Technical debt
   - Recommendations

4. **Security Review** (detailed)
   - Vulnerability findings
   - Compliance status
   - Risk assessment
   - Mitigation strategies

5. **Scalability Assessment** (detailed)
   - Capacity analysis
   - Bottleneck identification
   - Growth projections
   - Scaling recommendations

6. **Risk Matrix** (visual)
   - 2D matrix (Severity × Impact)
   - Color-coded findings
   - Distribution by category

7. **Recommendations** (prioritized)
   - By severity
   - By timeline
   - By effort

8. **Audit Trail**
   - Review date and time
   - Artifacts analyzed
   - Standards applied
   - Review execution details

### Report Formats

Generated in multiple formats:
- **Markdown**: Human-readable, version control friendly
- **HTML**: Interactive, styled for browsers
- **PDF**: Shareable, archive-ready
- **JSON**: Machine-readable, for tools integration

## 6. Integration & Notification

### Update Jira

```python
# Add comment with summary
jira.add_comment(
    ticket_id="PROJ-123",
    comment="""
    Design Review Complete
    - Critical Issues: 2
    - High Issues: 5
    - Recommendation: Approve with Conditions
    [View Full Report](report_url)
    """
)

# Update fields
jira.update_ticket(
    ticket_id="PROJ-123",
    updates={
        "customfield_10000": "Design Reviewed",
        "labels": ["design-review", "reviewed"]
    }
)
```

### Create Subtasks (Optional)

For each critical finding, optionally create subtasks:

```python
for critical_finding in critical_findings:
    jira.create_subtask(
        parent_id="PROJ-123",
        summary=f"Address: {critical_finding.title}",
        description=critical_finding.details,
        priority="Critical"
    )
```

### Send Notifications

```python
# Email to stakeholders
send_email(
    to=["[REDACTED_EMAIL_ADDRESS_6]"],
    subject=f"Design Review Report: {ticket_id}",
    body=report.generate_html(),
    attachments=[report_pdf]
)

# Slack notification
slack.post_message(
    channel="#design-reviews",
    text=f"""
    Design Review Complete: {ticket_id}
    Status: {status}
    Critical Issues: {critical_count}
    [View Report](link)
    """
)
```

### Store Report

```
reports/
├── PROJ-123-design-review.md
├── PROJ-123-design-review.html
├── PROJ-123-design-review.pdf
├── PROJ-123-findings.json
└── PROJ-123-audit.log
```

## 7. Follow-up & Tracking

### Tracking Findings

```python
# Track finding status
finding.status = "open|in_progress|resolved|closed"
finding.assigned_to = "developer_name"
finding.due_date = "2024-06-30"
finding.linked_issue = "PROJ-456"
```

### Remediation Timeline

```
Day 0:   Design Review Complete
Day 1-7: Critical issues must be addressed
Day 8-14: High severity issues started
Day 15-30: Medium issues in backlog
Day 30+: Low priority for future sprints
```

### Re-review Trigger

Automatic re-review triggered when:
- Related code PR is created
- Design document is updated
- Critical finding status changes
- Timeline milestone is reached

## 8. Quality Metrics

### Tracking KPIs

```yaml
metrics:
  - requirement_completeness: %
  - architecture_quality_score: 0-100
  - security_risk_level: low|medium|high
  - scalability_readiness: %
  - review_cycle_time: hours
  - findings_fixed_rate: %
  - rework_reduction: %
```

### Dashboard

Real-time dashboard showing:
- Reviews in progress
- Recent findings
- Remediation status
- Approval sign-offs
- Trend analysis

## 9. Continuous Improvement

### Feedback Loop

1. Track which recommendations are implemented
2. Measure impact of changes
3. Gather stakeholder feedback
4. Improve agent accuracy
5. Refine rules and thresholds

### Agent Fine-tuning

Based on user feedback:
- Adjust severity classifications
- Refine recommendation text
- Add custom rules
- Improve pattern detection

## Workflow Diagram

```
┌─────────────────────┐
│  Initiate Review    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Extract from Jira   │
│ & Discover Artifacts│
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Run 4 Agents        │
│ (in parallel)       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Classify & Prioritize│
│ Findings            │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Generate Report     │
│ (Multiple Formats)  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Update Jira &       │
│ Send Notifications  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Track Remediation   │
│ & Schedule Re-review│
└─────────────────────┘
```

---

**Version**: 1.0  
**Last Updated**: May 24, 2026
