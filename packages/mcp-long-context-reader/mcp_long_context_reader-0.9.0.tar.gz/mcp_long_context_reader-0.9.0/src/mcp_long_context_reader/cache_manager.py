"""
Handles the filesystem-based LRU caching for pre-processed documents.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class CacheManager:
    """
    Manages a filesystem-based LRU cache for strategy artifacts.

    This class is responsible for:
    - Creating a deterministic cache key based on file content and strategy.
    - Storing and retrieving pre-processed artifacts.
    - Pruning the cache to respect size and age limits.
    """

    def __init__(self, cache_dir: Path, manifest_path: Path):
        self.cache_dir = cache_dir
        self.manifest_path = manifest_path
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        """Loads the cache manifest file."""
        if not self.manifest_path.exists():
            return {"entries": {}}
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"entries": {}}  # Manifest is corrupt, start fresh

    def _save_manifest(self):
        """Saves the current state of the manifest."""
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self._manifest, f, indent=2)

    def generate_key(
        self, file_path: Path, strategy_name: str, strategy_params: Dict[str, Any]
    ) -> str:
        """
        Generates a deterministic SHA256 hash key for a given resource.
        """
        if not file_path.exists():
            raise FileNotFoundError(
                f"Cannot generate key for non-existent file: {file_path}"
            )

        # Get file modification time as a proxy for content change
        mtime = str(file_path.stat().st_mtime)

        # Sort params to ensure consistent key generation
        sorted_params = json.dumps(strategy_params, sort_keys=True)

        key_string = f"{file_path.resolve()}|{mtime}|{strategy_name}|{sorted_params}"

        return hashlib.sha256(key_string.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Path]:
        """
        Retrieves the cache file path for a key and updates its access time.
        Returns None if not found.
        """
        entry = self._manifest["entries"].get(key)
        if not entry:
            return None

        cache_filepath = self.cache_dir / entry["filename"]
        if not cache_filepath.exists():
            # Data corruption or manual deletion, remove from manifest
            del self._manifest["entries"][key]
            self._save_manifest()
            return None

        entry["last_accessed"] = time.time()
        self._save_manifest()
        return cache_filepath

    def put(self, key: str) -> Path:
        """
        Creates a new entry in the manifest and returns the path for the new artifact.
        """
        filename = f"{key}.cache"
        self._manifest["entries"][key] = {
            "filename": filename,
            "created": time.time(),
            "last_accessed": time.time(),
        }
        self._save_manifest()
        return self.cache_dir / filename

    def prune(
        self,
        max_size_bytes: Optional[int] = None,
        max_age_seconds: Optional[int] = None,
    ):
        """
        Removes stale or excess cache files based on LRU and TTL policies.
        """
        now = time.time()
        entries_to_delete = set()

        # 1. Identify entries older than max_age_seconds (TTL)
        if max_age_seconds is not None:
            for key, entry in self._manifest["entries"].items():
                age = now - entry["last_accessed"]
                if age > max_age_seconds:
                    entries_to_delete.add(key)

        # 2. If size still exceeds max_size_bytes, remove the least recently used
        current_size = sum(
            f.stat().st_size for f in self.cache_dir.glob("*.cache") if f.is_file()
        )

        if max_size_bytes is not None and current_size > max_size_bytes:
            # Sort entries by last_accessed time, oldest first
            sorted_entries = sorted(
                self._manifest["entries"].items(),
                key=lambda item: item[1]["last_accessed"],
            )

            for key, entry in sorted_entries:
                if key in entries_to_delete:
                    continue  # Already marked for deletion

                if current_size <= max_size_bytes:
                    break

                filepath = self.cache_dir / entry["filename"]
                if filepath.exists():
                    current_size -= filepath.stat().st_size

                entries_to_delete.add(key)

        # 3. Perform deletion
        for key in entries_to_delete:
            entry = self._manifest["entries"].pop(key, None)
            if entry:
                filepath = self.cache_dir / entry["filename"]
                if filepath.exists():
                    filepath.unlink()

        self._save_manifest()
