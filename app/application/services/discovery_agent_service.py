import logging
from typing import List, Dict, Any, Optional
from app.contracts.services.i_discovery_agent_service import IDiscoveryAgentService
from app.contracts.services.i_semantic_search_service import ISemanticSearchService
from app.contracts.providers.i_llm_provider import ILLMProvider, ExtractionResult
from app.contracts.dtos.agent_dtos import AgentRequest, AgentResponse
from app.domain.value_objects.search_result import SearchQuery

logger = logging.getLogger(__name__)


class DiscoveryAgentService(IDiscoveryAgentService):
    """
    Summary: Orchestrates the dataset discovery pipeline using a single LLM model.
    Phase 1: Intent Extraction (determines if search is needed)
    Phase 2: Semantic Retrieval (existing pipeline)
    Phase 3: Answer Synthesis (generates natural language response)
    """

    INTENT_TEMPLATE = """You are a Coreference Resolution and Intent Specialist.
Given a Conversation History and a New User Message, determine if a search is needed.
If the New Message contains pronouns (e.g., 'those', 'it', 'them'), resolve them using the History.
JSON Schema:
{{
  "is_search_required": boolean,
  "search_query": string or null,
  "reasoning": string
}}
History:
{history}
New Message: "{user_input}"
"""

    SYNTHESIS_PROMPT = """You are a Scientific Data Assistant. You MUST follow these rules:
1. Only answer based on the provided 'Context' and 'Conversation History'.
2. If the context contains datasets, you MUST cite them using the format [ID: file_identifier].
3. If no relevant datasets are in the context, state that clearly.
4. Maintain a professional, objective tone suitable for scientific discovery.

Context:
{context}
"""

    def __init__(
        self,
        semantic_search_service: ISemanticSearchService,
        llm_provider: ILLMProvider
    ):

        self._search = semantic_search_service
        self._llm = llm_provider

    async def chat(self, request: AgentRequest) -> AgentResponse:
        """
        Summary: Handles a conversational request using a single LLM model for intent and synthesis.
        """

        try:
            
            history_str = self._format_history(request.history[-3:])

            intent_prompt = self.INTENT_TEMPLATE.format(
                history=history_str,
                user_input=request.message
            )

            intent: ExtractionResult = await self._llm.extract_intent(intent_prompt)

            context_data = "No relevant datasets found in catalogue."
            related_ids = []

            if intent.is_search_required and intent.search_query:
                
                search_query = SearchQuery(
                    query_text=intent.search_query,
                    limit=3,
                    offset=0
                )

                search_result = await self._search.perform_semantic_context(search_query)

                if search_result.results:
                    
                    related_ids = [r.identifier for r in search_result.results]
                    context_data = self._format_results_for_synthesis(search_result.results)

            synthesis_message = f"User Message: {request.message}\nContext: {context_data}"

            answer = await self._llm.generate_response(
                prompt=synthesis_message,
                system_message=self.SYNTHESIS_PROMPT.format(context=context_data)
            )

            return AgentResponse(
                answer=answer,
                suggested_query=intent.search_query,
                related_identifiers=related_ids
            )

        except Exception as e:
            
            logger.error(f"Discovery Agent Error: {str(e)}")
            
            return AgentResponse(
                answer="I'm sorry, I encountered an issue while retrieving dataset information.",
                related_identifiers=[]
            )

    def _format_history(self, history: List) -> str:
        """
        Summary: Formats conversation history for the LLM prompt.
        """

        return "\n".join([f"{m.role.upper()}: {m.content}" for m in history])

    def _format_results_for_synthesis(self, results: List) -> str:
        """
        Summary: Formats search results for grounding the synthesis model.
        """

        items = []

        for r in results:
            
            items.append(f"- ID: {r.identifier} | Title: {r.title} | Abstract: {r.description}")

        return "\n".join(items)
