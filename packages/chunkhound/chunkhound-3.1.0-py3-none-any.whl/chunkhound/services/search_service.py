"""Search service for ChunkHound - handles semantic and regex search operations."""

import asyncio
from pathlib import Path
from typing import Any

from loguru import logger

from chunkhound.core.types.common import ChunkId
from chunkhound.interfaces.database_provider import DatabaseProvider
from chunkhound.interfaces.embedding_provider import EmbeddingProvider

from .base_service import BaseService


class SearchService(BaseService):
    """Service for performing semantic and regex searches across indexed code."""

    def __init__(
        self,
        database_provider: DatabaseProvider,
        embedding_provider: EmbeddingProvider | None = None,
    ):
        """Initialize search service.

        Args:
            database_provider: Database provider for data access
            embedding_provider: Optional embedding provider for semantic search
        """
        super().__init__(database_provider)
        self._embedding_provider = embedding_provider

    async def search_semantic(
        self,
        query: str,
        page_size: int = 10,
        offset: int = 0,
        threshold: float | None = None,
        provider: str | None = None,
        model: str | None = None,
        path_filter: str | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Perform semantic search using vector similarity.
        
        Automatically selects the best search strategy:
        - Two-hop + reranking if provider supports reranking
        - Standard single-hop otherwise

        Args:
            query: Natural language search query
            page_size: Number of results per page
            offset: Starting position for pagination
            threshold: Optional similarity threshold to filter results
            provider: Optional specific embedding provider to use
            model: Optional specific model to use
            path_filter: Optional relative path to limit search scope (e.g., 'src/', 'tests/')

        Returns:
            Tuple of (results, pagination_metadata)
        """
        try:
            if not self._embedding_provider:
                raise ValueError(
                    "Embedding provider not configured for semantic search"
                )

            # Type narrowing for mypy
            embedding_provider = self._embedding_provider
            
            # Use provided provider/model or fall back to configured defaults
            search_provider = provider or embedding_provider.name
            search_model = model or embedding_provider.model

            # Choose search strategy based on provider capabilities
            if hasattr(embedding_provider, 'supports_reranking') and embedding_provider.supports_reranking():
                logger.debug(f"Using two-hop search with reranking for: '{query}'")
                return await self._search_semantic_two_hop(
                    query=query,
                    page_size=page_size,
                    offset=offset,
                    threshold=threshold,
                    provider=search_provider,
                    model=search_model,
                    path_filter=path_filter,
                )
            else:
                logger.debug(f"Using standard semantic search for: '{query}'")
                return await self._search_semantic_standard(
                    query=query,
                    page_size=page_size,
                    offset=offset,
                    threshold=threshold,
                    provider=search_provider,
                    model=search_model,
                    path_filter=path_filter,
                )

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            raise

    async def _search_semantic_standard(
        self,
        query: str,
        page_size: int,
        offset: int,
        threshold: float | None,
        provider: str,
        model: str,
        path_filter: str | None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Standard single-hop semantic search implementation."""
        if not self._embedding_provider:
            raise ValueError("Embedding provider not configured")
        
        # Generate query embedding
        query_results = await self._embedding_provider.embed([query])
        if not query_results:
            return [], {}

        query_vector = query_results[0]

        # Perform vector similarity search
        results, pagination = self._db.search_semantic(
            query_embedding=query_vector,
            provider=provider,
            model=model,
            page_size=page_size,
            offset=offset,
            threshold=threshold,
            path_filter=path_filter,
        )

        # Enhance results with additional metadata
        enhanced_results = []
        for result in results:
            enhanced_result = self._enhance_search_result(result)
            enhanced_results.append(enhanced_result)

        logger.info(
            f"Standard semantic search completed: {len(enhanced_results)} results found"
        )
        return enhanced_results, pagination

    async def _search_semantic_two_hop(
        self,
        query: str,
        page_size: int,
        offset: int,
        threshold: float | None,
        provider: str,
        model: str,
        path_filter: str | None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Two-hop semantic search with reranking implementation."""
        # Step 1: Get more initial candidates (2-3x final limit)
        initial_limit = min(page_size * 3, 100)  # Cap at 100 for performance
        first_hop_results, _ = await self._search_semantic_standard(
            query=query,
            page_size=initial_limit,
            offset=0,  # Always start from beginning for two-hop
            threshold=0.0,  # No threshold filtering for first hop
            provider=provider,
            model=model,
            path_filter=path_filter,
        )

        if len(first_hop_results) <= 10:
            # Not enough results for expansion, fall back to standard search
            logger.debug("Not enough results for two-hop expansion, using standard search")
            return await self._search_semantic_standard(
                query=query,
                page_size=page_size,
                offset=offset,
                threshold=threshold,
                provider=provider,
                model=model,
                path_filter=path_filter,
            )

        # Step 2: Expand top 10 results to find semantic neighbors
        top_candidates = first_hop_results[:10]
        expanded_results = list(first_hop_results)  # Start with original results

        for candidate in top_candidates:
            try:
                neighbors = self._db.find_similar_chunks(
                    chunk_id=candidate["chunk_id"],
                    provider=provider,
                    model=model,
                    limit=10,
                    threshold=None,  # No threshold for neighbor expansion
                )
                expanded_results.extend(self._enhance_search_result(n) for n in neighbors)
            except Exception as e:
                logger.warning(f"Failed to find neighbors for chunk {candidate['chunk_id']}: {e}")

        # Step 3: Deduplicate by chunk_id
        unique_results = []
        seen_chunk_ids = set()
        for result in expanded_results:
            chunk_id = result["chunk_id"]
            if chunk_id not in seen_chunk_ids:
                unique_results.append(result)
                seen_chunk_ids.add(chunk_id)

        # Step 4: Rerank all results against original query
        if len(unique_results) > page_size:
            try:
                documents = [result["content"] for result in unique_results]
                # Type narrowing: we know provider has rerank if we're in two-hop
                assert self._embedding_provider is not None
                assert hasattr(self._embedding_provider, 'rerank')
                rerank_results = await self._embedding_provider.rerank(
                    query=query,
                    documents=documents,
                    top_k=page_size * 2,  # Get extra candidates before threshold filtering
                )

                # Apply reranking scores
                for rerank_result in rerank_results:
                    if rerank_result.index < len(unique_results):
                        unique_results[rerank_result.index]["score"] = rerank_result.score

                # Sort by rerank score (highest first)
                unique_results = sorted(
                    unique_results, key=lambda x: x.get("score", 0.0), reverse=True
                )
            except Exception as e:
                logger.warning(f"Reranking failed, using original order: {e}")

        # Step 5: Apply threshold and pagination
        if threshold is not None:
            unique_results = [r for r in unique_results if r.get("score", 1.0) >= threshold]

        # Apply pagination
        total_results = len(unique_results)
        paginated_results = unique_results[offset : offset + page_size]

        pagination = {
            "offset": offset,
            "page_size": page_size,
            "has_more": offset + page_size < total_results,
            "next_offset": offset + page_size if offset + page_size < total_results else None,
            "total": total_results,
        }

        logger.info(
            f"Two-hop semantic search completed: {len(paginated_results)} results returned "
            f"({total_results} total candidates)"
        )
        return paginated_results, pagination

    def search_regex(
        self,
        pattern: str,
        page_size: int = 10,
        offset: int = 0,
        path_filter: str | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Perform regex search on code content.

        Args:
            pattern: Regular expression pattern to search for
            page_size: Number of results per page
            offset: Starting position for pagination
            path_filter: Optional relative path to limit search scope (e.g., 'src/', 'tests/')

        Returns:
            Tuple of (results, pagination_metadata)
        """
        try:
            logger.debug(f"Performing regex search for pattern: '{pattern}'")

            # Perform regex search
            results, pagination = self._db.search_regex(
                pattern=pattern,
                page_size=page_size,
                offset=offset,
                path_filter=path_filter,
            )

            # Enhance results with additional metadata
            enhanced_results = []
            for result in results:
                enhanced_result = self._enhance_search_result(result)
                enhanced_results.append(enhanced_result)

            logger.info(
                f"Regex search completed: {len(enhanced_results)} results found"
            )
            return enhanced_results, pagination

        except Exception as e:
            logger.error(f"Regex search failed: {e}")
            raise

    async def search_hybrid(
        self,
        query: str,
        regex_pattern: str | None = None,
        page_size: int = 10,
        offset: int = 0,
        semantic_weight: float = 0.7,
        threshold: float | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Perform hybrid search combining semantic and regex results.

        Args:
            query: Natural language search query
            regex_pattern: Optional regex pattern to include in search
            page_size: Number of results per page
            offset: Starting position for pagination
            semantic_weight: Weight given to semantic results (0.0-1.0)
            threshold: Optional similarity threshold for semantic results

        Returns:
            Tuple of (results, pagination_metadata)
        """
        try:
            logger.debug(
                f"Performing hybrid search: query='{query}', pattern='{regex_pattern}'"
            )

            # Perform searches concurrently
            tasks = []

            # Semantic search
            if self._embedding_provider:
                semantic_task = asyncio.create_task(
                    self.search_semantic(
                        query,
                        page_size=page_size * 2,
                        offset=offset,
                        threshold=threshold,
                    )
                )
                tasks.append(("semantic", semantic_task))

            # Regex search
            if regex_pattern:

                async def get_regex_results() -> tuple[list[dict[str, Any]], dict[str, Any]]:
                    return self.search_regex(
                        regex_pattern, page_size=page_size * 2, offset=offset
                    )

                tasks.append(("regex", asyncio.create_task(get_regex_results())))

            # Wait for all searches to complete
            results_by_type = {}
            pagination_data = {}
            for search_type, task in tasks:
                results, pagination = await task
                results_by_type[search_type] = results
                pagination_data[search_type] = pagination

            # Combine and rank results
            combined_results = self._combine_search_results(
                semantic_results=results_by_type.get("semantic", []),
                regex_results=results_by_type.get("regex", []),
                semantic_weight=semantic_weight,
                limit=page_size,
            )

            # Create combined pagination metadata
            combined_pagination = {
                "offset": offset,
                "page_size": page_size,
                "has_more": len(combined_results) == page_size,
                "next_offset": offset + page_size
                if len(combined_results) == page_size
                else None,
                "total": None,  # Cannot estimate for hybrid search
            }

            logger.info(
                f"Hybrid search completed: {len(combined_results)} results found"
            )
            return combined_results, combined_pagination

        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            raise

    def get_chunk_context(
        self, chunk_id: ChunkId, context_lines: int = 5
    ) -> dict[str, Any]:
        """Get additional context around a specific chunk.

        Args:
            chunk_id: ID of the chunk to get context for
            context_lines: Number of lines before/after to include

        Returns:
            Dictionary with chunk details and surrounding context
        """
        try:
            # Get chunk details
            chunk_query = """
                SELECT c.*, f.path, f.language
                FROM chunks c
                JOIN files f ON c.file_id = f.id
                WHERE c.id = ?
            """
            chunk_results = self._db.execute_query(chunk_query, [chunk_id])

            if not chunk_results:
                return {}

            chunk = chunk_results[0]

            # Get surrounding chunks for context
            context_query = """
                SELECT symbol, start_line, end_line, code, chunk_type
                FROM chunks
                WHERE file_id = ?
                AND (
                    (start_line BETWEEN ? AND ?) OR
                    (end_line BETWEEN ? AND ?) OR
                    (start_line <= ? AND end_line >= ?)
                )
                ORDER BY start_line
            """

            start_context = max(1, chunk["start_line"] - context_lines)
            end_context = chunk["end_line"] + context_lines

            context_results = self._db.execute_query(
                context_query,
                [
                    chunk["file_id"],
                    start_context,
                    end_context,
                    start_context,
                    end_context,
                    start_context,
                    end_context,
                ],
            )

            return {
                "chunk": chunk,
                "context": context_results,
                "file_path": chunk["path"],
                "language": chunk["language"],
            }

        except Exception as e:
            logger.error(f"Failed to get chunk context for {chunk_id}: {e}")
            return {}

    def get_file_chunks(self, file_path: str) -> list[dict[str, Any]]:
        """Get all chunks for a specific file.

        Args:
            file_path: Path to the file

        Returns:
            List of chunks in the file ordered by line number
        """
        try:
            query = """
                SELECT c.*, f.language
                FROM chunks c
                JOIN files f ON c.file_id = f.id
                WHERE f.path = ?
                ORDER BY c.start_line
            """

            results = self._db.execute_query(query, [file_path])

            # Enhance results
            enhanced_results = []
            for result in results:
                enhanced_result = self._enhance_search_result(result)
                enhanced_results.append(enhanced_result)

            return enhanced_results

        except Exception as e:
            logger.error(f"Failed to get chunks for file {file_path}: {e}")
            return []

    def _enhance_search_result(self, result: dict[str, Any]) -> dict[str, Any]:
        """Enhance search result with additional metadata and formatting.

        Args:
            result: Raw search result from database

        Returns:
            Enhanced result with additional metadata
        """
        enhanced = result.copy()

        # Add computed fields
        if "start_line" in result and "end_line" in result:
            enhanced["line_count"] = result["end_line"] - result["start_line"] + 1

        # Add code preview (truncated if too long)
        if "code" in result and result["code"]:
            code = result["code"]
            if len(code) > 500:
                enhanced["code_preview"] = code[:500] + "..."
                enhanced["is_truncated"] = True
            else:
                enhanced["code_preview"] = code
                enhanced["is_truncated"] = False

        # Add file extension for quick language identification
        if "path" in result:
            file_path = result["path"]
            enhanced["file_extension"] = Path(file_path).suffix.lower()

        # Format similarity score if present
        if "similarity" in result:
            enhanced["similarity_percentage"] = round(result["similarity"] * 100, 2)

        return enhanced

    def _combine_search_results(
        self,
        semantic_results: list[dict[str, Any]],
        regex_results: list[dict[str, Any]],
        semantic_weight: float,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Combine semantic and regex search results with weighted ranking.

        Args:
            semantic_results: Results from semantic search
            regex_results: Results from regex search
            semantic_weight: Weight for semantic results (0.0-1.0)
            limit: Maximum number of results to return

        Returns:
            Combined and ranked results
        """
        combined = {}
        regex_weight = 1.0 - semantic_weight

        # Process semantic results
        for i, result in enumerate(semantic_results):
            chunk_id = result.get("chunk_id") or result.get("id")
            if chunk_id:
                # Score based on position and similarity
                position_score = (len(semantic_results) - i) / len(semantic_results)
                similarity_score = result.get("similarity", 0.5)
                score = (
                    position_score * 0.3 + similarity_score * 0.7
                ) * semantic_weight

                combined[chunk_id] = {
                    **result,
                    "search_type": "semantic",
                    "combined_score": score,
                    "semantic_score": similarity_score,
                }

        # Process regex results
        for i, result in enumerate(regex_results):
            chunk_id = result.get("chunk_id") or result.get("id")
            if chunk_id:
                # Score based on position (regex has no similarity score)
                position_score = (len(regex_results) - i) / len(regex_results)
                score = position_score * regex_weight

                if chunk_id in combined:
                    # Boost existing result
                    combined[chunk_id]["combined_score"] += score
                    combined[chunk_id]["search_type"] = "hybrid"
                    combined[chunk_id]["regex_score"] = position_score
                else:
                    combined[chunk_id] = {
                        **result,
                        "search_type": "regex",
                        "combined_score": score,
                        "regex_score": position_score,
                    }

        # Sort by combined score and return top results
        sorted_results = sorted(
            combined.values(), key=lambda x: x["combined_score"], reverse=True
        )

        return sorted_results[:limit]
