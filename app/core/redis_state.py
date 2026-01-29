import json
import redis
from typing import Optional
from app.persistence.models import ConversationState


class RedisStateStore:
    """Almacenamiento de estado usando Redis para persistencia y escalabilidad."""

    def __init__(
        self, redis_url: str = "redis://localhost:6379/0", ttl_seconds: int = 3600
    ):
        """
        Inicializa el almacenamiento Redis.

        Args:
            redis_url: URL de conexión a Redis
            ttl_seconds: Tiempo de vida de las conversaciones en segundos (default: 1 hora)
        """
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.ttl_seconds = ttl_seconds
        self._test_connection()

    def _test_connection(self):
        """Prueba la conexión a Redis."""
        try:
            self.redis_client.ping()
        except redis.ConnectionError as e:
            logger.info("using_memory_store")
            raise

    def _get_key(self, conversation_id: str) -> str:
        """Genera la clave Redis para una conversación."""
        return f"conversation:{conversation_id}"

    def get_state(self, conversation_id: str, flow_id: str) -> ConversationState:
        """
        Obtiene el estado de una conversación desde Redis.
        Si no existe, crea uno nuevo.
        """
        key = self._get_key(conversation_id)

        try:
            data = self.redis_client.get(key)
            if data:
                # Deserializar el estado
                state_data = json.loads(data)
                state = ConversationState(conversation_id, flow_id)
                state.current_node = state_data.get("current_node")
                state.context = state_data.get("context", {})
                return state
        except (json.JSONDecodeError, redis.RedisError) as e:
            print(f"⚠️  Error leyendo de Redis: {e}")

        # Si no existe o hay error, crear nuevo estado
        return ConversationState(conversation_id, flow_id)

    def save_state(self, state: ConversationState):
        """Guarda el estado en Redis con TTL."""
        key = self._get_key(state.conversation_id)

        try:
            data = {
                "conversation_id": state.conversation_id,
                "flow_id": state.flow_id,
                "current_node": state.current_node,
                "context": state.context,
            }

            # Guardar con TTL
            self.redis_client.setex(key, self.ttl_seconds, json.dumps(data))
        except redis.RedisError as e:
            print(f"⚠️  Error guardando en Redis: {e}")

    def delete_state(self, conversation_id: str):
        """Elimina el estado de una conversación."""
        try:
            key = self._get_key(conversation_id)
            self.redis_client.delete(key)
        except redis.RedisError as e:
            print(f"⚠️  Error eliminando de Redis: {e}")

    def get_all_conversations(self) -> list:
        """Obtiene todas las conversaciones activas (para debug/admin)."""
        try:
            keys = self.redis_client.keys("conversation:*")
            conversations = []
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    conversations.append(json.loads(data))
            return conversations
        except redis.RedisError as e:
            print(f"⚠️  Error obteniendo conversaciones: {e}")
            return []
