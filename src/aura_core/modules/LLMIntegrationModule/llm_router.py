"""LLM Router agent for Orion Vision Core."""

import asyncio
import json
import os
import subprocess
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from ..core.base_agent import BaseAgent
from ..core.config import get_config
from ..core.exceptions import AgentError, LLMError


class LLMRequest(BaseModel):
    """LLM request model."""

    prompt: str = Field(..., description="Input prompt")
    model: Optional[str] = Field(None, description="Specific model to use")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: float = Field(0.7, ge=0, le=2, description="Sampling temperature")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LLMResponse(BaseModel):
    """LLM response model."""

    content: str = Field(..., description="Generated content")
    model_used: str = Field(..., description="Model that generated the response")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")


class LLMRouter(BaseAgent):
    """Agent for routing LLM requests to different models."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize LLMRouter.

        Args:
            config: Agent configuration
        """
        super().__init__("llm_router", config)

        self._config = get_config()
        self._client = httpx.AsyncClient(timeout=self._config.llm.timeout_seconds)

        # Load API keys from environment if not in config
        self._load_api_keys()

    def _load_api_keys(self) -> None:
        """Load API keys from environment variables."""
        env_keys = {
            "openrouter": os.getenv("OPENROUTER_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY"),
        }

        # Update config with environment keys
        for provider, key in env_keys.items():
            if key and provider not in self._config.llm.api_keys:
                self._config.llm.api_keys[provider] = key

    async def _custom_validate_task(self, task: Dict[str, Any]) -> None:
        """Validate LLM router specific tasks."""
        task_type = task.get("type")

        if task_type not in ["generate", "chat", "complete"]:
            raise AgentError(
                f"Invalid task type: {task_type}",
                agent_name=self.name,
                error_code="INVALID_TASK_TYPE"
            )

        if "prompt" not in task and "messages" not in task:
            raise AgentError(
                "Either 'prompt' or 'messages' is required",
                agent_name=self.name,
                error_code="MISSING_INPUT"
            )

    async def _execute_task(self, task: Dict[str, Any]) -> LLMResponse:
        """Execute LLM router task."""
        task_type = task.get("type", "generate")

        # Create LLM request
        llm_request = LLMRequest(
            prompt=task.get("prompt", ""),
            model=task.get("model"),
            max_tokens=task.get("max_tokens"),
            temperature=task.get("temperature", 0.7),
            system_prompt=task.get("system_prompt"),
            metadata=task.get("metadata", {})
        )

        # Route to appropriate model
        return await self._route_request(llm_request)

    async def _route_request(self, request: LLMRequest) -> LLMResponse:
        """Route LLM request to appropriate model."""
        errors = []

        # Try specific model if requested
        if request.model:
            try:
                return await self._call_model(request, request.model)
            except Exception as e:
                errors.append(f"Specific model {request.model} failed: {e}")

        # Try local model first if preferred
        if self._config.llm.prefer_local:
            try:
                return await self._call_local_model(request)
            except Exception as e:
                errors.append(f"Local model failed: {e}")
                self.logger.warning(f"Local model failed: {e}")

        # Try fallback models
        for model in self._config.llm.fallback_order:
            try:
                return await self._call_api_model(request, model)
            except Exception as e:
                errors.append(f"Model {model} failed: {e}")
                self.logger.warning(f"Model {model} failed: {e}")

        # All models failed
        error_msg = f"All models failed: {'; '.join(errors)}"
        raise LLMError(
            error_msg,
            error_code="ALL_MODELS_FAILED",
            details={"errors": errors, "agent_name": self.name}
        )

    async def _call_local_model(self, request: LLMRequest) -> LLMResponse:
        """Call local Ollama model."""
        model_name = self._config.llm.local_model

        try:
            # Set environment for Turkish locale
            env = os.environ.copy()
            env['LANG'] = 'tr_TR.UTF-8'

            # Build command
            command = ["ollama", "run", model_name]

            # Add system prompt if provided
            if request.system_prompt:
                full_prompt = f"System: {request.system_prompt}\n\nUser: {request.prompt}"
            else:
                full_prompt = request.prompt

            # Run command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )

            stdout, stderr = await process.communicate(full_prompt.encode('utf-8'))

            if process.returncode != 0:
                raise LLMError(
                    f"Ollama command failed: {stderr.decode('utf-8')}",
                    model_name=model_name,
                    error_code="OLLAMA_FAILED"
                )

            content = stdout.decode('utf-8').strip()

            return LLMResponse(
                content=content,
                model_used=f"ollama/{model_name}",
                tokens_used=None,
                finish_reason="stop",
                metadata={"provider": "ollama", "local": True}
            )

        except Exception as e:
            raise LLMError(
                f"Local model execution failed: {e}",
                model_name=model_name,
                error_code="LOCAL_EXECUTION_FAILED"
            )

    async def _call_api_model(self, request: LLMRequest, model: str) -> LLMResponse:
        """Call API model."""
        provider = model.split('/')[0] if '/' in model else model
        api_key = self._config.llm.api_keys.get(provider)

        if not api_key:
            raise LLMError(
                f"API key not found for provider: {provider}",
                model_name=model,
                error_code="API_KEY_MISSING"
            )

        if "openrouter" in provider:
            return await self._call_openrouter(request, model, api_key)
        elif "openai" in provider:
            return await self._call_openai(request, model, api_key)
        else:
            raise LLMError(
                f"Unsupported API provider: {provider}",
                model_name=model,
                error_code="UNSUPPORTED_PROVIDER"
            )

    async def _call_openrouter(self, request: LLMRequest, model: str, api_key: str) -> LLMResponse:
        """Call OpenRouter API."""
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://orion-vision-core.local",
            "X-Title": "Orion Vision Core"
        }

        # Build messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        data = {
            "model": model,
            "messages": messages,
            "temperature": request.temperature,
        }

        if request.max_tokens:
            data["max_tokens"] = request.max_tokens

        try:
            response = await self._client.post(url, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            choice = result["choices"][0]

            return LLMResponse(
                content=choice["message"]["content"],
                model_used=model,
                tokens_used=result.get("usage", {}).get("total_tokens"),
                finish_reason=choice.get("finish_reason"),
                metadata={"provider": "openrouter", "usage": result.get("usage", {})}
            )

        except httpx.HTTPStatusError as e:
            raise LLMError(
                f"OpenRouter API error: {e.response.status_code} - {e.response.text}",
                model_name=model,
                error_code="OPENROUTER_API_ERROR"
            )
        except Exception as e:
            raise LLMError(
                f"OpenRouter request failed: {e}",
                model_name=model,
                error_code="OPENROUTER_REQUEST_FAILED"
            )

    async def _call_openai(self, request: LLMRequest, model: str, api_key: str) -> LLMResponse:
        """Call OpenAI API."""
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Build messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        data = {
            "model": model,
            "messages": messages,
            "temperature": request.temperature,
        }

        if request.max_tokens:
            data["max_tokens"] = request.max_tokens

        try:
            response = await self._client.post(url, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            choice = result["choices"][0]

            return LLMResponse(
                content=choice["message"]["content"],
                model_used=model,
                tokens_used=result.get("usage", {}).get("total_tokens"),
                finish_reason=choice.get("finish_reason"),
                metadata={"provider": "openai", "usage": result.get("usage", {})}
            )

        except httpx.HTTPStatusError as e:
            raise LLMError(
                f"OpenAI API error: {e.response.status_code} - {e.response.text}",
                model_name=model,
                error_code="OPENAI_API_ERROR"
            )
        except Exception as e:
            raise LLMError(
                f"OpenAI request failed: {e}",
                model_name=model,
                error_code="OPENAI_REQUEST_FAILED"
            )

    async def _call_model(self, request: LLMRequest, model: str) -> LLMResponse:
        """Call specific model (local or API)."""
        if model.startswith("ollama/") or model in ["mistral", "llama2", "codellama"]:
            # Local model
            local_request = LLMRequest(**request.model_dump())
            return await self._call_local_model(local_request)
        else:
            # API model
            return await self._call_api_model(request, model)

    async def _custom_stop(self) -> None:
        """Custom stop logic for LLM router."""
        if self._client:
            await self._client.aclose()


# Legacy function for backward compatibility
async def route_llm_request(prompt: str, model: Optional[str] = None) -> str:
    """Legacy function for routing LLM requests."""
    router = LLMRouter()
    task = {
        "type": "generate",
        "prompt": prompt,
        "model": model
    }
    result = await router.execute(task)

    if result.success:
        return result.data.content
    else:
        return f"Error: {result.error}"