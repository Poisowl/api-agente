from typing import Dict, Any
from app.core.engine import DecisionTreeEngine
from app.schemas.response import AgentResponse


class DecisionTreeAgent:
    """Decision tree agent that processes conversation flows."""

    def __init__(self):
        self.engine = DecisionTreeEngine()

    def process(self, request_data: Dict[str, Any]) -> AgentResponse:
        """Process a conversation request through the decision tree."""
        return self.engine.run(request_data)
