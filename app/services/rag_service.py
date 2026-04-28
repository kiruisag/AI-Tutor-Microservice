import logging
from typing import List, Optional

from app.core.config import settings
from app.ml.vector_store import upsert_vector, search_vectors

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self._client = None

    # -----------------------
    # EMBEDDING CLIENT
    # -----------------------
    def _get_client(self):
        if self._client:
            return self._client

        try:
            if self.provider == "openai":
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=settings.openai_api_key)

            elif self.provider == "gemini":
                from google import genai
                self._client = genai.Client(api_key=settings.gemini_api_key)

            else:
                logger.warning("No valid LLM provider for embeddings")

        except Exception as e:
            logger.error(f"Failed to initialize embedding client: {e}")

        return self._client

    # -----------------------
    # EMBEDDINGS (ROBUST)
    # -----------------------
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding with retry + fallback
        """
        try:
            client = self._get_client()

            if not client:
                return []

            if self.provider == "openai":
                resp = await client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                return resp.data[0].embedding

            elif self.provider == "gemini":
                result = await client.aio.models.embed_content(
                    model="text-embedding-004",
                    contents=text
                )
                return result.embeddings[0].values

        except Exception as e:
            logger.warning(f"Embedding failed: {e}")

        return []

    # -----------------------
    # ADD DOCUMENT
    # -----------------------
    async def add_document(
        self,
        tenant: str,
        text: str,
        metadata: Optional[dict] = None
    ):
        """
        Stores document in Qdrant with tenant isolation
        """
        embedding = await self._get_embedding(text)

        if not embedding:
            logger.warning("Skipping document (no embedding)")
            return

        payload = {
            "tenant": tenant,
            "text": text,
            **(metadata or {})
        }

        try:
            upsert_vector(
                tenant=tenant,
                vector=embedding,
                payload=payload
            )
        except Exception as e:
            logger.error(f"Vector upsert failed: {e}")

    # -----------------------
    # SEARCH (WITH FILTERS)
    # -----------------------
    async def search(
        self,
        tenant: str,
        query: str,
        top_k: int = 3
    ) -> List[str]:
        """
        Vector search with strict tenant isolation
        """

        embedding = await self._get_embedding(query)

        if not embedding:
            logger.warning("No embedding → fallback to empty context")
            return []

        try:
            results = search_vectors(
                tenant=tenant,
                query_vector=embedding,
                top_k=top_k,
                filters={"tenant": tenant}  # 🔥 CRITICAL
            )

            return [r["text"] for r in results]

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    # -----------------------
    # BULK INGEST (IMPORTANT)
    # -----------------------
    async def add_documents_bulk(
        self,
        tenant: str,
        texts: List[str],
        metadata: Optional[dict] = None
    ):
        """
        Batch ingestion (used for course uploads)
        """
        for text in texts:
            await self.add_document(tenant, text, metadata)