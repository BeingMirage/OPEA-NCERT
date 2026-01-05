"""ChromaDB vector store configuration and helper utilities.

This module replaces the previous Milvus dependency with a pure-Python
Chroma setup so the OPEA RAG pipeline can run without Docker.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

import chromadb
from chromadb.api.models.Collection import Collection
from loguru import logger


class ChromaVectorDB:
    """Lightweight wrapper around a persistent ChromaDB collection."""

    def __init__(self,
                 persist_directory: str = "chroma_db",
                 collection_name: str = "ncert_chunks") -> None:
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.client: Optional[chromadb.PersistentClient] = None
        self.collection: Optional[Collection] = None

    # ------------------------------------------------------------------
    # Connection & collection management
    # ------------------------------------------------------------------
    def connect(self) -> bool:
        """Create a persistent Chroma client and ensure storage exists."""
        try:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("✓ Chroma vector store ready")
            return True
        except Exception as exc:  # pragma: no cover - informative logging
            logger.error(f"✗ Failed to initialize ChromaDB: {exc}")
            return False

    def create_collection(self, recreate: bool = False) -> bool:
        """Ensure the collection exists; optionally recreate it."""
        if not self.client:
            logger.error("Chroma client not initialized. Call connect() first.")
            return False

        try:
            if recreate:
                try:
                    self.client.delete_collection(name=self.collection_name)
                    logger.info(f"Cleared existing collection '{self.collection_name}'")
                except Exception as exc:
                    logger.warning(f"Collection removal skipped: {exc}")

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"✓ Collection ready: {self.collection_name}")
            return True
        except Exception as exc:
            logger.error(f"✗ Failed to prepare Chroma collection: {exc}")
            return False

    # ------------------------------------------------------------------
    # Data operations
    # ------------------------------------------------------------------
    def insert_chunks(self, chunks: List[Dict]) -> int:
        """Insert embedded chunks into the Chroma collection."""
        if not chunks:
            logger.warning("No chunks provided for insertion")
            return 0
        if not self.collection:
            logger.error("Chroma collection not initialized")
            return 0

        ids: List[str] = []
        embeddings: List[List[float]] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Optional[str]]] = []

        for chunk in chunks:
            embedding = chunk.get("embedding")
            if embedding is None:
                continue

            chunk_id = str(chunk.get("chunk_id") or uuid4())
            ids.append(chunk_id)
            embeddings.append(embedding)
            documents.append(chunk.get("text", ""))

            metadata = {
                key: value
                for key, value in {
                    "grade": str(chunk.get("grade")) if chunk.get("grade") else None,
                    "subject": chunk.get("subject"),
                    "source_file": chunk.get("source_file"),
                    "language": chunk.get("language"),
                    "element_type": chunk.get("element_type"),
                }.items()
                if value is not None
            }
            metadatas.append(metadata)

        if not ids:
            logger.warning("No embeddings available for insertion")
            return 0

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )
        logger.info(f"✓ Inserted {len(ids)} chunks into Chroma")
        return len(ids)

    def search_similar(self,
                        query_embedding: List[float],
                        grade: Optional[str] = None,
                        subject: Optional[str] = None,
                        limit: int = 5) -> List[Dict]:
        """Search similar chunks with optional metadata filtering."""
        if not self.collection:
            logger.error("Chroma collection not initialized")
            return []

        where: Dict[str, str] = {}
        if grade:
            where["grade"] = str(grade)
        if subject:
            where["subject"] = subject

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where or None,
                include=["metadatas", "documents", "distances", "ids"],
            )
        except Exception as exc:
            logger.error(f"Chroma query failed: {exc}")
            return []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        formatted: List[Dict] = []
        for idx, doc, metadata, distance in zip(ids, documents, metadatas, distances):
            metadata = metadata or {}
            formatted.append({
                "chunk_id": idx,
                "text": doc,
                "grade": metadata.get("grade"),
                "subject": metadata.get("subject"),
                "source_file": metadata.get("source_file"),
                "language": metadata.get("language"),
                "element_type": metadata.get("element_type"),
                "score": 1 - float(distance) if distance is not None else None,
            })

        return formatted

    def get_collection_info(self) -> Dict:
        """Return collection metadata for logging/testing."""
        count = self.collection.count() if self.collection else 0
        return {
            "name": self.collection_name,
            "num_entities": count,
            "persist_directory": str(self.persist_directory),
            "fields": [
                "chunk_id", "embedding", "text",
                "grade", "subject", "source_file", "language", "element_type",
            ],
        }


def setup_chroma(persist_directory: str = "chroma_db",
                 collection_name: str = "ncert_chunks",
                 recreate: bool = False) -> Optional[ChromaVectorDB]:
    """Helper used by setup.py/tests to provision the vector store."""
    db = ChromaVectorDB(persist_directory=persist_directory,
                        collection_name=collection_name)

    if not db.connect():
        return None

    if not db.create_collection(recreate=recreate):
        return None

    info = db.get_collection_info()
    logger.info(f"✓ Chroma ready: {info}")
    return db


# ------------------------------------------------------------------
# Backwards compatibility exports (legacy Milvus naming)
# ------------------------------------------------------------------

MilvusVectorDB = ChromaVectorDB


def setup_milvus(*args, **kwargs):
    """Deprecated helper maintained for backward compatibility."""
    logger.warning(
        "setup_milvus() is deprecated; use setup_chroma() instead. Proceeding with Chroma backend."
    )
    return setup_chroma(*args, **kwargs)
