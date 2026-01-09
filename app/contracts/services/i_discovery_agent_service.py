from abc import ABC, abstractmethod
from app.contracts.dtos.agent_dtos import AgentRequest, AgentResponse

class IDiscoveryAgentService(ABC):
    """
    Summary: Contract for the dataset discovery conversational agent.
    """

    @abstractmethod
    async def chat(self, request: AgentRequest) -> AgentResponse:
        """
        Summary: Processes a user message and returns a discovery-focused response.
        """

        pass

