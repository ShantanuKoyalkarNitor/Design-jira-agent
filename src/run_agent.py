#!/usr/bin/env python3
"""
Agent Runner - Execute design review agents with different LLMs
"""

import os
import sys
import json
import re
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_factory import LLMFactory, OfflineLLM, get_default_llm
from jira_connector import JiraConnector
from github_connector import GitHubConnector


logger = logging.getLogger(__name__)


class AgentRunner:
    """Runs design review agents"""
    
    def __init__(self, agent_name: str, llm_provider: str = None):
        """
        Initialize agent runner
        
        Args:
            agent_name: Name of agent (e.g., 'requirement_analysis')
            llm_provider: LLM provider to use (default from .env)
        """
        self.agent_name = agent_name
        self.agent_config = self._load_agent_config(agent_name)
        self.prompt_template = self._load_prompt_template(agent_name)
        
        # Create LLM instance - use provided provider or from config or default
        provider = llm_provider or self.agent_config.get('llm', {}).get('provider') or os.getenv("LLM_PROVIDER", "offline")
        # Use fallback mechanism - tries primary provider, then google, then offline
        self.llm = LLMFactory.create_with_fallback(provider)
        
        # Create Jira connector
        self.jira = JiraConnector()
        self.github = GitHubConnector()
        self._repository_context_cache: Optional[Dict[str, Any]] = None
        
        print(f"✓ Agent '{agent_name}' initialized")
        print(f"✓ Using LLM: {self.llm.get_model_name()}")
        print(f"✓ Agent Config: {self.agent_config.get('description', '')}")

    def has_repository_context(self) -> bool:
        """Return True when GitHub repository details are configured."""
        return self.github.is_configured()

    def get_repository_context(self) -> Optional[Dict[str, Any]]:
        """Fetch and cache representative repository code for review."""
        if self._repository_context_cache is not None:
            return self._repository_context_cache

        if not self.github.is_configured():
            return None

        try:
            self._repository_context_cache = self.github.build_repository_context()
        except Exception as exc:
            logger.warning("Unable to load GitHub repository context: %s", exc)
            self._repository_context_cache = None

        return self._repository_context_cache

    def _load_design_source(self, design_source: str) -> tuple[str, str]:
        """
        Resolve design input from either a file path or direct content.

        Returns:
            (design_content, source_label)
        """
        source_path = Path(design_source)
        if source_path.exists():
            return source_path.read_text(encoding="utf-8"), str(source_path)
        return design_source, "jira_content"
    
    def _load_agent_config(self, agent_name: str) -> dict:
        """Load agent YAML configuration"""
        config_path = Path(__file__).parent.parent / f"agents/{agent_name}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        
        with open(config_path, 'r') as f:
            content = f.read()
            # Extract YAML frontmatter (between first and second ---)
            if content.startswith('---'):
                parts = content.split('---')
                if len(parts) >= 2:
                    yaml_content = parts[1].strip()
                else:
                    yaml_content = content
            else:
                yaml_content = content
            
            config = yaml.safe_load(yaml_content) or {}
            return config

    def _load_prompt_template(self, agent_name: str) -> str:
        """Load the markdown prompt template for an agent."""
        prompt_map = {
            'requirement_analysis': 'requirement_analysis.md',
            'design_document_review': 'design_document_review.md',
            'design_feasibility_review': 'design_feasibility_review.md',
            'design_code_review': 'design_code_review.md',
            'design_security_review': 'design_security_review.md',
            'design_scalability_review': 'design_scalability_review.md',
        }

        prompt_file = prompt_map.get(agent_name)
        if not prompt_file:
            return ""

        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
        if not prompt_path.exists():
            return ""

        return prompt_path.read_text(encoding="utf-8").strip()

    def _compose_prompt(self, context_title: str, context_body: str) -> str:
        """Combine the markdown prompt template with live Jira content."""
        sections = []
        if self.prompt_template:
            sections.append(self.prompt_template)
        sections.extend([
            "",
            f"## {context_title}",
            context_body.strip(),
            "",
            "Important: Return valid JSON only.",
            "Do not add markdown fences, code blocks, commentary, or surrounding text.",
            "Use nested objects and arrays when needed.",
        ])
        return "\n".join(sections).strip()

    def _parse_llm_json(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse JSON returned by the LLM.

        The model sometimes wraps valid JSON in markdown fences or adds
        surrounding commentary, so we try a few safe extraction strategies
        before falling back to raw text.
        """
        text = analysis_text.strip()

        # Try the response as-is first.
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # If the response is fenced markdown, try the fenced payload.
        fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if fenced_match:
            fenced_text = fenced_match.group(1).strip()
            try:
                return json.loads(fenced_text)
            except json.JSONDecodeError:
                text = fenced_text

        table_data = self._parse_markdown_table(text)
        if table_data:
            return table_data

        # As a last structured attempt, extract the outermost JSON object.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        return {"raw_analysis": analysis_text}

    def _parse_markdown_table(self, text: str) -> Dict[str, Any]:
        """
        Parse a markdown table into a dictionary.

        Expected shape:
            | field | value |
            | --- | --- |
            | key | plain text or JSON |
        """
        lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
        if len(lines) < 2:
            return {}

        def split_row(row: str) -> list[str]:
            parts = [cell.strip() for cell in row.strip("|").split("|")]
            return parts

        header = [cell.lower() for cell in split_row(lines[0])]
        if len(header) < 2 or "field" not in header[0] or "value" not in header[1]:
            return {}

        rows = lines[2:] if len(lines) > 2 and set(split_row(lines[1])) <= {"---", ":---", "---:", ":---:"} else lines[1:]
        parsed: Dict[str, Any] = {}

        for row in rows:
            cells = split_row(row)
            if len(cells) < 2:
                continue

            key = cells[0]
            value = "|".join(cells[1:]).strip()
            if not key:
                continue

            parsed[key] = self._coerce_table_value(value)

        return parsed

    def _coerce_table_value(self, value: str) -> Any:
        """Try to decode a table cell as JSON, otherwise keep it as text."""
        value = value.strip()
        if not value:
            return ""

        if value.startswith("{") or value.startswith("[") or value in {"true", "false", "null"}:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass

        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def _generate_structured_analysis(self, prompt: str, *, max_tokens: int = 2000) -> tuple[Dict[str, Any], str, bool, str, Dict[str, Any]]:
        """
        Generate analysis and guarantee structured JSON output.

        If the primary LLM returns incomplete JSON, fall back to the local
        deterministic reviewer instead of saving raw truncated text.

        Returns:
            (analysis, model_name, used_fallback, raw_live_response, parsed_response)
        """
        primary_model = self.llm.get_model_name()
        analysis_text = self.llm.generate(prompt, temperature=0.3, max_tokens=max_tokens)
        parsed_live_response = self._parse_llm_json(analysis_text)

        if isinstance(parsed_live_response, dict) and "raw_analysis" not in parsed_live_response:
            return parsed_live_response, primary_model, False, analysis_text, parsed_live_response

        logger.warning(
            f"Primary LLM {primary_model} returned incomplete JSON for {self.agent_name}; "
            "falling back to offline reviewer."
        )
        fallback_llm = OfflineLLM()
        fallback_text = fallback_llm.generate(prompt, temperature=0.0, max_tokens=max_tokens)
        fallback_analysis = self._parse_llm_json(fallback_text)

        if isinstance(fallback_analysis, dict) and "raw_analysis" not in fallback_analysis:
            return fallback_analysis, fallback_llm.get_model_name(), True, analysis_text, fallback_analysis

        return parsed_live_response, primary_model, False, analysis_text, parsed_live_response
    
    def get_requirements(self, ticket_id: str) -> Dict[str, Any]:
        """
        Extract requirements from Jira ticket
        
        Args:
            ticket_id: Jira ticket ID (e.g., 'PROJ-123')
        
        Returns:
            Dictionary with requirement details
        """
        ticket = self.jira.get_ticket(ticket_id)
        fields = ticket['fields']
        
        # Extract acceptance criteria from custom field or description
        acceptance_criteria = []
        
        # Try custom field first
        if 'customfield_10043' in fields:  # Common acceptance criteria field
            criteria_text = fields['customfield_10043'] or ''
            acceptance_criteria = [
                line.strip('- []* ') 
                for line in criteria_text.split('\n') 
                if line.strip() and not line.startswith('#')
            ]
        
        # Get linked artifacts
        artifacts = self.jira.get_linked_artifacts(ticket_id)
        
        return {
            'ticket_id': ticket_id,
            'summary': fields.get('summary', ''),
            'description': fields.get('description', ''),
            'acceptance_criteria': acceptance_criteria,
            'epic': fields.get('customfield_10000', {}).get('name', '') if fields.get('customfield_10000') else '',
            'status': fields.get('status', {}).get('name', ''),
            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
            'linked_documents': artifacts
        }
    
    def analyze_requirement(self, ticket_id: str) -> Dict[str, Any]:
        """
        Analyze single requirement from Jira ticket
        
        Args:
            ticket_id: Jira ticket ID (e.g., 'PROJ-123')
        
        Returns:
            Analysis result with findings
        """
        print(f"\n📋 Analyzing requirement: {ticket_id}")
        
        # Get requirement details
        requirement = self.get_requirements(ticket_id)
        
        # Build prompt for LLM
        prompt = self._build_requirement_prompt(requirement)
        
        print(f"📤 Sending to LLM: {self.llm.get_model_name()}")
        
        # Call LLM with lower temperature for more deterministic output
        analysis, llm_model, used_fallback, raw_live_response, parsed_response = self._generate_structured_analysis(prompt)
        
        result = {
            'agent': self.agent_name,
            'ticket_id': ticket_id,
            'ticket_summary': requirement['summary'],
            'analysis': analysis,
            'raw_live_response': raw_live_response,
            'parsed_response': parsed_response,
            'llm_model': llm_model,
            'fallback_used': used_fallback,
            'status': 'success'
        }
        
        print(f"✓ Analysis complete")
        return result
    
    def analyze_architecture(self, design_source: str, source_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze architecture from design document
        
        Args:
            design_doc_path: Path to design document
        
        Returns:
            Architecture analysis result
        """
        display_name = source_name or design_source
        print(f"\n🏗️  Analyzing architecture: {display_name}")

        design_content, resolved_source = self._load_design_source(design_source)
        
        prompt = self._build_architecture_prompt(design_content)
        
        print(f"📤 Sending to LLM: {self.llm.get_model_name()}")
        
        analysis, llm_model, used_fallback, raw_live_response, parsed_response = self._generate_structured_analysis(prompt)
        
        return {
            'agent': self.agent_name,
            'document': display_name,
            'source': resolved_source,
            'analysis': analysis,
            'raw_live_response': raw_live_response,
            'parsed_response': parsed_response,
            'llm_model': llm_model,
            'fallback_used': used_fallback,
            'status': 'success'
        }

    def analyze_security(self, design_source: str, source_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze security aspects of design
        
        Args:
            design_content: Design document content
        
        Returns:
            Security analysis result
        """
        display_name = source_name or design_source
        print(f"\n🔒 Analyzing security aspects: {display_name}")

        design_content, resolved_source = self._load_design_source(design_source)

        prompt = self._build_security_prompt(design_content)
        
        print(f"📤 Sending to LLM: {self.llm.get_model_name()}")
        
        analysis, llm_model, used_fallback, raw_live_response, parsed_response = self._generate_structured_analysis(prompt)
        
        return {
            'agent': self.agent_name,
            'analysis_type': 'security_review',
            'source': resolved_source,
            'analysis': analysis,
            'raw_live_response': raw_live_response,
            'parsed_response': parsed_response,
            'llm_model': llm_model,
            'fallback_used': used_fallback,
            'status': 'success'
        }

    def analyze_scalability(self, design_source: str, source_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze scalability and performance aspects of design.

        Args:
            design_source: Either a design document path or direct content
            source_name: Friendly label for the source

        Returns:
            Scalability analysis result
        """
        display_name = source_name or design_source
        print(f"\n📈 Analyzing scalability aspects: {display_name}")

        design_content, resolved_source = self._load_design_source(design_source)

        prompt = self._build_scalability_prompt(design_content)

        print(f"📤 Sending to LLM: {self.llm.get_model_name()}")

        analysis, llm_model, used_fallback, raw_live_response, parsed_response = self._generate_structured_analysis(prompt)

        return {
            'agent': self.agent_name,
            'analysis_type': 'scalability_review',
            'source': resolved_source,
            'analysis': analysis,
            'raw_live_response': raw_live_response,
            'parsed_response': parsed_response,
            'llm_model': llm_model,
            'fallback_used': used_fallback,
            'status': 'success'
        }
    
    def _build_requirement_prompt(self, requirement: Dict) -> str:
        """Build prompt for requirement analysis"""
        
        criteria_text = '\n'.join(f"- {c}" for c in requirement.get('acceptance_criteria', []))

        context = f"""TICKET: {requirement['ticket_id']}
SUMMARY: {requirement['summary']}

DESCRIPTION:
{requirement['description'] or 'Not provided'}

ACCEPTANCE CRITERIA:
{criteria_text if criteria_text else 'Not specified'}

STATUS: {requirement['status']}
ASSIGNEE: {requirement['assignee']}
"""

        return self._compose_prompt("Jira Ticket Input", context)
    
    def _build_architecture_prompt(self, design_content: str) -> str:
        """Build prompt for architecture review"""
        
        # Limit content to avoid token limits
        limited_content = design_content[:3000]

        context = f"""DESIGN CONTENT:
{limited_content}
"""

        return self._compose_prompt("Jira Design Input", context)
    
    def _build_security_prompt(self, design_content: str) -> str:
        """Build prompt for security review"""
        
        limited_content = design_content[:3000]

        context = f"""DESIGN CONTENT:
{limited_content}
"""

        return self._compose_prompt("Jira Design Input", context)

    def _build_scalability_prompt(self, design_content: str) -> str:
        """Build prompt for scalability review"""

        limited_content = design_content[:3000]

        context = f"""DESIGN CONTENT:
{limited_content}
"""

        return self._compose_prompt("Jira Design Input", context)

    def _build_feasibility_prompt(self, design_content: str, repository_context: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for implementation feasibility review."""
        limited_content = design_content[:3000]

        repo_sections = []
        if repository_context:
            repo_summary = {
                key: value
                for key, value in repository_context.items()
                if key != "context_text"
            }
            repo_context_text = repository_context.get("context_text", "")[:12000]
            repo_summary_json = json.dumps(repo_summary, indent=2, ensure_ascii=False)
            repo_sections = [
                "",
                f"REPOSITORY:",
                repository_context.get("repository", "unknown"),
                "",
                f"BRANCH:",
                repository_context.get("branch", "unknown"),
                "",
                "REPOSITORY SUMMARY:",
                repo_summary_json,
                "",
                "REPOSITORY CODE:",
                repo_context_text,
            ]

        context = "\n".join([
            "DESIGN CONTENT:",
            limited_content,
            *repo_sections,
        ])

        prompt = self._compose_prompt("Jira Design Feasibility Input", context)
        prompt += (
            "\n\nDecide whether the approach is implementable, what changes are required, "
            "what is blocking, and what should happen first."
        )
        return prompt

    def _build_code_review_prompt(self, design_content: str, repository_context: Dict[str, Any]) -> str:
        """Build prompt for code-aware design review."""
        limited_design_content = design_content[:3000]
        repo_summary = {
            key: value
            for key, value in repository_context.items()
            if key != "context_text"
        }
        repo_context_text = repository_context.get("context_text", "")[:12000]
        repo_summary_json = json.dumps(repo_summary, indent=2, ensure_ascii=False)
        repository_name = repository_context.get("repository", "unknown")
        branch_name = repository_context.get("branch", "unknown")

        context = f"""DESIGN CONTENT:
{limited_design_content}

REPOSITORY:
{repository_name}

BRANCH:
{branch_name}

REPOSITORY SUMMARY:
{repo_summary_json}

REPOSITORY CODE:
{repo_context_text}
"""

        prompt = self._compose_prompt("Jira Design and Repository Input", context)
        prompt += (
            "\n\nFocus on whether the current codebase matches the design, what is already implemented, "
            "what is missing, and where the code contradicts the design."
        )
        return prompt

    def analyze_feasibility(
        self,
        design_source: str,
        source_name: Optional[str] = None,
        repository_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Analyze whether the design approach is implementable."""
        display_name = source_name or design_source
        print(f"\n🧪 Analyzing implementation feasibility: {display_name}")

        design_content, resolved_source = self._load_design_source(design_source)
        prompt = self._build_feasibility_prompt(design_content, repository_context)

        print(f"📤 Sending to LLM: {self.llm.get_model_name()}")

        analysis, llm_model, used_fallback, raw_live_response, parsed_response = self._generate_structured_analysis(prompt)

        result = {
            'agent': self.agent_name,
            'analysis_type': 'feasibility_review',
            'source': resolved_source,
            'analysis': analysis,
            'raw_live_response': raw_live_response,
            'parsed_response': parsed_response,
            'llm_model': llm_model,
            'fallback_used': used_fallback,
            'status': 'success'
        }

        if repository_context:
            result['repository_context'] = {
                'repository': repository_context.get('repository', ''),
                'branch': repository_context.get('branch', ''),
                'file_count': repository_context.get('file_count', 0),
                'files_reviewed': repository_context.get('files_reviewed', []),
            }

        return result

    def analyze_code_review(
        self,
        design_source: str,
        repository_context: Dict[str, Any],
        source_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze the design from a codebase perspective."""
        display_name = source_name or design_source
        print(f"\n🧩 Analyzing code perspective: {display_name}")

        design_content, resolved_source = self._load_design_source(design_source)
        prompt = self._build_code_review_prompt(design_content, repository_context)

        print(f"📤 Sending to LLM: {self.llm.get_model_name()}")

        analysis, llm_model, used_fallback, raw_live_response, parsed_response = self._generate_structured_analysis(prompt)

        return {
            'agent': self.agent_name,
            'analysis_type': 'code_review',
            'source': resolved_source,
            'repository_context': {
                'repository': repository_context.get('repository', ''),
                'branch': repository_context.get('branch', ''),
                'file_count': repository_context.get('file_count', 0),
                'files_reviewed': repository_context.get('files_reviewed', []),
            },
            'analysis': analysis,
            'raw_live_response': raw_live_response,
            'parsed_response': parsed_response,
            'llm_model': llm_model,
            'fallback_used': used_fallback,
            'status': 'success'
        }


def main():
    """Main execution"""
    
    print("\n" + "=" * 70)
    print("DESIGN REVIEW AGENT - MULTI-LLM RUNNER")
    print("=" * 70)
    
    # Example 1: Requirement Analysis with default LLM
    print("\n[1] REQUIREMENT ANALYSIS - Using default LLM from .env")
    print("-" * 70)
    
    try:
        runner = AgentRunner('requirement_analysis')
        
        # Replace with your actual ticket ID
        # result = runner.analyze_requirement('PROJ-123')
        # print(f"\n✓ Result:\n{json.dumps(result, indent=2)}")
        
        print("Note: Update ticket_id in code to test with real Jira ticket")
        
    except Exception as e:
        print(f"⚠️  Requirement Analysis Demo: {type(e).__name__}")
        print(f"   To test: Set JIRA credentials and ticket ID")
    
    # Example 2: Architecture Review
    print("\n[2] ARCHITECTURE REVIEW - Analyzing design document")
    print("-" * 70)
    
    try:
        runner = AgentRunner('architecture_review')
        
        if Path('DESIGN.md').exists():
            result = runner.analyze_architecture('DESIGN.md')
            print(f"\n✓ Architecture Analysis Result:")
            print(json.dumps(result, indent=2))
        else:
            print("Design document 'DESIGN.md' not found")
    
    except Exception as e:
        print(f"⚠️  Architecture Review: {type(e).__name__}")
    
    # Example 3: Switch LLM provider
    print("\n[3] SWITCHING LLM PROVIDER - Using Anthropic Claude")
    print("-" * 70)
    
    try:
        # Make sure anthropic package is installed
        runner_claude = AgentRunner('requirement_analysis', llm_provider='anthropic')
        print("✓ Successfully switched to Anthropic Claude")
        print("  (Would analyze with Claude 3 Opus)")
    
    except Exception as e:
        print(f"⚠️  Anthropic Provider: {type(e).__name__}")
        print("   Install: pip install anthropic")
    
    # Example 4: Available LLMs
    print("\n[4] AVAILABLE LLM PROVIDERS")
    print("-" * 70)
    print("Supported LLMs:")
    for provider in ['openai', 'azure', 'anthropic', 'google', 'ollama', 'mistral']:
        print(f"  • {provider}")
    
    print("\n" + "=" * 70)
    print("QUICK START:")
    print("=" * 70)
    print("1. Edit .env with your LLM credentials")
    print("2. Uncomment and set JIRA ticket ID to test requirement analysis")
    print("3. Run: python src/run_agent.py")
    print("4. Or use Copilot Chat: Ctrl+Shift+I then @agents Analyze...")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
