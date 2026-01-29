import os
from typing import Optional
from app.core.redis_state import RedisStateStore
from app.config.settings import settings
from app.persistence.models import ConversationState
from app.config.logging import logger

# Configuración de Redis desde settings
REDIS_URL = settings.REDIS_URL
REDIS_TTL_SECONDS = settings.REDIS_TTL_SECONDS

# Intentar usar Redis, fallback a memoria si no está disponible
_use_redis = settings.USE_REDIS
_redis_store: Optional[RedisStateStore] = None

if _use_redis:
    try:
        _redis_store = RedisStateStore(REDIS_URL, REDIS_TTL_SECONDS)
        logger.debug(f"redis_connected", url=REDIS_URL)
    except Exception as e:
        logger.debug(f"redis_connection_failed", url=REDIS_URL, error=str(e))
        _redis_store = None

# Almacenamiento en memoria como fallback
_state_store: dict[str, ConversationState] = {}


def get_state(conversation_id: str, flow_id: str) -> ConversationState:
    """Obtiene el estado de una conversación."""
    if _redis_store:
        return _redis_store.get_state(conversation_id, flow_id)
    else:
        # Fallback a memoria
        if conversation_id not in _state_store:
            state = ConversationState(conversation_id, flow_id)
            _state_store[conversation_id] = state
        return _state_store[conversation_id]


def save_state(state: ConversationState):
    """Guarda el estado de una conversación."""
    if _redis_store:
        _redis_store.save_state(state)
    else:
        # Fallback a memoria
        _state_store[state.conversation_id] = state


def delete_state(conversation_id: str):
    """Elimina el estado de una conversación."""
    if _redis_store:
        _redis_store.delete_state(conversation_id)
    else:
        # Fallback a memoria
        _state_store.pop(conversation_id, None)


def debug_state_store():
    """Función de debug para ver el estado actual del almacenamiento."""
    if _redis_store:
        conversations = _redis_store.get_all_conversations()
        logger.debug(f"DEBUG: Redis - {len(conversations)} conversaciones activas")
        for conv in conversations:
            logger.debug(f"  - {conv['conversation_id']}: current_node={conv.get('current_node')}, context={conv.get('context')}")
    else:
        logger.debug(f"DEBUG: Memoria - {len(_state_store)} conversaciones activas")
        for conversation_id, state in _state_store.items():
            logger.debug(f"  - {conversation_id}: current_node={state.current_node}, context={state.context}")