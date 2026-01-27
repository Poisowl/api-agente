from pydantic import BaseModel


class Message(BaseModel):
    type: str
    content: str

class AgentRequest(BaseModel):
    conversation_id: str
    user_id: str
    channel: str
    message: Message
    metadata: dict | None = None