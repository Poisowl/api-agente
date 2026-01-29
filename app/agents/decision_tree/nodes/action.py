from typing import Any, Dict, Optional
from .base import BaseNode


class ActionNode(BaseNode):
    """Node that executes an action (like validation)."""
    
    def execute(self, context: Dict[str, Any], user_input: Optional[str] = None) -> Dict[str, Any]:
        """Execute action node - runs custom logic."""
        action_name = self.node_data.get("action")
        messages = []
        
        if action_name:
            # For now, we'll implement basic validation actions
            if action_name == "validate_dni":
                dni = context.get("dni", "")
                if self._validate_dni(dni):
                    messages.append("✅ DNI válido")
                else:
                    messages.append("❌ DNI inválido. Debe tener 8 dígitos.")
                    # Return to input node or show error
                    return {
                        "messages": messages,
                        "next_node": None,  # Stay on same node or go back
                        "should_continue": False,
                        "handoff": False
                    }
        
        # If action succeeds, continue to next node
        return {
            "messages": messages,
            "next_node": self.get_next_node(),
            "should_continue": True,
            "handoff": False
        }
    
    def _validate_dni(self, dni: str) -> bool:
        """Validate DNI format."""
        return len(dni) == 8 and dni.isdigit()