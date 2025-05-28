"""Configuration management for Orion Vision Core."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ConfigError
from .logging import get_logger

logger = get_logger(__name__)


class LLMConfig(BaseModel):
    """LLM configuration model."""

    prefer_local: bool = Field(True, description="Prefer local models over API")
    local_model: str = Field("mistral", description="Default local model name")
    fallback_order: List[str] = Field(
        default_factory=lambda: [
            "openrouter/claude-3-haiku",
            "openrouter/command-r",
            "google/palm-chat"
        ],
        description="Fallback model order"
    )
    api_keys: Dict[str, str] = Field(
        default_factory=dict,
        description="API keys for different providers"
    )
    timeout_seconds: float = Field(30.0, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum number of retries")

    @field_validator('api_keys')
    @classmethod
    def validate_api_keys(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate API keys format."""
        for provider, key in v.items():
            if not key or not isinstance(key, str):
                raise ValueError(f"Invalid API key for provider: {provider}")
        return v


class PersonaConfig(BaseModel):
    """Persona configuration model."""

    tone: str = Field("dürüst, stratejik, sakin", description="Personality tone")
    roles: str = Field("danışman, analizci, teknik asistan", description="Roles")
    language: str = Field("tr", description="Primary language")
    response_style: str = Field("professional", description="Response style")


class AgentConfig(BaseModel):
    """Agent configuration model."""

    enabled: bool = Field(True, description="Whether agent is enabled")
    timeout_seconds: float = Field(30.0, description="Agent timeout")
    max_retries: int = Field(3, description="Maximum retries")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific config")


class Config(BaseSettings):
    """Main configuration class."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    # Logging
    log_level: str = Field(default="INFO")
    log_file: Optional[str] = Field(default=None)
    json_logs: bool = Field(default=False)

    # Paths
    config_dir: Path = Field(default=Path("orion_vision_core/config"))
    memory_dir: Path = Field(default=Path("orion_vision_core/memory"))

    # LLM Configuration
    llm: LLMConfig = Field(default_factory=lambda: LLMConfig())

    # Persona Configuration
    persona: PersonaConfig = Field(default_factory=lambda: PersonaConfig())

    # Agent Configurations
    agents: Dict[str, AgentConfig] = Field(default_factory=dict)

    # API Configuration
    api_host: str = Field(default="localhost")
    api_port: int = Field(default=8001)

    def __init__(self, **kwargs):
        """Initialize configuration."""
        super().__init__(**kwargs)
        self._load_config_files()

    def _load_config_files(self) -> None:
        """Load configuration from JSON files."""
        try:
            # Load LLM config
            llm_config_path = self.config_dir / "llm_config.json"
            if llm_config_path.exists():
                with open(llm_config_path, 'r', encoding='utf-8') as f:
                    llm_data = json.load(f)
                    if "llm_selection_strategy" in llm_data:
                        strategy = llm_data["llm_selection_strategy"]
                        self.llm.prefer_local = strategy.get("prefer_local", True)
                        self.llm.local_model = strategy.get("local_model", "mistral")
                        self.llm.fallback_order = strategy.get("fallback_order", [])
                    if "api_keys" in llm_data:
                        self.llm.api_keys = llm_data["api_keys"]

            # Load persona config
            persona_config_path = self.config_dir / "persona.json"
            if persona_config_path.exists():
                with open(persona_config_path, 'r', encoding='utf-8') as f:
                    persona_data = json.load(f)
                    self.persona.tone = persona_data.get("ton", self.persona.tone)
                    self.persona.roles = persona_data.get("roller", self.persona.roles)

        except Exception as e:
            logger.warning(f"Failed to load config files: {e}")

    def save_config_files(self) -> None:
        """Save configuration to JSON files."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Save LLM config
            llm_config_path = self.config_dir / "llm_config.json"
            llm_data = {
                "llm_selection_strategy": {
                    "prefer_local": self.llm.prefer_local,
                    "local_model": self.llm.local_model,
                    "fallback_order": self.llm.fallback_order,
                },
                "api_keys": self.llm.api_keys,
                "timeout_seconds": self.llm.timeout_seconds,
                "max_retries": self.llm.max_retries,
            }
            with open(llm_config_path, 'w', encoding='utf-8') as f:
                json.dump(llm_data, f, indent=2, ensure_ascii=False)

            # Save persona config
            persona_config_path = self.config_dir / "persona.json"
            persona_data = {
                "ton": self.persona.tone,
                "roller": self.persona.roles,
                "language": self.persona.language,
                "response_style": self.persona.response_style,
            }
            with open(persona_config_path, 'w', encoding='utf-8') as f:
                json.dump(persona_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise ConfigError(f"Failed to save config files: {e}")

    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """Get configuration for a specific agent."""
        if agent_name not in self.agents:
            self.agents[agent_name] = AgentConfig()
        return self.agents[agent_name]

    def update_agent_config(self, agent_name: str, config: Dict[str, Any]) -> None:
        """Update configuration for a specific agent."""
        if agent_name not in self.agents:
            self.agents[agent_name] = AgentConfig()

        for key, value in config.items():
            if hasattr(self.agents[agent_name], key):
                setattr(self.agents[agent_name], key, value)
            else:
                self.agents[agent_name].config[key] = value


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def load_config_from_file(config_path: Union[str, Path]) -> Config:
    """Load configuration from a specific file."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return Config(**config_data)
    except Exception as e:
        raise ConfigError(f"Failed to load configuration from {config_path}: {e}")


def save_config_to_file(config: Config, config_path: Union[str, Path]) -> None:
    """Save configuration to a specific file."""
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config.dict(), f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        raise ConfigError(f"Failed to save configuration to {config_path}: {e}")
