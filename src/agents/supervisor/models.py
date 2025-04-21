from pydantic import BaseModel, Field


class ClarificationRequest(BaseModel):
    follow_up_question: str = Field(
        description="The clarifying question to ask the user"
    )


class AgentDelegation(BaseModel):
    suggestion_agent: str | None = Field(
        description="The detailed task for the Suggestion Agent. None if this agent is not needed",
        default=None,
    )
    harm_agent: str | None = Field(
        description="The detailed task for the Harm Agent. None if this agent is not needed",
        default=None,
    )
    factor_agent: str | None = Field(
        description="The detailed task for the Factor Agent. None if this agent is not needed",
        default=None,
    )
    should_response: bool = Field(
        description=(
            "Set to True only if sufficient information has been gathered from all relevant agents, and this information is available (e.g., in the chat history). "
            "This field should never be set to True if one or more agents have pending tasks, as it indicates that the context is incomplete."
        ),
        default=False,
    )
