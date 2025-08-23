import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

from cogents.common.llm import get_llm_client_instructor
from cogents.common.llm.token_tracker import get_token_tracker
from cogents.common.logging import get_logger

from .models import ResearchOutput


class BaseAgent(ABC):
    """
    Base class for all agents with common functionality.

    Provides:
    - LLM client management with instructor support
    - Token usage tracking
    - Logging capabilities
    - Configuration management
    - Error handling patterns
    """

    def __init__(self, llm_provider: str = "openrouter", model_name: Optional[str] = None):
        """Initialize base agent with LLM client and logging."""
        self.logger = get_logger(self.__class__.__name__)
        self.llm_provider = llm_provider
        self.model_name = model_name

        # Initialize LLM client with instructor support
        self.llm = get_llm_client_instructor(provider=llm_provider, chat_model=model_name)

        self.logger.info(f"Initialized {self.__class__.__name__} with {llm_provider} provider")

    def get_token_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive token usage statistics."""
        return get_token_tracker().get_stats()

    def print_token_usage_summary(self):
        """Print a brief structured token usage summary."""
        stats = self.get_token_usage_stats()
        if stats["total_tokens"] > 0:
            print(
                f"FINAL_SUMMARY: {stats['total_tokens']} total | {stats['total_calls']} calls | P:{stats['total_prompt_tokens']} C:{stats['total_completion_tokens']}"
            )
        else:
            print("FINAL_SUMMARY: 0 total | 0 calls | P:0 C:0")

    @abstractmethod
    def run(self, user_message: str, context: Dict[str, Any] = None, config: Optional[RunnableConfig] = None) -> str:
        """Run the agent with a user message and context."""


class BaseGraphicAgent(BaseAgent):
    """
    Base class for agents using LangGraph.

    Provides:
    - LangGraph state management
    - Graph building abstractions
    - Graph export functionality
    - Common graph patterns
    """

    def __init__(self, llm_provider: str = "openrouter", model_name: Optional[str] = None):
        """Initialize graphic agent with graph support."""
        super().__init__(llm_provider, model_name)
        self.graph: Optional[StateGraph] = None

    @abstractmethod
    def _build_graph(self) -> StateGraph:
        """Build the agent's graph. Must be implemented by subclasses."""

    @abstractmethod
    def get_state_class(self) -> Type:
        """Get the state class for this agent's graph."""

    def export_graph(self, output_path: Optional[str] = None, format: str = "png"):
        """
        Export the agent graph visualization to file.

        Args:
            output_path: Optional path for output file. If None, uses default naming.
            format: Export format ('png' or 'mermaid')
        """
        if not self.graph:
            self.logger.warning("No graph to export. Build graph first.")
            return

        if not output_path:
            class_name = self.__class__.__name__.lower()
            output_path = os.path.join(os.path.dirname(__file__), f"{class_name}_graph.{format}")

        try:
            graph_structure = self.graph.get_graph()

            if format == "png":
                try:
                    graph_structure.draw_png(output_path)
                    self.logger.info(f"Graph exported successfully to {output_path}")
                except ImportError:
                    self.logger.warning("pygraphviz not installed, trying mermaid fallback")
                    graph_structure.draw_mermaid_png(output_path)
                    self.logger.info(f"Graph exported with mermaid to {output_path}")
            elif format == "mermaid":
                # For mermaid, we might want to save the mermaid code itself
                mermaid_code = graph_structure.draw_mermaid()
                with open(output_path.replace(".png", ".md"), "w") as f:
                    f.write(f"```mermaid\n{mermaid_code}\n```")
                self.logger.info(f"Mermaid graph exported to {output_path.replace('.png', '.md')}")
            else:
                self.logger.error(f"Unsupported export format: {format}")

        except Exception as e:
            self.logger.error(f"Failed to export graph: {e}")

    def _create_error_response(self, error_message: str, **kwargs) -> Dict[str, Any]:
        """Create a standardized error response."""
        self.logger.error(f"Agent error: {error_message}")
        return {"error": error_message, "success": False, "timestamp": self._now_iso(), **kwargs}

    def _now_iso(self) -> str:
        """Get current time in ISO format."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


class BaseConversationAgent(BaseGraphicAgent):
    """
    Abstract base class for conversation-style agents like AskuraAgent.

    Provides:
    - Session management patterns
    - Message handling abstractions
    - Conversation state management
    - Response generation patterns
    """

    def __init__(self, llm_provider: str = "openrouter", model_name: Optional[str] = None):
        """Initialize conversation agent."""
        super().__init__(llm_provider, model_name)
        self._session_states: Dict[str, Any] = {}

    @abstractmethod
    def start_conversation(self, user_id: str, initial_message: Optional[str] = None) -> Any:
        """Start a new conversation with a user."""

    @abstractmethod
    def process_user_message(self, user_id: str, session_id: str, message: str) -> Any:
        """Process a user message and return the agent's response."""

    def get_session_state(self, session_id: str) -> Optional[Any]:
        """Get the state for a specific session."""
        return self._session_states.get(session_id)

    def list_sessions(self) -> list[str]:
        """List all active session IDs."""
        return list(self._session_states.keys())

    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session."""
        if session_id in self._session_states:
            del self._session_states[session_id]
            self.logger.info(f"Cleared session {session_id}")
            return True
        return False

    def clear_all_sessions(self):
        """Clear all sessions."""
        session_count = len(self._session_states)
        self._session_states.clear()
        self.logger.info(f"Cleared {session_count} sessions")

    @abstractmethod
    def _create_response(self, state: Any) -> Any:
        """Create response from final state. Must be implemented by subclasses."""


class BaseResearcher(BaseGraphicAgent):
    """
    Abstract base class for research-style agents like SeekraAgent.

    Provides:
    - Research workflow patterns
    - Source management
    - Query generation abstractions
    - Result compilation patterns
    """

    def __init__(self, llm_provider: str = "openrouter", model_name: Optional[str] = None):
        """Initialize researcher agent."""
        super().__init__(llm_provider, model_name)

    @abstractmethod
    def research(
        self,
        user_message: str,
        context: Dict[str, Any] = None,
        config: Optional[RunnableConfig] = None,
    ) -> ResearchOutput:
        """Research a topic and return structured results."""

    @abstractmethod
    def get_prompts(self) -> Dict[str, str]:
        """
        Get prompts for the researcher.
        Override this method in subclasses for specialized prompts.
        """

    def preprocess_research_topic(self, research_topic: str) -> str:
        """
        Preprocess research topic before generating queries.
        Can be overridden by subclasses for domain-specific preprocessing.
        """
        return research_topic.strip()

    def format_final_answer(self, final_answer: str, sources: list[Dict[str, Any]]) -> str:
        """
        Format the final research answer.
        Override this method in subclasses for domain-specific formatting.
        """
        return final_answer

    @abstractmethod
    def generate_fallback_queries(self, prompt: str) -> list[str]:
        """
        Generate fallback queries when structured generation fails.
        Must be implemented by subclasses.
        """

    def run(self, user_message: str, context: Dict[str, Any] = None, config: Optional[RunnableConfig] = None) -> str:
        """
        Default implementation of run() for researchers.
        Calls research() and returns the content.
        """
        result = self.research(user_message, context, config)
        return result.content if result else "Research failed to produce results."
