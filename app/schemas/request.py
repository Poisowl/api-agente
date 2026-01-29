from typing import Optional
from pydantic import BaseModel


class AgentRequest(BaseModel):
    conversation_id: str
    flow_id: str
    current_node: Optional[str] = None
    context: dict = {}
    user_input: Optional[str] = None