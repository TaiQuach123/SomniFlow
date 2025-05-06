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
            "Indicates whether a final response can be generated for the user. "
            "Set to True if either: (1) sufficient information has been gathered "
            "from all relevant agents and is accessible (e.g., in the chat history), "
            "or (2) the query does not require context or delegation (e.g., greetings, simple acknowledgments). "
            "Do not set to True if any required agent tasks are still pending."
        ),
        default=False,
    )
