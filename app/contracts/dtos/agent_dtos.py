from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ChatMessageDto(BaseModel):
    """
    Summary: Represents a single message in the chat history.
    """

    role: str

    content: str

    timestamp: Optional[datetime] = None


class AgentRequest(BaseModel):
    """
    Summary: Request payload for the Discovery Agent.
    """

    message: str = Field(..., min_length=1)

    history: List[ChatMessageDto] = Field(default_factory=list)


class AgentResponse(BaseModel):
    """
    Summary: Response payload from the Discovery Agent.
    """

    answer: str

    suggested_query: Optional[str] = None

    related_identifiers: List[str] = Field(default_factory=list)

