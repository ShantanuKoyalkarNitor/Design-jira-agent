#!/usr/bin/env python3
"""
Design Review Agent - Reviews design documents against Jira ticket requirements
Input: Requirement Ticket ID, Design Ticket ID
Output: Comprehensive design document review report
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Make console output safe on Windows shells that default to a legacy code page.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from run_agent import AgentRunner


def _as_lines(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _section_title(agent_name: str) -> str:
    return agent_name.replace("_", " ").title()


def _render_kv_table(data: dict) -> str:
    if not data:
        return ""

    rows = ["| Field | Value |", "| --- | --- |"]
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, indent=2, ensure_ascii=False)
            value = f"`{value}`"
        rows.append(f"| {key} | {str(value).replace('|', '\\|')} |")
    return "\n".join(rows)


def _render_findings(items, title, key_map):
    lines = [f"### {title}"]
    if not items:
        lines.append("No findings.")
        return "\n".join(lines)

    for idx, item in enumerate(items, start=1):
        issue_key = key_map.get("issue")
        issue_alt_key = key_map.get("issue_alt")
        issue_value = item.get(issue_key, "") if issue_key else ""
        if not issue_value and issue_alt_key:
            issue_value = item.get(issue_alt_key, "")
        lines.append(f"{idx}. {item.get(key_map['id'], 'N/A')} - {issue_value}")
        for field_label, field_key in key_map.get("details", []):
            value = item.get(field_key)
            if value:
                lines.append(f"   - {field_label}: {value}")
    return "\n".join(lines)


def _render_agent_report(agent_name: str, result: dict) -> str:
    analysis = result.get("analysis", {}) if isinstance(result, dict) else {}
    lines = [f"## {_section_title(agent_name)}"]

    if result.get("status") != "success":
        lines.append(f"Status: ERROR")
        lines.append(f"Error: {result.get('error', 'Unknown error')}")
        return "\n".join(lines)

    lines.append(f"Status: {result.get('status', 'unknown')}")
    lines.append(f"LLM Model: {result.get('llm_model', 'N/A')}")
    lines.append(f"Fallback Used: {result.get('fallback_used', False)}")

    if agent_name == "requirement_analysis":
        lines.append("")
        lines.append("### Summary")
        lines.append(_render_kv_table(analysis.get("summary", {})))
        lines.append("")
        lines.append("### Key Design Focus Areas")
        for item in analysis.get("key_design_focus_areas", []):
            lines.append(f"- {item.get('area', 'N/A')}: {item.get('description', '')}")
        lines.append("")
        lines.append(_render_findings(
            analysis.get("requirements", []),
            "Requirements",
            {
                "id": "id",
                "issue": "statement",
                "details": [("Type", "type"), ("Priority", "priority"), ("Focus Area", "design_focus_area")],
            },
        ))
        return "\n".join(lines)

    if agent_name == "design_document_review":
        lines.append("")
        lines.append("### Coverage")
        lines.append(_render_kv_table(analysis.get("requirements_coverage", {})))
        lines.append("")
        lines.append(_render_findings(
            analysis.get("design_findings", []),
            "Design Findings",
            {
                "id": "finding_id",
                "issue": "issue",
                "details": [("Severity", "severity"), ("Category", "category"), ("Effort", "effort"), ("Recommendation", "recommendation")],
            },
        ))
        lines.append("")
        lines.append("### Quality Assessment")
        lines.append(_render_kv_table(analysis.get("quality_assessment", {})))
        lines.append("")
        lines.append("### Summary")
        lines.append(_render_kv_table(analysis.get("summary", {})))
        return "\n".join(lines)

    if agent_name == "design_feasibility_review":
        repo_context = result.get("repository_context", {}) if isinstance(result, dict) else {}
        lines.append("")
        lines.append("### Feasibility Assessment")
        lines.append(_render_kv_table(analysis.get("feasibility_assessment", {})))
        lines.append("")
        lines.append("### Required Changes")
        required_changes = analysis.get("required_changes", [])
        if required_changes:
            for idx, item in enumerate(required_changes, start=1):
                lines.append(f"{idx}. {item.get('area', 'N/A')} - {item.get('change', '')}")
                lines.append(f"   - Priority: {item.get('priority', '')}")
                lines.append(f"   - Effort: {item.get('effort', '')}")
        else:
            lines.append("No required changes.")
        lines.append("")
        lines.append("### Implementation Steps")
        for step in analysis.get("implementation_steps", []):
            lines.append(f"- {step}")
        lines.append("")
        if repo_context:
            lines.append("### Repository Context")
            lines.append(_render_kv_table(repo_context))
            lines.append("")
        lines.append("### Feasibility Findings")
        lines.append(_render_findings(
            analysis.get("feasibility_findings", []),
            "Feasibility Findings",
            {
                "id": "finding_id",
                "issue": "issue",
                "details": [("Severity", "severity"), ("Category", "category"), ("Required Change", "required_change"), ("Recommendation", "recommendation")],
            },
        ))
        lines.append("")
        lines.append("### Summary")
        lines.append(_render_kv_table(analysis.get("summary", {})))
        return "\n".join(lines)

    if agent_name == "design_code_review":
        repo_context = result.get("repository_context", {}) if isinstance(result, dict) else {}
        lines.append("")
        lines.append("### Repository Context")
        lines.append(_render_kv_table(repo_context))
        lines.append("")
        lines.append("### Code Findings")
        lines.append(_render_findings(
            analysis.get("code_findings", []),
            "Code Findings",
            {
                "id": "finding_id",
                "issue": "issue",
                "details": [("Severity", "severity"), ("Category", "category"), ("File", "file_path"), ("Recommendation", "recommendation")],
            },
        ))
        lines.append("")
        lines.append("### Implementation Assessment")
        lines.append(_render_kv_table(analysis.get("implementation_assessment", {})))
        lines.append("")
        lines.append("### Summary")
        lines.append(_render_kv_table(analysis.get("summary", {})))
        return "\n".join(lines)

    if agent_name == "design_security_review":
        lines.append("")
        lines.append("### Security Findings")
        lines.append(_render_findings(
            analysis.get("security_findings", []),
            "Security Findings",
            {
                "id": "finding_id",
                "issue": "issue",
                "details": [("Severity", "severity"), ("Category", "category"), ("Recommendation", "recommendation")],
            },
        ))
        lines.append("")
        lines.append("### Coverage")
        lines.append(_render_kv_table(analysis.get("security_requirements_coverage", {})))
        lines.append("")
        lines.append("### Threat Assessment")
        lines.append(_render_kv_table(analysis.get("threat_assessment", {})))
        lines.append("")
        lines.append("### Summary")
        lines.append(_render_kv_table(analysis.get("summary", {})))
        return "\n".join(lines)

    if agent_name == "design_scalability_review":
        lines.append("")
        lines.append("### Scalability Findings")
        lines.append(_render_findings(
            analysis.get("scalability_findings", []),
            "Scalability Findings",
            {
                "id": "finding_id",
                "issue": "concern",
                "issue_alt": "aspect",
                "details": [("Severity", "severity"), ("Recommendation", "recommendation")],
            },
        ))
        lines.append("")
        lines.append("### Performance Assessment")
        lines.append(_render_kv_table(analysis.get("performance_assessment", {})))
        lines.append("")
        lines.append("### Summary")
        lines.append(_render_kv_table(analysis.get("summary", {})))
        return "\n".join(lines)

    lines.append("")
    lines.append("### Analysis")
    lines.append("```json")
    lines.append(json.dumps(analysis, indent=2, ensure_ascii=False))
    lines.append("```")
    return "\n".join(lines)


def render_markdown_report(all_results: dict) -> str:
    lines = [
        "# Design Document Review Report",
        "",
        f"- Requirement Ticket: `{all_results.get('requirement_ticket_id', '')}`",
        f"- Design Ticket: `{all_results.get('design_ticket_id', '')}`",
        f"- Timestamp: `{all_results.get('timestamp', '')}`",
        f"- Review Type: `{all_results.get('review_type', '')}`",
        "",
        "## Executive Summary",
    ]

    results = all_results.get("results", {})
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    fallback_count = sum(1 for r in results.values() if r.get("fallback_used"))
    error_count = sum(1 for r in results.values() if r.get("status") == "error")
    lines.append(f"- Successful agents: {success_count}")
    lines.append(f"- Fallback used: {fallback_count}")
    lines.append(f"- Errors: {error_count}")

    lines.append("")
    lines.append("## Agent Reports")
    agent_order = ["requirement_analysis", "design_document_review", "design_feasibility_review"]
    if "design_code_review" in results:
        agent_order.append("design_code_review")
    agent_order.extend(["design_security_review", "design_scalability_review"])

    for agent_name in agent_order:
        result = results.get(agent_name, {})
        lines.append(_render_agent_report(agent_name, result))
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def render_text_report(all_results: dict) -> str:
    md = render_markdown_report(all_results)
    plain = md.replace("```json", "").replace("```", "")
    plain = plain.replace("**", "")
    return plain


def review_design_document(requirement_ticket_id: str, design_ticket_id: str):
    """Review design document based on Jira ticket requirements
    
    Args:
        requirement_ticket_id: Ticket ID containing requirements
        design_ticket_id: Ticket ID containing design document
    """
    
    print("\n" + "=" * 80)
    print(f"DESIGN DOCUMENT REVIEW")
    print(f"Requirements: {requirement_ticket_id} | Design: {design_ticket_id}")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Agent sequence: requirement_analysis → design → feasibility → optional code review → security → scalability
    repo_configured = all(os.getenv(var) for var in ("GITHUB_TOKEN", "GITHUB_ORG", "GITHUB_REPO"))
    agents = [
        'requirement_analysis',
        'design_document_review',
        'design_feasibility_review',
    ]
    if repo_configured:
        agents.append('design_code_review')
    agents.extend([
        'design_security_review',
        'design_scalability_review'
    ])
    
    all_results = {
        'requirement_ticket_id': requirement_ticket_id,
        'design_ticket_id': design_ticket_id,
        'timestamp': datetime.now().isoformat(),
        'review_type': 'design_document_review',
        'results': {}
    }
    
    for agent_name in agents:
        print(f"\n{'='*80}")
        print(f"AGENT: {agent_name.upper()}")
        print(f"{'='*80}")
        
        try:
            runner = AgentRunner(agent_name)
            print(f"\n✓ {agent_name} runner initialized")
            
            # Use requirement ticket for requirement analysis, design ticket for others
            ticket_id = requirement_ticket_id if agent_name == 'requirement_analysis' else design_ticket_id
            
            # Review design document - call analyze method
            print(f"\n📋 Analyzing for ticket: {ticket_id}")
            
            # Call the analyze method
            if agent_name == 'requirement_analysis':
                result = runner.analyze_requirement(ticket_id)
            elif agent_name == 'design_feasibility_review':
                repository_context = runner.get_repository_context()
                design_content = runner.jira.format_ticket_for_review(design_ticket_id)
                result = runner.analyze_feasibility(design_content, source_name=design_ticket_id, repository_context=repository_context)
            elif agent_name == 'design_code_review':
                repository_context = runner.get_repository_context()
                if not repository_context:
                    raise RuntimeError("GitHub repository details are configured, but repository context could not be loaded.")

                design_content = runner.jira.format_ticket_for_review(design_ticket_id)
                result = runner.analyze_code_review(design_content, repository_context, source_name=design_ticket_id)
            else:
                # Pull the design ticket content from Jira and review the text directly
                design_content = runner.jira.format_ticket_for_review(design_ticket_id)

                if agent_name == 'design_document_review':
                    result = runner.analyze_architecture(design_content, source_name=design_ticket_id)
                elif agent_name == 'design_security_review':
                    result = runner.analyze_security(design_content, source_name=design_ticket_id)
                elif agent_name == 'design_scalability_review':
                    result = runner.analyze_scalability(design_content, source_name=design_ticket_id)
                else:
                    raise ValueError(f"Unsupported agent: {agent_name}")
            
            all_results['results'][agent_name] = result
            
            print(f"\n✓ {agent_name} analysis complete")
            if 'analysis' in result:
                print(f"Analysis Summary: {str(result['analysis'])[:200]}...")
            
        except Exception as e:
            error_msg = f"❌ Error running {agent_name}: {type(e).__name__}: {str(e)}"
            print(error_msg)
            all_results['results'][agent_name] = {
                'status': 'error',
                'error': str(e),
                'agent': agent_name
            }
    
    # Save results to file
    timestamp_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_base = f"review_results_{requirement_ticket_id}_vs_{design_ticket_id}_{timestamp_suffix}"
    output_json = f"{output_base}.json"
    output_md = f"{output_base}.md"
    output_txt = f"{output_base}.txt"

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, default=str, ensure_ascii=False)

    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(render_markdown_report(all_results))

    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(render_text_report(all_results))
    
    print(f"\n{'='*80}")
    print(f"REVIEW COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved to: {output_json}")
    print(f"Markdown report: {output_md}")
    print(f"Text report: {output_txt}\n")
    
    return all_results


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        requirement_ticket = sys.argv[1]
        design_ticket = sys.argv[2]
    elif len(sys.argv) == 2:
        # Single ticket - use for both
        requirement_ticket = sys.argv[1]
        design_ticket = sys.argv[1]
    else:
        # Default
        requirement_ticket = 'SK101-13'
        design_ticket = 'SK101-10'
    
    review_design_document(requirement_ticket, design_ticket)
