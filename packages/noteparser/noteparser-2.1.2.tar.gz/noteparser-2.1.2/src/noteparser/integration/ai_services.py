"""
AI Services Integration Module

Integrates various AI/ML services into the noteparser workflow.
"""

import logging
from pathlib import Path
from typing import Any

from .service_client import ServiceClientManager

logger = logging.getLogger(__name__)


class AIServicesIntegration:
    """Main integration class for AI services."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.manager = ServiceClientManager()
        self.services_initialized = False

    async def initialize(self) -> bool:
        """Initialize all AI services."""
        if self.services_initialized:
            return True

        logger.info("Initializing AI services...")

        try:
            # Check service health
            health = await self.manager.health_check_all()

            if health.get("ragflow", False):
                logger.info("RagFlow service connected")
            else:
                logger.warning("RagFlow service not available")

            if health.get("deepwiki", False):
                logger.info("DeepWiki service connected")
            else:
                logger.warning("DeepWiki service not available")

            self.services_initialized = True
            logger.info("AI services initialization completed")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AI services: {e}")
            return False

    async def process_document(self, document: dict[str, Any]) -> dict[str, Any]:
        """Process a document through AI services."""
        if not self.services_initialized:
            raise RuntimeError("AI services not initialized")

        results = {}

        # Extract content and metadata
        content = document.get("content", "")
        metadata = document.get("metadata", {})

        # Process through RagFlow for indexing and insights
        try:
            ragflow = self.manager.get_client("ragflow")

            # Index document
            rag_result = await ragflow.post("index", {"content": content, "metadata": metadata})
            results["rag_indexing"] = rag_result

            # Extract insights
            insights = await ragflow.post("extract_insights", {"content": content})
            results["ragflow_insights"] = insights

        except Exception as e:
            logger.exception(f"RagFlow processing failed: {e}")
            results["rag_error"] = {"error": str(e)}

        # Create wiki article
        try:
            deepwiki = self.manager.get_client("deepwiki")

            wiki_result = await deepwiki.post(
                "create_article",
                {
                    "title": metadata.get("title", "Untitled"),
                    "content": content,
                    "metadata": metadata,
                },
            )
            results["deepwiki_article"] = wiki_result

        except Exception as e:
            logger.exception(f"DeepWiki processing failed: {e}")
            results["wiki_error"] = {"error": str(e)}

        return results

    async def query_knowledge(self, query: str, filters: dict | None = None) -> dict[str, Any]:
        """Query the knowledge base."""
        if not self.services_initialized:
            raise RuntimeError("AI services not initialized")

        results = {}

        # Query through RagFlow
        try:
            ragflow = self.manager.get_client("ragflow")
            rag_response = await ragflow.post(
                "query",
                {"query": query, "k": 5, "filters": filters or {}},
            )
            # Extract documents and answer from the response
            results["documents"] = rag_response.get("documents", [])
            results["answer"] = rag_response.get("answer", "")
        except Exception as e:
            logger.exception(f"RagFlow query failed: {e}")
            results["rag_error"] = {"error": str(e)}

        # Query through DeepWiki
        try:
            deepwiki = self.manager.get_client("deepwiki")

            # Search wiki
            wiki_search = await deepwiki.post("search", {"query": query, "limit": 5})
            results["wiki_search"] = wiki_search

            # Ask AI assistant
            ai_response = await deepwiki.post("ask", {"question": query})
            results["ai_assistant"] = ai_response

        except Exception as e:
            logger.exception(f"DeepWiki query failed: {e}")
            results["wiki_error"] = {"error": str(e)}

        return results

    async def organize_knowledge(self) -> dict[str, Any]:
        """Organize and structure the knowledge base."""
        if not self.services_initialized:
            await self.initialize()

        results = {}

        # Get knowledge graph from DeepWiki
        try:
            deepwiki = self.manager.get_client("deepwiki")
            graph_result = await deepwiki.get("graph")
            results["knowledge_graph"] = graph_result
        except Exception as e:
            logger.exception(f"Knowledge graph retrieval failed: {e}")
            results["organization_error"] = {"error": str(e)}

        return results

    async def shutdown(self):
        """Shutdown all services."""
        if self.manager:
            await self.manager.close_all()
            self.services_initialized = False
            logger.info("All AI services connections closed")


# Integration with existing noteparser
def integrate_ai_services(parser_instance):
    """Integrate AI services with noteparser instance."""

    # Create AI services integration
    ai_integration = AIServicesIntegration()

    # Add to parser instance
    parser_instance.ai_services = ai_integration

    # Extend parser methods
    original_parse = parser_instance.parse_to_markdown

    async def enhanced_parse(file_path: str, **kwargs) -> dict[str, Any]:
        """Enhanced parse with AI services."""
        # Original parsing
        result: dict[str, Any] = original_parse(file_path, **kwargs)

        # Process through AI services
        if hasattr(parser_instance, "ai_services"):
            ai_result = await parser_instance.ai_services.process_document(
                {
                    "content": result.get("content", ""),
                    "metadata": {
                        "title": Path(file_path).stem,
                        "file_path": str(file_path),
                        **result.get("metadata", {}),
                    },
                },
            )
            result["ai_processing"] = ai_result

        return result

    parser_instance.parse_to_markdown_with_ai = enhanced_parse

    return parser_instance
