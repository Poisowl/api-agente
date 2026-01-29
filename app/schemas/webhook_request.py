from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    type: str = Field(..., description="Tipo de mensaje: text, image, audio, etc.")
    content: str = Field(..., description="Contenido del mensaje")


class Metadata(BaseModel):
    profile_name: Optional[str] = None
    whatsapp_id: Optional[str] = None
    timestamp: Optional[str] = None
    # Campos adicionales de metadata que puedan ser necesarios
    extra: Optional[Dict[str, Any]] = None


class WebhookRequest(BaseModel):
    """
    Contrato de API para el endpoint /agent/process
    NO expone estado interno del servicio
    """
    channel: str = Field(..., description="Canal de comunicación: whatsapp, telegram, etc.")
    from_: str = Field(..., description="Identificador del usuario (phone, user_id, etc.)", alias="from")
    message: Message
    metadata: Optional[Metadata] = None
    
    class Config:
        # Permite el uso de aliases
        populate_by_name = True