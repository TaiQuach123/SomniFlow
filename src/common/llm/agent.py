from typing import Literal

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


def create_llm_agent(
    provider: Literal["ollama", "groq"] = "ollama",
    model_name: str = "qwen2.5-coder",
    base_url: str = "http://localhost:11434/v1",
    **kwargs,
) -> Agent:
    """Create an LLM agent with standard configuration"""
    if provider == "ollama":
        llm = OpenAIModel(
            model_name=model_name,
            provider=OpenAIProvider(base_url=base_url),
        )
    elif provider == "groq":
        llm = f"groq:{model_name}"

    else:
        raise ValueError(f"Unsupported provider: {provider}")

    return Agent(llm, **kwargs)
