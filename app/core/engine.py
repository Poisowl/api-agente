from typing import List, Dict, Any, Optional
from app.agents.decision_tree.loader import load_flow
from app.core.state import get_state, save_state, debug_state_store
from app.core.transition import TransitionManager
from app.schemas.response import AgentResponse, Reply


class DecisionTreeEngine:
    """Engine that processes decision tree flows."""

    def __init__(self):
        self.transition_manager = TransitionManager()

    def run(self, request_data: Dict[str, Any]) -> AgentResponse:
        """Process a decision tree flow based on the request data."""
        conversation_id = request_data["conversation_id"]
        flow_id = request_data["flow_id"]
        user_input = request_data.get("user_input")

        # Load the flow configuration
        flow = load_flow(flow_id)

        # Get or create conversation state
        state = get_state(conversation_id, flow_id)
        
        # Debug: Log estado actual
        print(f"DEBUG: Estado actual - conversation_id: {conversation_id}, current_node: {state.current_node}, context: {state.context}")
        debug_state_store()

        # Set initial node if not set
        if state.current_node is None:
            state.current_node = flow.get("start_node")
            print(f"DEBUG: Estableciendo nodo inicial: {state.current_node}")
        else:
            print(f"DEBUG: Continuando desde nodo: {state.current_node}")

        # Update context with any provided context
        if request_data.get("context"):
            state.context.update(request_data["context"])

        all_messages: List[str] = []
        handoff = False

        # Process nodes until we hit one that requires user input
        while state.current_node:
            result = self.transition_manager.process_node(
                state.current_node, flow, state.context, user_input
            )

            # Add messages to response
            if result.get("messages"):
                all_messages.extend(result["messages"])

            # Update current node
            state.current_node = result.get("next_node")
            
            # Guardar estado después de cada nodo procesado
            save_state(state)

            # Check if we should continue processing
            if not result.get("should_continue", False):
                break

            # Check if conversation should end
            if result.get("handoff", False):
                handoff = True
                break

            # Clear user input after first processing (only used for first node)
            user_input = None

        # Guardar el estado después del procesamiento
        save_state(state)

        return AgentResponse(
            reply=Reply(type="text", content=all_messages), handoff=handoff
        )
