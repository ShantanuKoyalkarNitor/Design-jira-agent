"""
LLM Factory - Multi-LLM Support

Provides factory pattern to instantiate different LLM providers dynamically.
Supports: OpenAI, Azure OpenAI, Anthropic, Google Gemini, Ollama, Mistral
"""

import os
import logging
import json
import re
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name"""
        pass


class OfflineLLM(BaseLLM):
    """Deterministic offline fallback for local execution without network access."""

    def __init__(self, model: str = "offline-heuristic", **config):
        self.model = model
        self.temperature = config.get("temperature", 0.0)
        self.max_tokens = config.get("max_tokens", 4096)
        logger.info(f"Initialized offline LLM with model: {self.model}")

    def _extract(self, prompt: str, label: str) -> str:
        match = re.search(rf"{re.escape(label)}:\s*(.*)", prompt)
        return match.group(1).strip() if match else ""

    def _json(self, payload: Dict[str, Any]) -> str:
        return json.dumps(payload, indent=2)

    def generate(self, prompt: str, **kwargs) -> str:
        prompt_lower = prompt.lower()

        if "requirements analysis expert" in prompt_lower or "analyze the following jira requirement" in prompt_lower:
            ticket_id = self._extract(prompt, "TICKET") or "UNKNOWN"
            summary = self._extract(prompt, "SUMMARY")
            return self._json({
                "clarity_score": 5,
                "completeness": "partial",
                "is_testable": False,
                "issues": [
                    {
                        "issue": "Offline mode used; live model analysis was not available in this environment.",
                        "severity": "medium",
                    }
                ],
                "recommendations": [
                    "Re-run with a live LLM provider once network access is available.",
                    "Validate acceptance criteria are explicit and testable.",
                ],
                "missing_elements": [
                    "Live model analysis",
                    "Clear, testable acceptance criteria",
                ],
                "overall_assessment": f"Offline fallback generated for {ticket_id or 'the ticket'}; summary: {summary or 'not provided'}.",
            })

        if "software architect" in prompt_lower:
            return self._json({
                "design_quality_score": 5,
                "clarity_score": 5,
                "architectural_patterns": [],
                "design_principles_followed": [],
                "scalability_assessment": "concerns",
                "maintainability_score": 5,
                "risks": [
                    {
                        "risk": "Offline mode used; live design review unavailable.",
                        "severity": "medium",
                        "mitigation": "Run with a live LLM provider for a full review.",
                    }
                ],
                "improvements": [
                    "Confirm design content is complete in Jira before review.",
                    "Add explicit implementation boundaries and interfaces.",
                ],
                "compliance_concerns": [],
                "recommendations": [
                    "Re-run with live model access for deeper architectural analysis."
                ],
            })

        if "security expert" in prompt_lower:
            return self._json({
                "security_score": 5,
                "authentication": {"status": "at_risk", "details": "Offline mode used; no live security review."},
                "authorization": {"status": "at_risk", "details": "Offline mode used; no live security review."},
                "data_protection": {"status": "at_risk", "details": "Offline mode used; no live security review."},
                "api_security": {"status": "at_risk", "details": "Offline mode used; no live security review."},
                "vulnerabilities": [
                    {
                        "vulnerability": "Review was generated offline without live model access.",
                        "severity": "medium",
                        "remediation": "Run the review against a live model and validate security controls.",
                    }
                ],
                "compliance_gaps": [],
                "recommendations": [
                    "Re-run the security review with a live provider.",
                    "Ensure authentication, authorization, and data protection are explicitly documented.",
                ],
            })

        if "scalability expert" in prompt_lower:
            return self._json({
                "scalability_score": 5,
                "performance_assessment": {
                    "api_response_time": {
                        "requirement": "not assessed offline",
                        "design_support": "needs_improvement",
                    },
                    "throughput": {
                        "requirement": "not assessed offline",
                        "design_support": "needs_improvement",
                    },
                },
                "scalability_findings": [
                    {
                        "finding_id": "SCALE-001",
                        "aspect": "Review Execution",
                        "severity": "medium",
                        "concern": "Offline mode used; live scalability review unavailable.",
                        "recommendation": "Run with a live provider to assess capacity, bottlenecks, and growth limits.",
                    }
                ],
                "capacity_considerations": [
                    "Document expected traffic and storage growth in the design ticket.",
                    "Describe caching, batching, and async processing strategy if applicable.",
                ],
                "bottlenecks": [
                    "No live analysis was performed in this environment."
                ],
                "recommendations": [
                    "Re-run the scalability review with a live provider.",
                    "Add explicit load, throughput, and growth assumptions to the design.",
                ],
                "summary": {
                    "overall_scalability_status": "adequate_with_considerations",
                    "total_findings": 1,
                    "critical": 0,
                    "high": 0,
                    "medium": 1,
                    "low": 0,
                },
            })

        return self._json({"message": "offline fallback", "model": self.model})

    def get_model_name(self) -> str:
        return self.model


class OpenAILLM(BaseLLM):
    """OpenAI GPT-4/3.5 integration"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **config):
        try:
            import openai
        except ImportError:
            raise ImportError("openai package required: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", float(os.getenv("LLM_TEMPERATURE", 0.7)))
        self.max_tokens = config.get("max_tokens", int(os.getenv("LLM_MAX_TOKENS", 4096)))
        
        self.client = openai.OpenAI(api_key=self.api_key)
        logger.info(f"Initialized OpenAI LLM with model: {self.model}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                timeout=kwargs.get("timeout", 60)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model


class AzureOpenAILLM(BaseLLM):
    """Azure OpenAI integration"""
    
    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None, **config):
        try:
            from openai import AzureOpenAI
        except ImportError:
            raise ImportError("openai package required: pip install openai")
        
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = config.get("deployment_name") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = config.get("api_version", os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"))
        self.temperature = config.get("temperature", float(os.getenv("LLM_TEMPERATURE", 0.7)))
        self.max_tokens = config.get("max_tokens", int(os.getenv("LLM_MAX_TOKENS", 4096)))
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        logger.info(f"Initialized Azure OpenAI with deployment: {self.deployment_name}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate using Azure OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                deployment_id=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                timeout=kwargs.get("timeout", 60)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Azure OpenAI error: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.deployment_name


class AnthropicLLM(BaseLLM):
    """Anthropic Claude integration"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229", **config):
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
        self.temperature = config.get("temperature", float(os.getenv("LLM_TEMPERATURE", 0.7)))
        self.max_tokens = config.get("max_tokens", int(os.getenv("LLM_MAX_TOKENS", 4096)))
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info(f"Initialized Anthropic LLM with model: {self.model}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate using Anthropic API"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature)
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model


class GoogleGeminiLLM(BaseLLM):
    """Google Gemini integration"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro", **config):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package required: pip install google-generativeai")
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model or os.getenv("GOOGLE_MODEL", "gemini-pro")
        self.temperature = config.get("temperature", float(os.getenv("LLM_TEMPERATURE", 0.7)))
        
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
        logger.info(f"Initialized Google Gemini with model: {self.model}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate using Google Gemini API"""
        try:
            response = self.client.generate_content(
                prompt,
                generation_config=dict(
                    temperature=kwargs.get("temperature", self.temperature),
                    max_output_tokens=kwargs.get("max_tokens", 4096)
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Google Gemini error: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model


class OllamaLLM(BaseLLM):
    """Local Ollama integration (free, runs locally)"""
    
    def __init__(self, base_url: Optional[str] = None, model: str = "mistral", **config):
        try:
            import requests
        except ImportError:
            raise ImportError("requests package required: pip install requests")
        
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral")
        self.temperature = config.get("temperature", float(os.getenv("LLM_TEMPERATURE", 0.7)))
        logger.info(f"Initialized Ollama LLM with model: {self.model} at {self.base_url}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate using Ollama API"""
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": kwargs.get("temperature", self.temperature),
                    "stream": False
                },
                timeout=kwargs.get("timeout", 300)
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama error: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model


class MistralLLM(BaseLLM):
    """Mistral AI integration"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-large", **config):
        try:
            from mistralai.client import MistralClient
            from mistralai.models.chat_message import ChatMessage
        except ImportError:
            raise ImportError("mistral-sdk package required: pip install mistral-sdk")
        
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.model = model or os.getenv("MISTRAL_MODEL", "mistral-large")
        self.temperature = config.get("temperature", float(os.getenv("LLM_TEMPERATURE", 0.7)))
        
        self.client = MistralClient(api_key=self.api_key)
        self.ChatMessage = ChatMessage
        logger.info(f"Initialized Mistral LLM with model: {self.model}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate using Mistral API"""
        try:
            response = self.client.chat(
                model=self.model,
                messages=[self.ChatMessage(role="user", content=prompt)],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", 4096)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Mistral API error: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model


class LLMFactory:
    """Factory to create LLM instances based on configuration"""
    
    PROVIDERS = {
        "offline": OfflineLLM,
        "openai": OpenAILLM,
        "azure": AzureOpenAILLM,
        "anthropic": AnthropicLLM,
        "google": GoogleGeminiLLM,
        "ollama": OllamaLLM,
        "mistral": MistralLLM
    }
    
    @staticmethod
    def create(provider: Optional[str] = None, **kwargs) -> BaseLLM:
        """
        Create LLM instance based on provider
        
        Args:
            provider: LLM provider name (openai, azure, anthropic, google, ollama, mistral)
            **kwargs: Provider-specific configuration
        
        Returns:
            BaseLLM instance
        """
        provider = provider or os.getenv("LLM_PROVIDER", "openai").lower()
        
        if provider not in LLMFactory.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}. Supported: {list(LLMFactory.PROVIDERS.keys())}")
        
        llm_class = LLMFactory.PROVIDERS[provider]
        logger.info(f"Creating {provider} LLM instance")
        return llm_class(**kwargs)
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available providers"""
        return list(LLMFactory.PROVIDERS.keys())


# Convenience function for getting default LLM
def get_default_llm() -> BaseLLM:
    """Get default LLM based on environment configuration"""
    return LLMFactory.create()
