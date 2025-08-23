"""
FAISS vector store implementation for in-memory similarity search.
"""

import asyncio
import logging
import pickle
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

try:
    import faiss
except ImportError:
    faiss = None

from .base import BaseVectorStore, SearchResult

logger = logging.getLogger(__name__)


class FAISSVectorStore(BaseVectorStore):
    """FAISS-based vector store for efficient similarity search.

    Supports multiple index types:
    - flat: Exact search (brute force)
    - ivf: Inverted file index for large datasets
    - hnsw: Hierarchical Navigable Small World for fast approximate search
    """

    def __init__(
        self, dimension: int, index_type: str = "flat", metric: str = "cosine", **index_params
    ):
        """Initialize FAISS vector store.

        Args:
            dimension: Dimension of vectors
            index_type: Type of index (flat, ivf, hnsw)
            metric: Distance metric (cosine, l2, inner_product)
            **index_params: Additional parameters for index construction
        """
        if faiss is None:
            raise ImportError("FAISS is not installed. Install with: pip install faiss-cpu")

        super().__init__(dimension, index_type)
        self.metric = metric
        self.index_params = index_params

        # Create index
        self.index = self._create_index()

        # Storage for texts and metadata
        self.texts: dict[str, str] = {}
        self.metadata: dict[str, dict[str, Any]] = {}
        self.id_to_idx: dict[str, int] = {}
        self.idx_to_id: dict[int, str] = {}

        # Cache invalidation metadata
        self.index_created_at: str | None = None
        self.indexed_files: dict[str, dict[str, Any]] = {}

    def _create_index(self) -> Any:
        """Create FAISS index based on configuration."""
        # Normalize vectors for cosine similarity
        if self.metric == "cosine":
            index = faiss.IndexFlatIP(self.dimension)
            index = faiss.IndexIDMap(index)
        elif self.metric == "l2":
            index = faiss.IndexFlatL2(self.dimension)
            index = faiss.IndexIDMap(index)
        elif self.metric == "inner_product":
            index = faiss.IndexFlatIP(self.dimension)
            index = faiss.IndexIDMap(index)
        else:
            raise ValueError(f"Unknown metric: {self.metric}")

        # Apply index type modifications
        if self.index_type == "ivf":
            # Inverted file index
            nlist = self.index_params.get("nlist", 100)
            quantizer = faiss.IndexFlatL2(self.dimension)
            index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            index = faiss.IndexIDMap(index)

        elif self.index_type == "hnsw":
            # HNSW index
            m_param = self.index_params.get("M", 32)
            ef_construction = self.index_params.get("ef_construction", 200)
            index = faiss.IndexHNSWFlat(self.dimension, m_param)
            index.hnsw.efConstruction = ef_construction
            index = faiss.IndexIDMap(index)

        return index

    def _normalize_embeddings(self, embeddings: list[np.ndarray]) -> np.ndarray:
        """Normalize embeddings for cosine similarity."""
        embeddings_array = np.array(embeddings).astype("float32")

        if self.metric == "cosine":
            # Normalize for cosine similarity
            norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
            embeddings_array = embeddings_array / (norms + 1e-10)

        return embeddings_array

    async def add_vectors(
        self,
        texts: list[str],
        embeddings: list[np.ndarray],
        ids: list[str] | None = None,
        metadata: list[dict[str, Any]] | None = None,
    ) -> list[str]:
        """Add vectors to the FAISS index."""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]

        if metadata is None:
            metadata = [{} for _ in texts]

        # Normalize embeddings
        embeddings_array = self._normalize_embeddings(embeddings)

        # Get current index size
        current_size = self.index.ntotal

        # Create indices for new vectors
        indices = np.arange(current_size, current_size + len(texts), dtype=np.int64)

        # Add to index
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.index.add_with_ids(embeddings_array, indices)
        )

        # Store associated data
        for i, (id_, text, meta) in enumerate(zip(ids, texts, metadata, strict=False)):
            idx = current_size + i
            self.texts[id_] = text
            self.metadata[id_] = meta
            self.id_to_idx[id_] = idx
            self.idx_to_id[idx] = id_

        return ids

    async def remove_vector(self, id_: str) -> bool:
        """Remove a vector from the index by ID.

        Args:
            id_: The ID of the vector to remove

        Returns:
            True if removed successfully, False if ID not found
        """
        if id_ not in self.id_to_idx:
            return False

        # Get the index and file path before removing
        idx = self.id_to_idx[id_]
        removed_chunk_metadata = self.metadata.get(id_, {})
        removed_file_path = None
        if isinstance(removed_chunk_metadata, dict):
            removed_file_path = removed_chunk_metadata.get("file_path")

        # Note: FAISS doesn't support direct removal of vectors from IndexIDMap
        # The vector will remain in the index but we remove it from our mappings
        # This is a limitation of FAISS flat indexes

        # Remove from our mappings
        del self.texts[id_]
        del self.metadata[id_]
        del self.id_to_idx[id_]
        del self.idx_to_id[idx]

        # Update indexed_files if this was the last chunk for a file
        if hasattr(self, "indexed_files") and removed_file_path:
            # Check if there are any remaining chunks for this file
            remaining_chunks = any(
                isinstance(meta, dict) and meta.get("file_path") == removed_file_path
                for chunk_id, meta in self.metadata.items()
            )

            # If no remaining chunks, remove from indexed_files
            if not remaining_chunks and removed_file_path in self.indexed_files:
                del self.indexed_files[removed_file_path]

        return True

    async def search(
        self, query_embedding: np.ndarray, k: int = 10, filter: dict[str, Any] | None = None
    ) -> list[SearchResult]:
        """Search for similar vectors in the index."""
        # Normalize query
        query_array = self._normalize_embeddings([query_embedding])

        # Search (ensure k is at least 1 and not more than total items)
        # If index is empty, search_k will be 0 which FAISS doesn't allow, so we need min 1
        if self.index.ntotal == 0:
            # Can't search empty index, return empty results
            return []
        search_k = max(1, min(k * 2, self.index.ntotal))
        distances, indices = await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.index.search(query_array, search_k)
        )

        # Convert to results
        results = []
        for dist, idx in zip(distances[0], indices[0], strict=False):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue

            id_ = self.idx_to_id.get(int(idx))
            if id_ is None:
                continue

            # Apply filter if provided
            if filter:
                meta = self.metadata.get(id_, {})
                if not all(meta.get(k) == v for k, v in filter.items()):
                    continue

            # Convert distance to similarity score
            if self.metric == "cosine":
                score = float(dist)  # Already similarity for inner product
            elif self.metric == "l2":
                score = 1.0 / (1.0 + float(dist))  # Convert distance to similarity
            else:
                score = float(dist)

            results.append(
                SearchResult(
                    id=id_, text=self.texts[id_], score=score, metadata=self.metadata.get(id_)
                )
            )

            if len(results) >= k:
                break

        return results

    async def delete_vectors(self, ids: list[str]) -> int:
        """Delete vectors from the index."""
        # FAISS doesn't support deletion directly
        # We need to rebuild the index without the deleted vectors

        # Get all current data except deleted ones
        remaining_ids = []
        remaining_texts = []

        for id_, _idx in self.id_to_idx.items():
            if id_ not in ids:
                remaining_ids.append(id_)
                remaining_texts.append(self.texts[id_])
                # Note: We can't recover embeddings from FAISS directly
                # This is a limitation of this implementation

        logger.warning(
            "FAISS delete requires index rebuild. "
            "Consider using a different vector store for frequent deletions."
        )

        # Clear and rebuild
        deleted_count = len(ids)
        await self.clear()

        # Note: Without stored embeddings, we can't fully rebuild
        # This is a known limitation

        return deleted_count

    async def update_vectors(
        self,
        ids: list[str],
        embeddings: list[np.ndarray] | None = None,
        texts: list[str] | None = None,
        metadata: list[dict[str, Any]] | None = None,
    ) -> int:
        """Update existing vectors."""
        updated_count = 0

        for i, id_ in enumerate(ids):
            if id_ not in self.id_to_idx:
                continue

            if texts and i < len(texts):
                self.texts[id_] = texts[i]

            if metadata and i < len(metadata):
                self.metadata[id_] = metadata[i]

            if embeddings and i < len(embeddings):
                # Update embedding in index
                self.id_to_idx[id_]
                self._normalize_embeddings([embeddings[i]])

                # FAISS doesn't support direct update either
                # This is a simplified approach
                logger.warning(
                    "FAISS update is not efficient. "
                    "Consider using a different vector store for frequent updates."
                )

            updated_count += 1

        return updated_count

    async def get_vector_count(self) -> int:
        """Get total number of vectors in the index."""
        return self.index.ntotal

    async def clear(self) -> int:
        """Clear all vectors from the index."""
        count = self.index.ntotal

        # Reset index
        self.index.reset()

        # Clear metadata
        self.texts.clear()
        self.metadata.clear()
        self.id_to_idx.clear()
        self.idx_to_id.clear()

        return count

    async def save_index(self, path: str) -> None:
        """Save index and metadata to disk."""
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_path = str(path_obj.with_suffix(".faiss"))
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: faiss.write_index(self.index, index_path)
        )

        # Save metadata
        metadata_path = str(path_obj.with_suffix(".meta"))

        # Collect file metadata for cache invalidation
        file_info = {}
        for _chunk_id, chunk_metadata in self.metadata.items():
            if isinstance(chunk_metadata, dict) and "file_path" in chunk_metadata:
                file_path = chunk_metadata["file_path"]
                if file_path not in file_info:
                    file_info[file_path] = {
                        "mtime": chunk_metadata.get("file_mtime"),
                        "size": chunk_metadata.get("file_size"),
                        "indexed_at": chunk_metadata.get("indexed_at"),
                    }

        # Preserve any existing tracked files (like 0-chunk files) that aren't in chunk metadata
        if hasattr(self, "indexed_files") and self.indexed_files:
            for file_path, file_metadata in self.indexed_files.items():
                if file_path not in file_info:
                    file_info[file_path] = file_metadata

        # Update in-memory indexed_files so cache checks work immediately
        self.indexed_files = file_info

        metadata_dict = {
            "texts": self.texts,
            "metadata": self.metadata,
            "id_to_idx": self.id_to_idx,
            "idx_to_id": self.idx_to_id,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "metric": self.metric,
            "index_params": self.index_params,
            # Cache invalidation metadata
            "index_created_at": datetime.now().isoformat(),
            "indexed_files": file_info,
        }

        with open(metadata_path, "wb") as f:
            pickle.dump(metadata_dict, f)

    async def load_index(self, path: str) -> None:
        """Load index and metadata from disk."""
        path_obj = Path(path)

        # Load FAISS index
        index_path = str(path_obj.with_suffix(".faiss"))
        self.index = await asyncio.get_event_loop().run_in_executor(
            None, lambda: faiss.read_index(index_path)
        )

        # Load metadata
        metadata_path = str(path_obj.with_suffix(".meta"))
        with open(metadata_path, "rb") as f:
            metadata_dict = pickle.load(f)

        self.texts = metadata_dict["texts"]
        self.metadata = metadata_dict["metadata"]
        self.id_to_idx = metadata_dict["id_to_idx"]
        self.idx_to_id = metadata_dict["idx_to_id"]
        self.dimension = metadata_dict["dimension"]
        self.index_type = metadata_dict["index_type"]
        self.metric = metadata_dict["metric"]
        self.index_params = metadata_dict["index_params"]

        # Load cache invalidation metadata (with backwards compatibility)
        self.index_created_at = metadata_dict.get("index_created_at")
        self.indexed_files = metadata_dict.get("indexed_files", {})
