#!/usr/bin/env python3
"""
Agent Runner - Execute design review agents with different LLMs
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_factory import LLMFactory, get_default_llm
from jira_connector import JiraConnector


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
        
        # Create LLM instance - use provided provider or from config or default
        provider = llm_provider or self.agent_config.get('llm', {}).get('provider') or os.getenv("LLM_PROVIDER", "offline")
        self.llm = LLMFactory.create(provider)
        
        # Create Jira connector
        self.jira = JiraConnector()
        
        print(f"✓ Agent '{agent_name}' initialized")
        print(f"✓ Using LLM: {self.llm.get_model_name()}")
        print(f"✓ Agent Config: {self.agent_config.get('description', '')}")

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
        analysis_text = self.llm.generate(prompt, temperature=0.3, max_tokens=2000)
        
        # Try to parse as JSON, fallback to raw text
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            analysis = {'raw_analysis': analysis_text}
        
        result = {
            'agent': self.agent_name,
            'ticket_id': ticket_id,
            'ticket_summary': requirement['summary'],
            'analysis': analysis,
            'llm_model': self.llm.get_model_name(),
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
        
        analysis_text = self.llm.generate(prompt, temperature=0.3, max_tokens=2000)
        
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            analysis = {'raw_analysis': analysis_text}
        
        return {
            'agent': self.agent_name,
            'document': display_name,
            'source': resolved_source,
            'analysis': analysis,
            'llm_model': self.llm.get_model_name(),
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
        
        analysis_text = self.llm.generate(prompt, temperature=0.3, max_tokens=2000)
        
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            analysis = {'raw_analysis': analysis_text}
        
        return {
            'agent': self.agent_name,
            'analysis_type': 'security_review',
            'source': resolved_source,
            'analysis': analysis,
            'llm_model': self.llm.get_model_name(),
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

        analysis_text = self.llm.generate(prompt, temperature=0.3, max_tokens=2000)

        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            analysis = {'raw_analysis': analysis_text}

        return {
            'agent': self.agent_name,
            'analysis_type': 'scalability_review',
            'source': resolved_source,
            'analysis': analysis,
            'llm_model': self.llm.get_model_name(),
            'status': 'success'
        }
    
    def _build_requirement_prompt(self, requirement: Dict) -> str:
        """Build prompt for requirement analysis"""
        
        criteria_text = '\n'.join(f"- {c}" for c in requirement.get('acceptance_criteria', []))
        
        prompt = f"""You are a Requirements Analysis Expert. Analyze the following Jira requirement and provide structured feedback.

TICKET: {requirement['ticket_id']}
SUMMARY: {requirement['summary']}

DESCRIPTION:
{requirement['description']}

ACCEPTANCE CRITERIA:
{criteria_text if criteria_text else 'Not specified'}

STATUS: {requirement['status']}
ASSIGNEE: {requirement['assignee']}

Provide your analysis in the following JSON format:
{{
    "clarity_score": <1-10>,
    "completeness": "<complete|partial|incomplete>",
    "is_testable": <true|false>,
    "issues": [
        {{"issue": "description", "severity": "<critical|high|medium|low>"}}
    ],
    "recommendations": ["recommendation1", "recommendation2"],
    "missing_elements": ["element1", "element2"],
    "overall_assessment": "brief summary"
}}

Be specific and provide actionable feedback."""
        
        return prompt
    
    def _build_architecture_prompt(self, design_content: str) -> str:
        """Build prompt for architecture review"""
        
        # Limit content to avoid token limits
        limited_content = design_content[:3000]
        
        prompt = f"""You are a Software Architect. Review the following design document and provide detailed architectural analysis.

DESIGN DOCUMENT:
{limited_content}

Provide your analysis in the following JSON format:
{{
    "design_quality_score": <1-10>,
    "clarity_score": <1-10>,
    "architectural_patterns": ["pattern1", "pattern2"],
    "design_principles_followed": ["principle1"],
    "scalability_assessment": "<scalable|limited|concerns>",
    "maintainability_score": <1-10>,
    "risks": [
        {{"risk": "description", "severity": "<critical|high|medium|low>", "mitigation": "suggested mitigation"}}
    ],
    "improvements": ["improvement1", "improvement2"],
    "compliance_concerns": ["concern1"],
    "recommendations": ["recommendation1", "recommendation2"]
}}

Provide constructive and specific feedback."""
        
        return prompt
    
    def _build_security_prompt(self, design_content: str) -> str:
        """Build prompt for security review"""
        
        limited_content = design_content[:3000]
        
        prompt = f"""You are a Security Expert. Perform comprehensive security analysis of the following design.

DESIGN DOCUMENT:
{limited_content}

        Provide your security analysis in the following JSON format:
{{
    "security_score": <1-10>,
    "authentication": {{"status": "<secure|at_risk>", "details": "description"}},
    "authorization": {{"status": "<secure|at_risk>", "details": "description"}},
    "data_protection": {{"status": "<secure|at_risk>", "details": "description"}},
    "api_security": {{"status": "<secure|at_risk>", "details": "description"}},
    "vulnerabilities": [
        {{"vulnerability": "description", "severity": "<critical|high|medium|low>", "remediation": "how to fix"}}
    ],
    "compliance_gaps": ["gap1", "gap2"],
    "recommendations": ["recommendation1", "recommendation2"]
}}

Be thorough and specific about security concerns."""
        
        return prompt

    def _build_scalability_prompt(self, design_content: str) -> str:
        """Build prompt for scalability review"""

        limited_content = design_content[:3000]

        prompt = f"""You are a Scalability Expert. Analyze the following design for scalability and performance risks.

DESIGN DOCUMENT:
{limited_content}

Provide your scalability analysis in the following JSON format:
{{
    "scalability_score": <1-10>,
    "performance_assessment": {{
        "api_response_time": {{"requirement": "string", "design_support": "<good|adequate|needs_improvement>"}},
        "throughput": {{"requirement": "string", "design_support": "<good|adequate|needs_improvement>"}}
    }},
    "scalability_findings": [
        {{"finding_id": "SCALE-001", "aspect": "Database Layer", "severity": "<critical|high|medium|low>", "concern": "description", "recommendation": "how to improve"}}
    ],
    "capacity_considerations": ["consideration1", "consideration2"],
    "bottlenecks": ["bottleneck1", "bottleneck2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "summary": {{
        "overall_scalability_status": "<scalable_design|adequate_with_considerations|scalability_concerns>",
        "total_findings": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }}
}}

Focus on growth limits, performance risks, and operational scaling concerns."""

        return prompt


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
