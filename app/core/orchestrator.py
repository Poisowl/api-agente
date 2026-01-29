from typing import Dict, Any
from app.agents.decision_tree.agent import DecisionTreeAgent
from app.schemas.webhook_request import WebhookRequest
from app.schemas.webhook_response import WebhookResponse
from app.core.config import settings


class Orchestrator:
    """Main orchestrator that handles incoming requests and delegates to appropriate agents."""
    
    def __init__(self):
        self.decision_tree_agent = DecisionTreeAgent()
    
    def handle_webhook(self, webhook: WebhookRequest) -> WebhookResponse:
        """
        Handle an incoming webhook request.
        Genera conversation_id a partir de channel + from.
        """
        # Generar conversation_id único a partir de channel + from
        conversation_id = f"{webhook.channel}:{webhook.from_}"
        
        # Determinar flow_id (por ahora usamos uno por defecto, pero podría venir de config o metadata)
        flow_id = settings.default_flow_id  # Usar configuración centralizada
        
        # Extraer user_input del mensaje
        user_input = webhook.message.content if webhook.message.type == "text" else None
        
        # Convert request to dict format expected by the agent
        request_data = {
            "conversation_id": conversation_id,
            "flow_id": flow_id,
            "user_input": user_input,
            "context": {}  # El contexto se maneja internamente
        }
        
        # Process with decision tree agent
        agent_response = self.decision_tree_agent.process(request_data)
        
        # Convertir la respuesta del agente al formato webhook
        return WebhookResponse(
            reply={
                "type": agent_response.reply.type,
                "content": agent_response.reply.content
            },
            handoff=agent_response.handoff,
            metadata={
                "flow_id": flow_id,
                "channel": webhook.channel,
                "from": webhook.from_
            }
        )