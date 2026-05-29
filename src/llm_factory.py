"""
LLM Factory - Multi-LLM Support

Provides factory pattern to instantiate different LLM providers dynamically.
Supports: OpenAI, Azure OpenAI, Anthropic, Google Gemini, Ollama, Mistral
"""

import os
import logging
import json
import re
import time
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

        if (
            "requirement extraction specialist" in prompt_lower
            or "requirements analysis expert" in prompt_lower
            or "analyze the following jira requirement" in prompt_lower
        ):
            ticket_id = self._extract(prompt, "TICKET") or "UNKNOWN"
            summary = self._extract(prompt, "SUMMARY")
            return self._json({
                "ticket_id": ticket_id,
                "ticket_summary": summary or "not provided",
                "requirements": [
                    {
                        "id": "REQ-001",
                        "statement": "Offline fallback was used because live Gemini output was not trustworthy in this environment.",
                        "type": "assumption",
                        "priority": "medium",
                        "source": "offline_fallback",
                        "acceptance_criteria": ["Re-run with a working live model."],
                        "design_focus_area": "review_pipeline",
                        "notes": "Structured fallback to preserve usable output.",
                    }
                ],
                "summary": {
                    "total_requirements": 1,
                    "functional": 0,
                    "non_functional": 0,
                    "constraints": 0,
                    "assumptions": 1,
                    "critical": 0,
                    "high": 0,
                    "medium": 1,
                    "low": 0,
                },
                "key_design_focus_areas": [
                    {
                        "area": "review_pipeline",
                        "requirements_count": 1,
                        "importance": "high",
                        "description": "Make the live LLM path return complete JSON reliably.",
                    }
                ],
                "ambiguities": [],
                "assumptions_to_validate": [
                    {
                        "assumption": "The live model can return complete JSON for this prompt.",
                        "implication": "Primary analysis can be used without fallback.",
                        "risk_if_invalid": "Offline fallback will continue to be used.",
                    }
                ],
                "recommendations": [
                    {
                        "priority": "high",
                        "type": "validation",
                        "description": "Verify Gemini output completeness and parsing stability.",
                        "rationale": "This is required before trusting live analysis results.",
                    }
                ],
                "notes": "Offline fallback generated because the live response was not trustworthy in this run.",
            })

        if (
            "design review specialist" in prompt_lower
            or "design document review" in prompt_lower
            or "software architect" in prompt_lower
        ):
            return self._json({
                "requirements_coverage": {
                    "total_requirements": 1,
                    "complete": 0,
                    "partial": 1,
                    "missing": 0,
                    "coverage_percentage": 0,
                },
                "design_findings": [
                    {
                        "finding_id": "FIND-001",
                        "issue": "Offline fallback used because live Gemini output was not parseable.",
                        "severity": "medium",
                        "category": "feasibility",
                        "recommendation": "Stabilize the live model output or use a deterministic local model for reviews.",
                        "effort": "low",
                    }
                ],
                "quality_assessment": {
                    "solid_principles": "partial",
                    "design_patterns": "questionable",
                    "separation_of_concerns": "needs_improvement",
                },
                "summary": {
                    "overall_status": "review_required",
                    "total_findings": 1,
                    "critical": 0,
                    "high": 0,
                    "medium": 1,
                    "low": 0,
                },
            })

        if (
            "code review specialist" in prompt_lower
            or "repository code review" in prompt_lower
            or "code perspective" in prompt_lower
            or "design and repository" in prompt_lower
        ):
            return self._json({
                "repository_context": {
                    "repository": self._extract(prompt, "REPOSITORY") or "unknown",
                    "branch": self._extract(prompt, "BRANCH") or "unknown",
                    "files_reviewed": 1,
                },
                "code_findings": [
                    {
                        "finding_id": "CODE-001",
                        "issue": "Offline fallback used because the live model response was not stable enough for code review.",
                        "severity": "medium",
                        "category": "process",
                        "file_path": "n/a",
                        "recommendation": "Re-run with a stable live model or keep the offline reviewer for deterministic output.",
                    }
                ],
                "implementation_assessment": {
                    "design_implemented": "partial",
                    "architecture_match": "needs_improvement",
                    "test_coverage": "unknown",
                    "maintainability": "fair",
                },
                "summary": {
                    "overall_status": "review_required",
                    "total_findings": 1,
                    "critical": 0,
                    "high": 0,
                    "medium": 1,
                    "low": 0,
                    "code_alignment_score": 45,
                },
            })

        if (
            "implementation feasibility specialist" in prompt_lower
            or "implementation feasibility" in prompt_lower
            or "feasibility check" in prompt_lower
            or "can we build this" in prompt_lower
        ):
            return self._json({
                "feasibility_assessment": {
                    "implementable": "partial",
                    "confidence": "medium",
                    "overall_risk": "medium",
                    "summary": "The approach is feasible, but it needs structural changes before implementation can be trusted."
                },
                "feasibility_findings": [
                    {
                        "finding_id": "FEAS-001",
                        "issue": "Offline fallback used because the live model response was not stable enough for feasibility review.",
                        "category": "process",
                        "severity": "medium",
                        "required_change": "Re-run with a stable model or use offline output intentionally.",
                        "recommendation": "Validate the design in smaller implementation slices."
                    }
                ],
                "required_changes": [
                    {
                        "area": "review_pipeline",
                        "change": "Stabilize the live review flow",
                        "priority": "high",
                        "effort": "low"
                    }
                ],
                "implementation_steps": [
                    "Confirm the approach with stakeholders",
                    "Identify missing components",
                    "Implement changes in small steps"
                ],
                "summary": {
                    "overall_status": "implementable_with_changes",
                    "total_findings": 1,
                    "critical": 0,
                    "high": 0,
                    "medium": 1,
                    "low": 0,
                    "implementation_feasibility_score": 55,
                },
            })

        if "design security specialist" in prompt_lower or "security expert" in prompt_lower:
            return self._json({
                "security_findings": [
                    {
                        "finding_id": "SEC-001",
                        "issue": "Offline fallback used instead of a live security review.",
                        "severity": "medium",
                        "category": "process",
                        "recommendation": "Re-run security analysis with a stable Gemini response or keep the offline reviewer for deterministic output.",
                    }
                ],
                "security_requirements_coverage": {
                    "total_requirements": 1,
                    "covered": 0,
                    "partial": 1,
                    "missing": 0,
                },
                "threat_assessment": {
                    "identified_threats": 1,
                    "critical": 0,
                    "high": 0,
                    "medium": 1,
                },
                "summary": {
                    "overall_security_status": "needs_security_review",
                    "total_findings": 1,
                    "critical": 0,
                    "high": 0,
                    "medium": 1,
                    "low": 0,
                    "security_score": 40,
                },
            })

        if "design scalability specialist" in prompt_lower or "scalability expert" in prompt_lower:
            return self._json({
                "scalability_findings": [
                    {
                        "finding_id": "SCALE-001",
                        "aspect": "Review Execution",
                        "severity": "medium",
                        "concern": "Offline fallback used instead of a live scalability review.",
                        "recommendation": "Re-run once the live Gemini path is stable or use offline mode intentionally.",
                    }
                ],
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
                "scalability_requirements_coverage": {
                    "total_requirements": 1,
                    "covered": 0,
                    "partial": 1,
                    "missing": 0,
                },
                "summary": {
                    "overall_scalability_status": "adequate_with_considerations",
                    "total_findings": 1,
                    "critical": 0,
                    "high": 0,
                    "medium": 1,
                    "low": 0,
                    "scalability_score": 40,
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
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **config):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self._sdk = None
        self._genai = None
        self._types = None
        self.client = None

        try:
            from google import genai as google_genai
            from google.genai import types as google_types

            self._sdk = "google-genai"
            self._genai = google_genai
            self._types = google_types
            self.client = google_genai.Client(api_key=self.api_key)
        except ImportError:
            try:
                import google.generativeai as legacy_genai
            except ImportError as exc:
                raise ImportError(
                    "google-genai package required: pip install google-genai"
                ) from exc

            self._sdk = "google-generativeai"
            self._genai = legacy_genai
            legacy_genai.configure(api_key=self.api_key)
            self.client = None

        configured_model = model or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash-lite")
        self.model = self._resolve_model_name(configured_model)
        self.temperature = config.get("temperature", float(os.getenv("LLM_TEMPERATURE", 0.7)))

        if self._sdk == "google-generativeai":
            self.client = self._genai.GenerativeModel(self.model)

        logger.info(f"Initialized Google Gemini with model: {self.model}")

    def _extract_response_text(self, response: Any) -> str:
        """Collect text from all candidate parts instead of trusting response.text only."""
        parts: list[str] = []

        try:
            candidates = getattr(response, "candidates", None) or []
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                for part in getattr(content, "parts", None) or []:
                    text = getattr(part, "text", None)
                    if text:
                        parts.append(text)
        except Exception:
            parts = []

        if parts:
            return "".join(parts)

        text = getattr(response, "text", None)
        return text if isinstance(text, str) else str(text or "")

    def _extract_parsed_response(self, response: Any) -> Any:
        """Return structured Gemini output when the SDK provides it."""
        parsed = getattr(response, "parsed", None)
        if parsed is not None:
            return parsed
        return None

    def _resolve_model_name(self, requested_model: str) -> str:
        """Map deprecated aliases to a currently supported Gemini model."""
        aliases = {
            "gemini-pro": "gemini-1.5-flash-002",
            "gemini-1.5-flash": "gemini-1.5-flash-002",
            "gemini-1.5-flash-latest": "gemini-1.5-flash-002",
            "gemini-2.5-flash-latest": "gemini-2.5-flash",
            "gemini-2.5-flash-lite-latest": "gemini-2.5-flash-lite",
        }
        preferred_model = aliases.get(requested_model, requested_model)

        try:
            supported_models = []
            if self._sdk == "google-genai" and self.client is not None:
                model_iter = self.client.models.list()
                for model_info in model_iter:
                    model_name = getattr(model_info, "name", "")
                    if model_name.startswith("models/"):
                        model_name = model_name.split("/", 1)[1]

                    supported_methods = (
                        getattr(model_info, "supported_actions", None)
                        or getattr(model_info, "supported_generation_methods", None)
                        or []
                    )
                    if "generateContent" in supported_methods:
                        supported_models.append(model_name)
            elif self._sdk == "google-generativeai":
                for model_info in self._genai.list_models(page_size=100):
                    model_name = getattr(model_info, "name", "")
                    if model_name.startswith("models/"):
                        model_name = model_name.split("/", 1)[1]

                    supported_methods = (
                        getattr(model_info, "supported_generation_methods", None)
                        or getattr(model_info, "supported_actions", None)
                        or []
                    )

                    if "generateContent" in supported_methods:
                        supported_models.append(model_name)

            for candidate in (
                preferred_model,
                "gemini-2.5-flash-lite",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash-002",
                "gemini-1.5-flash-001",
            ):
                if candidate in supported_models:
                    return candidate
        except Exception as exc:
            logger.warning(f"Could not list Gemini models, using fallback '{preferred_model}': {exc}")

        return preferred_model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate using Google Gemini API"""
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", 8192)
        schema = kwargs.get("response_schema")
        attempts = kwargs.get("retry_attempts", 3)

        last_error = None
        for attempt in range(1, attempts + 1):
            try:
                if self._sdk == "google-genai":
                    generation_config_kwargs = dict(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                        response_mime_type=kwargs.get("response_mime_type", "text/plain"),
                    )
                    if schema is not None:
                        generation_config_kwargs["response_schema"] = schema
                    generation_config = self._types.GenerateContentConfig(**generation_config_kwargs)
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=generation_config,
                    )
                else:
                    generation_config = dict(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                        response_mime_type=kwargs.get("response_mime_type", "text/plain"),
                    )
                    if schema is not None:
                        generation_config["response_schema"] = schema
                    response = self.client.generate_content(
                        prompt,
                        generation_config=generation_config
                    )

                parsed = self._extract_parsed_response(response)
                if parsed is not None:
                    if hasattr(parsed, "model_dump"):
                        parsed = parsed.model_dump(exclude_none=True)
                    return json.dumps(parsed, ensure_ascii=False)
                return self._extract_response_text(response)

            except Exception as e:
                last_error = e
                error_text = str(e)
                is_retryable = "503" in error_text or "UNAVAILABLE" in error_text

                if attempt < attempts and is_retryable:
                    delay = min(2 ** (attempt - 1), 8)
                    logger.warning(
                        f"Google Gemini attempt {attempt} failed with retryable error: {error_text}. "
                        f"Retrying in {delay}s."
                    )
                    time.sleep(delay)
                    continue

                logger.error(f"Google Gemini error: {error_text}")
                raise

        if last_error is not None:
            raise last_error
    
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
    PROVIDER_ALIASES = {
        "gemini": "google",
    }

    @staticmethod
    def _normalize_provider(provider: Optional[str]) -> str:
        normalized = (provider or os.getenv("LLM_PROVIDER", "openai")).lower()
        return LLMFactory.PROVIDER_ALIASES.get(normalized, normalized)
    
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
        provider = LLMFactory._normalize_provider(provider)
        
        if provider not in LLMFactory.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}. Supported: {list(LLMFactory.PROVIDERS.keys())}")
        
        llm_class = LLMFactory.PROVIDERS[provider]
        logger.info(f"Creating {provider} LLM instance")
        return llm_class(**kwargs)
    
    @staticmethod
    def create_with_fallback(primary_provider: Optional[str] = None, **kwargs) -> BaseLLM:
        """
        Create LLM instance with automatic fallback to alternative providers
        
        Tries providers in order: primary -> google gemini -> offline
        This helps when primary provider (e.g., OpenAI) has quota issues
        
        Args:
            primary_provider: Primary LLM provider (default from .env or openai)
            **kwargs: Provider-specific configuration
        
        Returns:
            BaseLLM instance (whichever provider succeeds)
        """
        primary_provider = LLMFactory._normalize_provider(primary_provider)
        fallback_providers = ["google", "offline"]

        providers_to_try = list(dict.fromkeys([primary_provider] + fallback_providers))
        
        for provider in providers_to_try:
            try:
                provider = LLMFactory._normalize_provider(provider)

                if provider not in LLMFactory.PROVIDERS:
                    logger.warning(f"Provider {provider} not found, skipping")
                    continue
                
                logger.info(f"Attempting to create {provider} LLM instance")
                llm_class = LLMFactory.PROVIDERS[provider]
                llm_instance = llm_class(**kwargs)
                logger.info(f"✓ Successfully created {provider} LLM instance")
                return llm_instance
                
            except Exception as e:
                logger.warning(f"Failed to create {provider} LLM: {type(e).__name__}: {str(e)}")
                if provider == providers_to_try[-1]:
                    # Last provider failed, raise error
                    logger.error(f"All LLM providers failed. Last error: {str(e)}")
                    raise
                # Try next provider
                continue
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available providers"""
        return list(LLMFactory.PROVIDERS.keys())


# Convenience function for getting default LLM
def get_default_llm() -> BaseLLM:
    """Get default LLM based on environment configuration"""
    return LLMFactory.create()
