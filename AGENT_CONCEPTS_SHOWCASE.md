# Agent Concepts Showcase

This file explains the main ideas behind the current Jira design review agent in simple terms.

## What The Agent Does

The agent reviews Jira content and turns it into a structured review.

It produces:

- Requirement analysis
- Design review
- Security review
- Scalability review
- JSON, Markdown, and text reports

## Main Flow

1. Read the requirement ticket
2. Read the design ticket
3. Send the ticket content to the right agent
4. Parse the model output
5. Save the final reports

## The Four Agents

### `requirement_analysis`

This agent pulls out the main requirements from the Jira ticket. It helps the rest of the review know what the design is supposed to satisfy.

### `design_document_review`

This agent checks whether the design matches the requirements and whether the design looks complete and sensible.

### `design_security_review`

This agent looks for security risks such as weak access control, missing validation, and unsafe data handling.

### `design_scalability_review`

This agent looks for bottlenecks, scaling risks, and performance problems.

## Important Parts Of The Code

### `run_all_agents.py`

This is the main command you run from the terminal. It coordinates all four agents and writes the output files.

### `src/run_agent.py`

This file loads each agent, builds the prompt, calls the LLM, and tries to recover if the model output is messy.

### `src/jira_connector.py`

This file reads Jira tickets and turns them into plain text that the agents can review.

### `src/llm_factory.py`

This file chooses the LLM provider. It supports:

- OpenAI
- Azure OpenAI
- Anthropic
- Google Gemini
- Ollama
- Mistral
- Offline fallback

## Why The Offline Fallback Exists

Sometimes the live model returns incomplete or broken output. The offline fallback keeps the review usable instead of failing completely.

That is helpful when:

- The model quota is exhausted
- The API is slow or unavailable
- You want a stable result for testing

## What The Reports Look Like

Each run saves three files:

- JSON for automation
- Markdown for reading
- Plain text for quick viewing

## Files Worth Reading

- `README.md`
- `run_all_agents.py`
- `src/run_agent.py`
- `src/jira_connector.py`
- `src/llm_factory.py`
- `agents/requirement_analysis.yaml`
- `agents/design_document_review.yaml`
- `agents/design_security_review.yaml`
- `agents/design_scalability_review.yaml`
- `prompts/requirement_analysis.md`
- `prompts/design_document_review.md`
- `prompts/design_security_review.md`
- `prompts/design_scalability_review.md`

## Short Summary

This project is a Jira-based review system with separate agents for requirements, design quality, security, and scalability. It is built to keep working even when the live model is unreliable.
