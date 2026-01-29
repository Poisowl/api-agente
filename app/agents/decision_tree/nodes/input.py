from typing import Any, Dict, Optional
from .base import BaseNode


class InputNode(BaseNode):
    """Node that requests user input and saves it to context."""
    
    def execute(self, context: Dict[str, Any], user_input: Optional[str] = None) -> Dict[str, Any]:
        """Execute input node - saves user input to context."""
        messages = []
        save_as = self.node_data.get("save_as")
        
        # If we have user input, save it and advance
        if user_input and save_as:
            context[save_as] = user_input.strip()
            return {
                "messages": [],  # No additional messages after saving input
                "next_node": self.get_next_node(),
                "should_continue": True,  # Continue to next node
                "handoff": False
            }
        
        # If no input provided, show the input prompt
        if isinstance(self.node_data.get("message"), list):
            messages.extend(self.node_data["message"])
        elif isinstance(self.node_data.get("message"), str):
            messages.append(self.node_data["message"])
        
        return {
            "messages": messages,
            "next_node": None,  # Don't advance automatically
            "should_continue": False,  # Wait for user input
            "handoff": False
        }