from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)
from app.core.config import settings
import uuid

# ------------------------
# CLIENT
# ------------------------
client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key
)


# ------------------------
# COLLECTION PER TENANT
# ------------------------
def get_collection(tenant: str) -> str:
    return f"lms_{tenant}"


# ------------------------
# INIT COLLECTION
# ------------------------
def init_collection(tenant: str, vector_size: int):
    collection_name = get_collection(tenant)

    existing = [
        c.name for c in client.get_collections().collections
    ]

    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )


# ------------------------
# UPSERT VECTOR
# ------------------------
def upsert_vector(tenant: str, vector, payload: dict):
    collection = get_collection(tenant)

    init_collection(tenant, len(vector))

    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={
            **payload,
            "tenant": tenant  # safety layer
        }
    )

    client.upsert(
        collection_name=collection,
        points=[point]
    )


# ------------------------
# SEARCH VECTORS
# ------------------------
def search_vectors(tenant: str, query_vector, top_k=3):
    collection = get_collection(tenant)

    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=top_k
    )

    return [
        {
            "score": r.score,
            "text": r.payload.get("text"),
            "metadata": r.payload.get("metadata", {})
        }
        for r in results
    ]