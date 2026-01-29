from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Reply(BaseModel):
    type: str = Field(..., description="Tipo de respuesta: text, image, audio, etc.")
    content: List[str] = Field(..., description="Contenido de la respuesta")


class WebhookResponse(BaseModel):
    """
    Respuesta del servicio de agentes para el endpoint /agent/process
    """
    reply: Reply
    handoff: bool = Field(False, description="Indica si se debe transferir a un humano")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata adicional opcional")
    
    class Config:
        # Ejemplo de respuesta
        json_schema_extra = {
            "example": {
                "reply": {
                    "type": "text",
                    "content": ["👋 Bienvenido al sistema de citas EsSalud", "🔐 Todo dato es cifrado para su seguridad"]
                },
                "handoff": False,
                "metadata": {
                    "flow_id": "citas_essalud",
                    "current_node": "welcome",
                    "context": {}
                }
            }
        }