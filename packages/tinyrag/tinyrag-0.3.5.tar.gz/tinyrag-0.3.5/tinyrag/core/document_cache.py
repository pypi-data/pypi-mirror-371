"""
Document cache system to avoid re-processing the same documents
"""

import os
import json
import hashlib
import pickle
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime


class DocumentCache:
    """
    Manages caching of processed documents to avoid re-chunking and re-embedding
    """
    
    def __init__(self, cache_dir: str = ".tinyrag_cache"):
        """
        Initialize document cache
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache files
        self.metadata_file = self.cache_dir / "metadata.json"
        self.embeddings_dir = self.cache_dir / "embeddings"
        self.chunks_dir = self.cache_dir / "chunks"
        
        # Create subdirectories
        self.embeddings_dir.mkdir(exist_ok=True)
        self.chunks_dir.mkdir(exist_ok=True)
        
        # Load existing metadata
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache metadata: {e}")
        
        return {
            "documents": {},  # file_hash -> document info
            "embedding_configs": {}  # config_hash -> embedding configuration
        }
    
    def _save_metadata(self):
        """Save cache metadata to disk"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache metadata: {e}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get hash of file content for cache key"""
        try:
            if os.path.isfile(file_path):
                # For files, hash content and modification time
                stat = os.stat(file_path)
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                hash_input = content + str(stat.st_mtime).encode() + str(stat.st_size).encode()
                return hashlib.sha256(hash_input).hexdigest()
            else:
                # For text strings, just hash the content
                return hashlib.sha256(file_path.encode('utf-8')).hexdigest()
        except Exception:
            # Fallback to simple string hash
            return hashlib.sha256(str(file_path).encode('utf-8')).hexdigest()
    
    def _get_embedding_config_hash(self, provider_info: Dict[str, Any]) -> str:\n        \"\"\"Get hash of embedding configuration\"\"\"\n        config_str = json.dumps(provider_info, sort_keys=True)\n        return hashlib.sha256(config_str.encode('utf-8')).hexdigest()\n    \n    def _get_provider_info(self, provider) -> Dict[str, Any]:\n        \"\"\"Extract relevant provider information for cache key\"\"\"\n        return {\n            \"embedding_provider\": getattr(provider, 'embedding_provider', 'unknown'),\n            \"embedding_model\": getattr(provider, 'embedding_model', 'unknown'),\n            \"base_url\": getattr(provider, 'base_url', ''),\n            \"ollama_base_url\": getattr(provider, 'ollama_base_url', '')\n        }\n    \n    def is_cached(self, document_path: str, provider, chunk_size: int) -> bool:\n        \"\"\"Check if document is already cached with current configuration\"\"\"\n        file_hash = self._get_file_hash(document_path)\n        provider_info = self._get_provider_info(provider)\n        config_hash = self._get_embedding_config_hash({\n            **provider_info,\n            \"chunk_size\": chunk_size\n        })\n        \n        # Check if document exists in cache\n        if file_hash not in self.metadata[\"documents\"]:\n            return False\n        \n        doc_info = self.metadata[\"documents\"][file_hash]\n        \n        # Check if embedding configuration matches\n        return doc_info.get(\"config_hash\") == config_hash\n    \n    def get_cached_data(self, document_path: str, provider, chunk_size: int) -> Optional[Tuple[List[str], List[List[float]]]]:\n        \"\"\"Get cached chunks and embeddings for a document\"\"\"\n        if not self.is_cached(document_path, provider, chunk_size):\n            return None\n        \n        file_hash = self._get_file_hash(document_path)\n        \n        try:\n            # Load chunks\n            chunks_file = self.chunks_dir / f\"{file_hash}.json\"\n            with open(chunks_file, 'r', encoding='utf-8') as f:\n                chunks = json.load(f)\n            \n            # Load embeddings\n            embeddings_file = self.embeddings_dir / f\"{file_hash}.pkl\"\n            with open(embeddings_file, 'rb') as f:\n                embeddings = pickle.load(f)\n            \n            return chunks, embeddings\n        \n        except Exception as e:\n            print(f\"Warning: Could not load cached data for {document_path}: {e}\")\n            return None\n    \n    def cache_document(self, document_path: str, chunks: List[str], \n                      embeddings: List[List[float]], provider, chunk_size: int):\n        \"\"\"Cache processed document chunks and embeddings\"\"\"\n        file_hash = self._get_file_hash(document_path)\n        provider_info = self._get_provider_info(provider)\n        config_hash = self._get_embedding_config_hash({\n            **provider_info,\n            \"chunk_size\": chunk_size\n        })\n        \n        try:\n            # Save chunks\n            chunks_file = self.chunks_dir / f\"{file_hash}.json\"\n            with open(chunks_file, 'w', encoding='utf-8') as f:\n                json.dump(chunks, f, ensure_ascii=False)\n            \n            # Save embeddings\n            embeddings_file = self.embeddings_dir / f\"{file_hash}.pkl\"\n            with open(embeddings_file, 'wb') as f:\n                pickle.dump(embeddings, f)\n            \n            # Update metadata\n            self.metadata[\"documents\"][file_hash] = {\n                \"original_path\": document_path,\n                \"config_hash\": config_hash,\n                \"chunk_count\": len(chunks),\n                \"cached_at\": datetime.now().isoformat(),\n                \"provider_info\": provider_info,\n                \"chunk_size\": chunk_size\n            }\n            \n            # Store embedding configuration\n            self.metadata[\"embedding_configs\"][config_hash] = {\n                **provider_info,\n                \"chunk_size\": chunk_size,\n                \"created_at\": datetime.now().isoformat()\n            }\n            \n            self._save_metadata()\n            \n        except Exception as e:\n            print(f\"Warning: Could not cache document {document_path}: {e}\")\n    \n    def clear_cache(self):\n        \"\"\"Clear all cached data\"\"\"\n        try:\n            # Remove all cache files\n            for file in self.embeddings_dir.glob(\"*.pkl\"):\n                file.unlink()\n            for file in self.chunks_dir.glob(\"*.json\"):\n                file.unlink()\n            \n            # Clear metadata\n            self.metadata = {\n                \"documents\": {},\n                \"embedding_configs\": {}\n            }\n            self._save_metadata()\n            \n            print(\"✓ Cache cleared\")\n            \n        except Exception as e:\n            print(f\"Warning: Could not clear cache: {e}\")\n    \n    def get_cache_info(self) -> Dict[str, Any]:\n        \"\"\"Get information about cached documents\"\"\"\n        total_documents = len(self.metadata[\"documents\"])\n        total_configs = len(self.metadata[\"embedding_configs\"])\n        \n        # Calculate cache size\n        cache_size = 0\n        try:\n            for file in self.cache_dir.rglob(\"*\"):\n                if file.is_file():\n                    cache_size += file.stat().st_size\n        except Exception:\n            cache_size = 0\n        \n        return {\n            \"total_documents\": total_documents,\n            \"total_configurations\": total_configs,\n            \"cache_size_mb\": cache_size / (1024 * 1024),\n            \"cache_directory\": str(self.cache_dir)\n        }\n    \n    def cleanup_old_cache(self, days: int = 30):\n        \"\"\"Remove cache entries older than specified days\"\"\"\n        from datetime import datetime, timedelta\n        \n        cutoff_date = datetime.now() - timedelta(days=days)\n        removed_count = 0\n        \n        try:\n            # Find old documents\n            to_remove = []\n            for file_hash, doc_info in self.metadata[\"documents\"].items():\n                cached_at = datetime.fromisoformat(doc_info.get(\"cached_at\", \"\"))\n                if cached_at < cutoff_date:\n                    to_remove.append(file_hash)\n            \n            # Remove old cache files\n            for file_hash in to_remove:\n                # Remove files\n                chunks_file = self.chunks_dir / f\"{file_hash}.json\"\n                embeddings_file = self.embeddings_dir / f\"{file_hash}.pkl\"\n                \n                chunks_file.unlink(missing_ok=True)\n                embeddings_file.unlink(missing_ok=True)\n                \n                # Remove from metadata\n                del self.metadata[\"documents\"][file_hash]\n                removed_count += 1\n            \n            # Clean up unused configurations\n            used_configs = set(doc[\"config_hash\"] for doc in self.metadata[\"documents\"].values())\n            unused_configs = []\n            for config_hash in self.metadata[\"embedding_configs\"]:\n                if config_hash not in used_configs:\n                    unused_configs.append(config_hash)\n            \n            for config_hash in unused_configs:\n                del self.metadata[\"embedding_configs\"][config_hash]\n            \n            self._save_metadata()\n            \n            if removed_count > 0:\n                print(f\"✓ Cleaned up {removed_count} old cache entries\")\n            \n        except Exception as e:\n            print(f\"Warning: Could not cleanup cache: {e}\")\n    \n    def disable_cache(self) -> 'NullCache':\n        \"\"\"Return a null cache that doesn't cache anything\"\"\"\n        return NullCache()\n\n\nclass NullCache:\n    \"\"\"A null cache implementation that doesn't cache anything\"\"\"\n    \n    def is_cached(self, *args, **kwargs) -> bool:\n        return False\n    \n    def get_cached_data(self, *args, **kwargs) -> None:\n        return None\n    \n    def cache_document(self, *args, **kwargs):\n        pass\n    \n    def clear_cache(self):\n        pass\n    \n    def get_cache_info(self) -> Dict[str, Any]:\n        return {\n            \"total_documents\": 0,\n            \"total_configurations\": 0,\n            \"cache_size_mb\": 0,\n            \"cache_directory\": \"disabled\"\n        }\n    \n    def cleanup_old_cache(self, days: int = 30):\n        pass\n