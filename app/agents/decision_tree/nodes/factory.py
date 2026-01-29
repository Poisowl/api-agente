from typing import Dict, Any
from .base import BaseNode
from .message import MessageNode
from .menu import MenuNode
from .input import InputNode
from .action import ActionNode
from .end import EndNode


def create_node(node_id: str, node_data: Dict[str, Any]) -> BaseNode:
    """Factory function to create appropriate node instance based on type."""
    node_type = node_data.get("type", "unknown")
    
    if node_type == "message":
        return MessageNode(node_id, node_data)
    elif node_type == "menu":
        return MenuNode(node_id, node_data)
    elif node_type == "input":
        return InputNode(node_id, node_data)
    elif node_type == "action":
        return ActionNode(node_id, node_data)
    elif node_type == "end":
        return EndNode(node_id, node_data)
    else:
        raise ValueError(f"Unknown node type: {node_type}")