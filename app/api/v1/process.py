from app.core.orchestrator import Orchestrator
from app.schemas.request import AgentRequest
from app.schemas.response import AgentResponse
from fastapi import APIRouter

router = APIRouter()


@router.post("/process", response_model=AgentResponse)
async def process_message(payload=AgentRequest):
    orchestrator = Orchestrator()
    return orchestrator.handle(payload)
