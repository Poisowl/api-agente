from typing import List

from pydantic import BaseModel


class Reply(BaseModel):
    type: str
    content: List[str]

class AgentResponse(BaseModel):
    reply: Reply
    handoff: bool = False