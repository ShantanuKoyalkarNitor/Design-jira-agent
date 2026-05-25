<!-- GitHub Copilot Custom Instructions for Design Review Agent -->

## AI-Driven Design Review Agent Workspace

This workspace contains a GitHub Copilot-based design review agent for automating design document reviews against Jira requirements.

### Project Overview
- **Purpose**: Automated design review using AI agents, prompts, and skills
- **Core Framework**: GitHub Copilot with custom agents and prompts
- **Target Users**: Software architects, design reviewers, project teams
- **Key Features**: Requirement extraction, design validation, risk classification, report generation

### Workspace Guidelines for Copilot

#### Code Style & Conventions
- Use clear, descriptive naming for agents, prompts, and skills
- Structure all prompts with explicit role definition and context
- Include severity levels in risk classifications (Critical, High, Medium, Low)
- Use markdown for all documentation and reports

#### Agent Development
- Each agent should have a specific responsibility (Requirement Analysis, Architecture Review, Security Review)
- Agents should include input/output specifications
- Agents should define success criteria clearly

#### Prompt Structure
- Begin with role definition (e.g., "You are a Design Review Expert")
- Provide context about the design review process
- Include specific checklists or criteria
- Ask for structured output (JSON or markdown)

#### Skills Organization
- Create reusable skills for common operations
- Each skill should be documented with input/output specifications
- Include example usage in skill documentation

### File Organization
- `docs/` - Detailed documentation and guides
- `agents/` - Agent definitions and configurations
- `prompts/` - Prompt templates for various review scenarios
- `skills/` - Reusable skill definitions
- `src/` - Implementation code and utilities
- `templates/` - Report and output templates
- `config/` - Configuration files for APIs and integrations

### Key Commands
- Review design documents: Use Design Review Agent
- Extract requirements: Use Requirement Analysis Agent
- Assess security: Use Security Review Agent
- Generate reports: Use Report Generator

### Integration Points
- Jira REST API for ticket extraction
- Confluence REST API for documentation
- Git for version control
- Markdown for all outputs

### Best Practices
1. Always validate extracted requirements with stakeholders
2. Cross-reference artifacts with Jira tickets
3. Classify findings by severity and impact
4. Generate audit-ready documentation
5. Include recommendations with each finding
6. Track review history and changes

---

## Project Deliverables

### ✅ Complete Design Specification
- Comprehensive DESIGN.md with 15 detailed sections
- Multi-agent architecture specification
- Data flow and component descriptions
- Success metrics and roadmap

### ✅ Four Specialized AI Agents
1. **Requirement Analysis Agent**: Validates requirements completeness
2. **Architecture Review Agent**: Assesses design against best practices
3. **Security & Compliance Agent**: Identifies vulnerabilities and gaps
4. **Scalability Assessment Agent**: Evaluates performance and growth

### ✅ Detailed Agent Prompts
- Structured prompts for each agent
- Classification frameworks
- Output JSON specifications
- Assessment criteria and best practices

### ✅ Reusable Skills
1. **Jira Integration Skill**: Ticket and artifact extraction
2. **Artifact Discovery Skill**: Document parsing and retrieval
3. **Report Generation Skill**: Structured report formatting
4. **Risk Classification Skill**: Finding prioritization

### ✅ Configuration Framework
- API configuration (Jira, Confluence, OpenAI)
- Review configuration (rules, criteria, approvals)
- Environment template (.env.example)
- Logging and performance settings

### ✅ Professional Documentation
1. **DESIGN.md**: Complete 15-section specification
2. **README.md**: Project overview and usage
3. **ARCHITECTURE.md**: System design and patterns
4. **QUICKSTART.md**: 5-minute setup guide
5. **WORKFLOW.md**: End-to-end process documentation
6. **PROJECT_SUMMARY.md**: Complete project overview

### ✅ Implementation Framework
- Python base classes and structure
- Jira REST API connector
- Report templates and examples
- Dependencies and environment setup

### ✅ Ready for Development
All components documented and ready for implementation. See PROJECT_SUMMARY.md for complete inventory.

---

**Status**: Complete - Ready for Implementation
**Last Updated**: May 24, 2026
**Next Phase**: Development and Integration
**Estimated Implementation Time**: 6-8 weeks
