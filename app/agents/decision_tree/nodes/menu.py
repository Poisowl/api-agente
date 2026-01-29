from typing import Any, Dict, Optional
from .base import BaseNode


class MenuNode(BaseNode):
    """Node that displays a menu and waits for user input."""
    
    def execute(self, context: Dict[str, Any], user_input: Optional[str] = None) -> Dict[str, Any]:
        """Execute menu node - waits for user input."""
        messages = []
        
        # If we have user input, process the selection
        if user_input:
            options = self.node_data.get("options", {})
            selected_option = user_input.strip()
            
            if selected_option in options:
                return {
                    "messages": [],  # No additional messages on valid selection
                    "next_node": options[selected_option],
                    "should_continue": True,  # Continue to next node
                    "handoff": False
                }
            else:
                # Invalid selection - show error and menu again
                messages.append("❌ Opción inválida. Por favor, seleccione una opción válida.")
        
        # Show the menu (first time or after invalid selection)
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