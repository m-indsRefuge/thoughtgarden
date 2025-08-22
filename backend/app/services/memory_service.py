# file: backend/app/services/memory_service.py (Corrected for ChromaDB Metadata)
import chromadb
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger("tes_backend")

def _flatten_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flattens the metadata dictionary to be compatible with ChromaDB.
    Converts nested dicts (like strategy_performance) into simple key-value pairs.
    """
    flat_meta = {}
    for key, value in metadata.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                # e.g., 'strategy_performance' becomes 'perf_Analogical Leap'
                flat_meta[f"perf_{sub_key}"] = sub_value
        else:
            flat_meta[key] = value
    return flat_meta

class MemoryStore:
    def __init__(self, path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name="thought_garden_memories")
        logger.info(f"MemoryStore initialized. Database stored at: {os.path.abspath(path)}")

    def store_experiment_summary(self, experiment_id: str, summary_text: str, metadata: Dict[str, Any]):
        """Stores a summary of a completed thought experiment in the vector database."""
        try:
            # Flatten the metadata before storing it
            compatible_metadata = _flatten_metadata(metadata)
            
            self.collection.add(
                documents=[summary_text],
                metadatas=[compatible_metadata],
                ids=[f"exp_{experiment_id}"]
            )
            logger.info(f"Successfully stored summary for experiment {experiment_id} in memory.")
        except Exception as e:
            logger.error(f"Failed to store experiment summary for ID {experiment_id}: {e}")

    def retrieve_similar_memories(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Searches for and retrieves memories semantically similar to a query."""
        if self.collection.count() == 0:
            return []
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            memories = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    memories.append({
                        "document": doc,
                        "metadata": results['metadatas'][0][i]
                    })
            return memories
        except Exception as e:
            logger.error(f"Failed to retrieve similar memories for query '{query_text}': {e}")
            return []

memory_service = MemoryStore()