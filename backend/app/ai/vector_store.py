from dataclasses import dataclass
import hashlib
import math
import re

import chromadb
import numpy as np

from app.core.config import get_settings


@dataclass
class RetrievedChunk:
    text: str
    metadata: dict
    distance: float


class VectorStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = chromadb.PersistentClient(path=self.settings.chroma_path)
        self.collection = self.client.get_or_create_collection(name=self.settings.rag_collection_name)
        self.embedding_model = self._build_embedding_model()

    def _build_embedding_model(self):
        try:
            from sentence_transformers import SentenceTransformer

            return SentenceTransformer(self.settings.embeddings_model)
        except Exception:
            return LightweightEmbeddingModel()

    def add_documents(self, ids: list[str], documents: list[str], metadatas: list[dict]) -> None:
        embeddings = self.embedding_model.encode(documents).tolist()
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    def reset(self) -> None:
        self.client.delete_collection(name=self.settings.rag_collection_name)
        self.collection = self.client.get_or_create_collection(name=self.settings.rag_collection_name)

    def query(self, text: str, top_k: int) -> list[RetrievedChunk]:
        embedding = self.embedding_model.encode([text]).tolist()[0]
        result = self.collection.query(query_embeddings=[embedding], n_results=top_k)
        chunks: list[RetrievedChunk] = []
        for document, metadata, distance in zip(
            result.get("documents", [[]])[0],
            result.get("metadatas", [[]])[0],
            result.get("distances", [[]])[0],
        ):
            chunks.append(RetrievedChunk(text=document, metadata=metadata, distance=distance))
        return chunks


class LightweightEmbeddingModel:
    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def encode(self, texts: list[str] | str) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        return np.array([self._encode_single(text) for text in texts], dtype=np.float32)

    def _encode_single(self, text: str) -> list[float]:
        vector = np.zeros(self.dimensions, dtype=np.float32)
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return vector.tolist()

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], byteorder="big") % self.dimensions
            vector[index] += 1.0

        norm = math.sqrt(float(np.dot(vector, vector)))
        if norm:
            vector = vector / norm
        return vector.tolist()
