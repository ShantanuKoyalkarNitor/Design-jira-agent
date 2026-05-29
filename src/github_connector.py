"""
GitHub Connector

Fetches repository metadata and representative source files for optional
code-aware design review.
"""

from __future__ import annotations

import base64
import logging
import os
from typing import Any, Dict, List, Optional

import requests


logger = logging.getLogger(__name__)


class GitHubConnector:
    """Small GitHub REST API helper for repository inspection."""

    CODE_EXTENSIONS = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".go",
        ".rb",
        ".cs",
        ".php",
        ".kt",
        ".swift",
        ".rs",
        ".yaml",
        ".yml",
        ".toml",
        ".json",
        ".ini",
        ".cfg",
    }

    CONTEXT_KEYWORDS = (
        "src/",
        "app/",
        "lib/",
        "service",
        "controller",
        "handler",
        "route",
        "api",
        "model",
        "test",
        "spec",
        "config",
        "worker",
        "main",
        "server",
    )

    def __init__(
        self,
        token: Optional[str] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        branch: Optional[str] = None,
        base_url: str = "https://api.github.com",
        timeout: int = 30,
    ) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.owner = owner or os.getenv("GITHUB_ORG", "")
        self.repo = repo or os.getenv("GITHUB_REPO", "")
        self.branch = branch or os.getenv("GITHUB_BRANCH", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._repo_cache: Optional[Dict[str, Any]] = None

    def is_configured(self) -> bool:
        """Return True when enough repo details are available."""
        return bool(self.token and self.owner and self.repo)

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        response = requests.get(
            url,
            headers=self._headers(),
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_repo_metadata(self) -> Dict[str, Any]:
        """Fetch repository metadata once and cache it."""
        if self._repo_cache is not None:
            return self._repo_cache

        if not self.is_configured():
            raise ValueError("GitHub repository details are not configured")

        self._repo_cache = self._request(f"/repos/{self.owner}/{self.repo}")
        return self._repo_cache

    def get_default_branch(self) -> str:
        """Resolve the branch to inspect."""
        if self.branch:
            return self.branch
        metadata = self.get_repo_metadata()
        return metadata.get("default_branch", "main")

    def list_repository_files(self, ref: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in the repository tree for the selected branch."""
        branch = ref or self.get_default_branch()
        tree = self._request(
            f"/repos/{self.owner}/{self.repo}/git/trees/{branch}",
            params={"recursive": "1"},
        )
        entries = tree.get("tree", []) if isinstance(tree, dict) else []
        files = [item for item in entries if item.get("type") == "blob"]
        logger.info("GitHub repository %s/%s returned %d files", self.owner, self.repo, len(files))
        return files

    def _score_path(self, path: str) -> int:
        score = 0
        lower_path = path.lower()
        for keyword in self.CONTEXT_KEYWORDS:
            if keyword in lower_path:
                score += 3
        if any(lower_path.endswith(ext) for ext in self.CODE_EXTENSIONS):
            score += 2
        if lower_path.endswith(("test.py", "spec.py", "test.ts", "spec.ts")):
            score += 2
        if lower_path.count("/") <= 2:
            score += 1
        return score

    def _is_relevant_file(self, path: str) -> bool:
        lower_path = path.lower()
        return any(lower_path.endswith(ext) for ext in self.CODE_EXTENSIONS)

    def get_file_content(self, path: str, ref: Optional[str] = None, max_chars: int = 2000) -> str:
        """Fetch and decode a single file from the repository."""
        branch = ref or self.get_default_branch()
        payload = self._request(
            f"/repos/{self.owner}/{self.repo}/contents/{path}",
            params={"ref": branch},
        )

        if isinstance(payload, list):
            return ""

        content = payload.get("content", "")
        encoding = payload.get("encoding", "")
        size = payload.get("size", 0)

        if not content:
            download_url = payload.get("download_url")
            if not download_url:
                return ""
            raw_response = requests.get(download_url, headers=self._headers(), timeout=self.timeout)
            raw_response.raise_for_status()
            text = raw_response.text
            return text[:max_chars]

        if encoding == "base64":
            decoded = base64.b64decode(content).decode("utf-8", errors="replace")
        else:
            decoded = content

        if size and size > max_chars:
            return decoded[:max_chars] + "\n... [truncated]"
        return decoded[:max_chars]

    def build_repository_context(
        self,
        *,
        max_files: int = 8,
        max_chars_per_file: int = 2000,
        max_total_chars: int = 12000,
    ) -> Dict[str, Any]:
        """Build a compact text bundle of representative code files."""
        if not self.is_configured():
            return {}

        metadata = self.get_repo_metadata()
        branch = self.get_default_branch()
        files = self.list_repository_files(branch)

        relevant_files = [item for item in files if self._is_relevant_file(item.get("path", ""))]
        relevant_files.sort(
            key=lambda item: (
                -self._score_path(item.get("path", "")),
                len(item.get("path", "")),
            )
        )

        selected: List[Dict[str, Any]] = []
        seen_paths = set()
        for item in relevant_files:
            path = item.get("path", "")
            if not path or path in seen_paths:
                continue
            selected.append(
                {
                    "path": path,
                    "size": item.get("size", 0),
                    "type": item.get("type", ""),
                }
            )
            seen_paths.add(path)
            if len(selected) >= max_files:
                break

        rendered_sections: List[str] = []
        total_chars = 0
        files_reviewed: List[Dict[str, Any]] = []
        for item in selected:
            path = item["path"]
            try:
                content = self.get_file_content(path, branch, max_chars=max_chars_per_file)
            except Exception as exc:
                logger.warning("Failed to fetch GitHub file %s: %s", path, exc)
                continue

            if not content.strip():
                continue

            section = f"FILE: {path}\n{content.strip()}\n"
            if total_chars + len(section) > max_total_chars:
                break

            rendered_sections.append(section)
            total_chars += len(section)
            files_reviewed.append(
                {
                    "path": path,
                    "size": item.get("size", 0),
                }
            )

        repo_full_name = metadata.get("full_name", f"{self.owner}/{self.repo}")
        context_text = "\n".join(
            [
                f"Repository: {repo_full_name}",
                f"Default branch: {branch}",
                f"Files reviewed: {len(files_reviewed)}",
                "",
                *rendered_sections,
            ]
        ).strip()

        return {
            "repository": repo_full_name,
            "owner": self.owner,
            "repo": self.repo,
            "branch": branch,
            "html_url": metadata.get("html_url", ""),
            "files_reviewed": files_reviewed,
            "file_count": len(files_reviewed),
            "context_text": context_text,
        }
