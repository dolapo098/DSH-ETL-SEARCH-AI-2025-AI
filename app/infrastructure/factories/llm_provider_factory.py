import os
import logging
from typing import Dict, Type, Any, Optional
from app.contracts.providers.i_llm_provider import ILLMProvider
from app.infrastructure.providers.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    Summary: Factory for creating LLM provider instances.
    Maintains clean architecture by abstracting concrete provider creation.
    Exclusively supports Gemini for high-performance cloud inference.
    """

    DEFAULT_MODEL = "gemini-flash-latest"
    MODEL_ENV_VAR = "LLM_MODEL"
    API_KEY_ENV_VAR = "GEMINI_API_KEY"

    _registry: Dict[str, Type[ILLMProvider]] = {}
    _initialized: bool = False

    @classmethod
    def _initialize_registry(cls) -> None:
        """
        Summary: Initializes the provider registry with the Gemini provider.
        """
        
        if cls._initialized:
            
            return

        try:
            
            cls._registry["gemini"] = GeminiProvider
            logger.debug("Registered GeminiProvider")

        except ImportError as e:
            
            logger.error(f"GeminiProvider not available: {e}")

        cls._initialized = True

    @classmethod
    def create(
        cls,
        provider_type: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs: Any
    ) -> ILLMProvider:
        """
        Summary: Creates an LLM provider instance.
        Defaults to Gemini as the exclusive high-performance cloud provider.
        
        Args:
            provider_type: Ignored (reserved for future multi-provider support)
            model_name: Specific Gemini model name (defaults to gemini-flash-latest)
            api_key: Optional API key override
            **kwargs: Additional configuration
            
        Returns:
            An instance of GeminiProvider
        """
        
        cls._initialize_registry()
        
        # We now exclusively use Gemini
        model_name = model_name or os.getenv(cls.MODEL_ENV_VAR, cls.DEFAULT_MODEL)
        api_key = api_key or os.getenv(cls.API_KEY_ENV_VAR)
        
        provider_class = cls._registry.get("gemini")
        
        if not provider_class:
            
            raise RuntimeError("GeminiProvider registration failed. Check infrastructure logs.")
            
        logger.info(f"Creating Gemini provider with model: {model_name}")
        
        return provider_class(model_name=model_name, api_key=api_key)
