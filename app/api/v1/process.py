from app.config.logging import logger
from app.core.orchestrator import Orchestrator
from app.schemas.webhook_request import WebhookRequest
from app.schemas.webhook_response import WebhookResponse
from fastapi import APIRouter

router = APIRouter()


@router.post("/process", response_model=WebhookResponse)
async def process_webhook(payload: WebhookRequest):
    """
    Process a webhook from external messaging platform.
    El estado conversacional se resuelve internamente usando channel + from.
    """
    logger.info(
        "webhook_received",
        channel=payload.channel,
        from_user=payload.from_,
        message_type=payload.message.type,
        message_content=payload.message.content,
    )
    
    orchestrator = Orchestrator()
    return orchestrator.handle_webhook(payload)