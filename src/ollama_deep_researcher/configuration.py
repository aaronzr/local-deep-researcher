import os
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional, Literal
from langchain_core.runnables import RunnableConfig

class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"
    SEARXNG = "searxng"

def detect_default_ollama_base_url() -> str:
    # Auto-detect whether running in Compose
    if os.environ.get("COMPOSE_PROJECT") or os.environ.get("COMPOSE_PROJECT_NAME"):
        # Inside Compose → use container network
        return "http://ollama:11434"
    elif os.environ.get("RUNNING_IN_DOCKER", "").lower() == "true":
        # Optional: if you define RUNNING_IN_DOCKER in plain docker run
        return "http://host.docker.internal:11434"
    else:
        # Local run
        return "http://localhost:11434"

class Configuration(BaseModel):
    """The configurable fields for the research assistant."""

    max_web_research_loops: int = Field(
        default=3,
        title="Research Depth",
        description="Number of research iterations to perform"
    )
    local_llm: str = Field(
        default="llama3.2",
        title="LLM Model Name",
        description="Name of the LLM model to use"
    )
    llm_provider: Literal["ollama", "lmstudio"] = Field(
        default="ollama",
        title="LLM Provider",
        description="Provider for the LLM (Ollama or LMStudio)"
    )
    search_api: Literal["perplexity", "tavily", "duckduckgo", "searxng"] = Field(
        default="duckduckgo",
        title="Search API",
        description="Web search API to use"
    )
    fetch_full_page: bool = Field(
        default=True,
        title="Fetch Full Page",
        description="Include the full page content in the search results"
    )
    ollama_base_url: str = Field(
        default_factory=lambda: os.environ.get("OLLAMA_BASE_URL", detect_default_ollama_base_url()),
        title="Ollama Base URL",
        description="Base URL for Ollama API"
    )
    lmstudio_base_url: str = Field(
        default_factory=lambda: os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
        title="LMStudio Base URL",
        description="Base URL for LMStudio OpenAI-compatible API"
    )
    strip_thinking_tokens: bool = Field(
        default=True,
        title="Strip Thinking Tokens",
        description="Whether to strip <think> tokens from model responses"
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        
        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}
        
        return cls(**values)
