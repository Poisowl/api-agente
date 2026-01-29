"""
API REST Simplificada del Chatbot
Solo maneja user_id y message en request/response
"""

import json
import re
from datetime import datetime

# Importar el engine del chatbot
from test.chatbot import ChatBotEngine
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =====================================================
# MODELOS DE DATOS
# =====================================================


class ChatRequest(BaseModel):
    """Modelo para el request del chat"""

    user_id: str
    message: Optional[str] = None  # Puede ser None en el primer mensaje
    metadata: Optional[Dict[str, Any]] = None  # Solo para el primer mensaje

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "user_id": "whatsapp_51987654321",
                    "message": None,
                    "metadata": {"usuarioNombre": "Carlos Pérez"},
                },
                {"user_id": "whatsapp_51987654321", "message": "1"},
                {"user_id": "whatsapp_51987654321", "message": "carlos@example.com"},
            ]
        }


class ChatResponse(BaseModel):
    """Modelo para la respuesta del chat"""

    user_id: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "whatsapp_51987654321",
                "message": "👋 ¡Hola Carlos! Bienvenido...\n\nPor favor selecciona una opción:\n1. FAQ\n2. Registro",
            }
        }


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="ChatBot API Simplificada",
    description="API REST para chatbot que solo maneja user_id y message",
    version="2.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar el motor del chatbot
chatbot = ChatBotEngine("chatbot.json")


# =====================================================
# ENDPOINTS
# =====================================================


@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "message": "ChatBot API Simplificada",
        "version": "2.0",
        "description": "API que solo maneja user_id y message",
        "endpoints": {
            "POST /chat": "Enviar mensaje al chatbot",
            "POST /chat/reset": "Resetear sesión del usuario",
            "GET /health": "Estado de la API",
        },
        "examples": {
            "primer_mensaje": {
                "user_id": "whatsapp_51987654321",
                "message": None,
                "metadata": {"usuarioNombre": "Carlos"},
            },
            "mensaje_normal": {"user_id": "whatsapp_51987654321", "message": "1"},
        },
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal para chat

    **Request:**
    ```json
    {
        "user_id": "whatsapp_51987654321",
        "message": "Hola",
        "metadata": {"usuarioNombre": "Carlos"}  // Solo en primer mensaje
    }
    ```

    **Response:**
    ```json
    {
        "user_id": "whatsapp_51987654321",
        "message": "👋 ¡Hola Carlos!\\n\\nSelecciona una opción:\\n1. FAQ\\n2. Registro"
    }
    ```
    """
    try:
        # Procesar el mensaje
        bot_message = chatbot.process_message(
            user_id=request.user_id,
            user_message=request.message,
            metadata=request.metadata,
        )
        
        return ChatResponse(user_id=request.user_id, message=bot_message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/reset")
async def reset_session(request: Dict[str, str]):
    """
    Resetea la sesión de un usuario

    **Request:**
    ```json
    {
        "user_id": "whatsapp_51987654321"
    }
    ```
    """
    user_id = request.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id es requerido")

    if user_id in chatbot.SESSIONS:
        del chatbot.SESSIONS[user_id]
        return {"message": f"Sesión de {user_id} reseteada correctamente"}
    else:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")


@app.get("/health")
async def health_check():
    """Verifica el estado de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(chatbot.SESSIONS),
    }
