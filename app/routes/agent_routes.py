from fastapi import APIRouter, Depends

from app.controllers.agent_controller import AgentController
from app.contracts.dtos.agent_dtos import AgentRequest, AgentResponse
from app.contracts.services.i_discovery_agent_service import IDiscoveryAgentService
from app.infrastructure.di import get_discovery_agent_service

router = APIRouter(prefix="/agent", tags=["Discovery Agent"])
controller = AgentController()


@router.post("/chat", response_model=AgentResponse)
async def chat(
    request: AgentRequest,
    service: IDiscoveryAgentService = Depends(get_discovery_agent_service)
) -> AgentResponse:

    return await controller.chat(request, service)

