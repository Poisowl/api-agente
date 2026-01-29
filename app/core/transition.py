from typing import Dict, Any, Optional, List
from app.agents.decision_tree.nodes.factory import create_node
from app.core.renderer import MessageRenderer


class TransitionManager:
    """Manages transitions between nodes in the decision tree."""

    def __init__(self):
        self.renderer = MessageRenderer()

    def process_node(
        self,
        node_id: str,
        flow_data: Dict[str, Any],
        context: Dict[str, Any],
        user_input: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a single node and return the result."""
        nodes = flow_data.get("nodes", {})

        if node_id not in nodes:
            raise ValueError(f"Node {node_id} not found in flow")

        node_data = nodes[node_id]
        node = create_node(node_id, node_data)

        # Execute the node
        result = node.execute(context, user_input)

        # Render any messages
        if result.get("messages"):
            result["messages"] = self.renderer.render_messages(
                result["messages"], context
            )

        return result

    def get_auto_nodes(self) -> List[str]:
        """Get list of node types that should auto-advance."""
        return ["message"]  # Message nodes auto-advance
