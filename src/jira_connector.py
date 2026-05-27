"""
Jira Connector

Provides integration with Jira REST API for extracting tickets and artifacts.
"""

import logging
import os
from typing import Dict, List, Any, Optional
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class JiraConnector:
    """
    Connector for Jira REST API v3
    
    Handles authentication, ticket extraction, artifact discovery, and project context.
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        username: Optional[str] = None,
        api_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize Jira connector
        
        Args:
            url: Jira URL (defaults to JIRA_URL env var)
            username: Jira username (defaults to JIRA_USERNAME env var)
            api_token: Jira API token (defaults to JIRA_API_TOKEN env var)
            timeout: Request timeout in seconds
        """
        self.url = url or os.getenv("JIRA_URL", "")
        self.username = username or os.getenv("JIRA_USERNAME", "")
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN", "")
        self.timeout = timeout
        
        # Use API v2 for issue access (v3 has limited endpoint support)
        self.api_endpoint = f"{self.url}/rest/api/2"
        self.auth = HTTPBasicAuth(self.username, self.api_token)
        
        logger.info(f"Initialized Jira connector for {self.url} (using API v2)")
    
    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """
        Get ticket details by ID
        
        Args:
            ticket_id: Jira ticket ID (e.g., "PROJ-123")
        
        Returns:
            Dictionary containing ticket details
        """
        logger.debug(f"Fetching ticket {ticket_id}")
        
        # Use singular /issue endpoint (not /issues)
        url = f"{self.api_endpoint}/issue/{ticket_id}"
        params = {
            "expand": "changelog,changes"
        }
        
        response = requests.get(
            url,
            auth=self.auth,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        ticket = response.json()
        logger.info(f"Retrieved ticket {ticket_id}: {ticket.get('fields', {}).get('summary', '')}")
        
        return ticket
    
    def get_linked_artifacts(self, ticket_id: str) -> List[Dict[str, Any]]:
        """
        Get artifacts linked to a ticket
        
        Args:
            ticket_id: Jira ticket ID
        
        Returns:
            List of linked artifacts
        """
        logger.debug(f"Fetching artifacts for {ticket_id}")
        
        ticket = self.get_ticket(ticket_id)
        artifacts = []
        
        # Get links
        if "issuelinks" in ticket.get("fields", {}):
            artifacts.extend(ticket["fields"]["issuelinks"])
        
        # Get attachments
        if "attachment" in ticket.get("fields", {}):
            artifacts.extend(ticket["fields"]["attachment"])
        
        logger.info(f"Found {len(artifacts)} artifacts for {ticket_id}")
        
        return artifacts

    def _stringify_field(self, value: Any) -> str:
        """Convert Jira field values into readable text."""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return str(value)
        if isinstance(value, list):
            parts = [self._stringify_field(item) for item in value]
            return "\n".join(part for part in parts if part)
        if isinstance(value, dict):
            if "content" in value and "type" in value:
                return self._stringify_field(value.get("content"))
            if "text" in value:
                return self._stringify_field(value.get("text"))
            if "name" in value:
                return self._stringify_field(value.get("name"))
            if "displayName" in value:
                return self._stringify_field(value.get("displayName"))
            if "value" in value:
                return self._stringify_field(value.get("value"))

            lines = []
            for key, item in value.items():
                rendered = self._stringify_field(item)
                if rendered:
                    lines.append(f"{key}: {rendered}")
            return "\n".join(lines)
        return str(value)

    def _safe_nested(self, value: Any, *keys: str, default: str = "") -> str:
        """Safely read nested dict keys without assuming the shape is present."""
        current = value
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key)
            if current is None:
                return default
        return self._stringify_field(current) or default

    def format_ticket_for_review(self, ticket_id: str) -> str:
        """
        Build a readable text representation of a Jira ticket for LLM review.

        This collects the ticket summary, description, status, assignee, and
        linked artifacts so review agents can work from Jira content directly.
        """
        ticket = self.get_ticket(ticket_id)
        fields = ticket.get("fields", {})
        linked_artifacts = self.get_linked_artifacts(ticket_id)

        sections = [
            f"Ticket: {ticket.get('key', ticket_id)}",
            f"Summary: {self._stringify_field(fields.get('summary', ''))}",
            f"Status: {self._safe_nested(fields.get('status'), 'name', default='')}",
            f"Assignee: {self._safe_nested(fields.get('assignee'), 'displayName', default='Unassigned')}",
            "",
            "Description:",
            self._stringify_field(fields.get('description', '')) or "Not provided",
        ]

        acceptance = self._stringify_field(fields.get("customfield_10043", ""))
        if acceptance:
            sections.extend(["", "Acceptance Criteria:", acceptance])

        if linked_artifacts:
            sections.extend(["", "Linked Artifacts:", self._stringify_field(linked_artifacts)])

        return "\n".join(sections).strip()
    
    def search(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for tickets using JQL
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
        
        Returns:
            List of matching tickets
        """
        logger.debug(f"Searching with JQL: {jql}")
        
        url = f"{self.api_endpoint}/search"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "expand": "changelog"
        }
        
        response = requests.get(
            url,
            auth=self.auth,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        results = response.json().get("issues", [])
        logger.info(f"Found {len(results)} tickets matching JQL")
        
        return results
    
    def get_project(self, project_key: str) -> Dict[str, Any]:
        """
        Get project details
        
        Args:
            project_key: Project key (e.g., "PROJ")
        
        Returns:
            Dictionary containing project details
        """
        logger.debug(f"Fetching project {project_key}")
        
        url = f"{self.api_endpoint}/projects/{project_key}"
        
        response = requests.get(
            url,
            auth=self.auth,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        project = response.json()
        logger.info(f"Retrieved project {project_key}: {project.get('name', '')}")
        
        return project
    
    def add_comment(self, ticket_id: str, comment: str) -> Dict[str, Any]:
        """
        Add a comment to a ticket
        
        Args:
            ticket_id: Jira ticket ID
            comment: Comment text
        
        Returns:
            Dictionary containing comment details
        """
        logger.debug(f"Adding comment to {ticket_id}")
        
        url = f"{self.api_endpoint}/issues/{ticket_id}/comments"
        data = {
            "body": {
                "version": 1,
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }
        
        response = requests.post(
            url,
            auth=self.auth,
            json=data,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        logger.info(f"Comment added to {ticket_id}")
        
        return response.json()
    
    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> None:
        """
        Update a ticket
        
        Args:
            ticket_id: Jira ticket ID
            updates: Dictionary of field updates
        """
        logger.debug(f"Updating ticket {ticket_id}")
        
        url = f"{self.api_endpoint}/issues/{ticket_id}"
        data = {
            "fields": updates
        }
        
        response = requests.put(
            url,
            auth=self.auth,
            json=data,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        logger.info(f"Ticket {ticket_id} updated successfully")


if __name__ == "__main__":
    # Example usage
    connector = JiraConnector()
    ticket = connector.get_ticket("DEMO-1")
    print(f"Retrieved ticket: {ticket['key']}")
