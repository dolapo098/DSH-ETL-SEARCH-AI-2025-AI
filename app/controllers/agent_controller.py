from app.contracts.dtos.agent_dtos import AgentRequest, AgentResponse
from app.contracts.services.i_discovery_agent_service import IDiscoveryAgentService


class AgentController:
    """
    Summary: Controller handling conversational discovery agent operations.
    """

    async def chat(
        self,
        request: AgentRequest,
        service: IDiscoveryAgentService
    ) -> AgentResponse:

        return await service.chat(request)

