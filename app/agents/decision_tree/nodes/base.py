from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseNode(ABC):
    """Base class for all decision tree nodes."""
    
    def __init__(self, node_id: str, node_data: Dict[str, Any]):
        self.node_id = node_id
        self.node_data = node_data
        self.node_type = node_data.get("type", "unknown")
    
    @abstractmethod
    def execute(self, context: Dict[str, Any], user_input: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the node logic.
        
        Returns:
            Dict containing:
                - messages: List of messages to send to user
                - next_node: Next node ID (if applicable)
                - should_continue: Whether to continue processing automatically
                - handoff: Whether to handoff to human
        """
        pass
    
    def get_next_node(self) -> Optional[str]:
        """Get the next node ID from node data."""
        return self.node_data.get("next")
    
    def get_message(self) -> Optional[str]:
        """Get the message from node data."""
        return self.node_data.get("message")
    
    def get_messages(self) -> Optional[list]:
        """Get multiple messages from node data."""
        return self.node_data.get("message", [])