from typing import Any, Dict, Optional
from .base import BaseNode


class EndNode(BaseNode):
    """Node that ends the conversation flow."""
    
    def execute(self, context: Dict[str, Any], user_input: Optional[str] = None) -> Dict[str, Any]:
        """Execute end node - finalizes the conversation."""
        messages = []
        
        # Show final message
        if isinstance(self.node_data.get("message"), list):
            messages.extend(self.node_data["message"])
        elif isinstance(self.node_data.get("message"), str):
            messages.append(self.node_data["message"])
        
        return {
            "messages": messages,
            "next_node": None,  # No next node
            "should_continue": False,  # Stop processing
            "handoff": True  # Signal conversation end
        }