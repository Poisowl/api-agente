from pydantic import BaseModel


class Reply(BaseModel):
    type: str
    content: str

class AgentResponse(BaseModel):
    reply: Reply
    handoff: bool = False