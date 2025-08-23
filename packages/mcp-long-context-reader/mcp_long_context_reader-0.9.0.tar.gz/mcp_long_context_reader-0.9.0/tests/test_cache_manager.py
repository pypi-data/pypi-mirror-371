import shutil
import time
from pathlib import Path

import pytest

from mcp_long_context_reader.cache_manager import CacheManager


@pytest.fixture
def temp_cache(tmp_path: Path):
    """Creates a temporary cache directory and manifest for testing."""
    cache_dir = tmp_path / "cache"
    manifest_path = cache_dir / "manifest.json"
    manager = CacheManager(cache_dir=cache_dir, manifest_path=manifest_path)

    # Create a dummy file to generate keys from
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("hello world")

    yield manager, dummy_file

    # Clean up
    shutil.rmtree(cache_dir, ignore_errors=True)


class TestCacheManager:
    """Tests for the CacheManager."""

    def test_key_generation_is_deterministic(self, temp_cache):
        """Ensures the same inputs produce the same key."""
        manager, dummy_file = temp_cache
        params = {"chunk_size": 512}

        key1 = manager.generate_key(dummy_file, "RAG", params)
        key2 = manager.generate_key(dummy_file, "RAG", params)

        assert key1 == key2
        assert len(key1) == 64  # SHA256

    def test_key_changes_with_file_modification(self, temp_cache):
        """Ensures the key changes if the file's mtime changes."""
        manager, dummy_file = temp_cache
        key1 = manager.generate_key(dummy_file, "RAG", {})

        # Simulate file modification by sleeping and touching the file
        time.sleep(0.01)
        dummy_file.touch()

        key2 = manager.generate_key(dummy_file, "RAG", {})
        assert key1 != key2

    def test_key_changes_with_strategy_or_params(self, temp_cache):
        """Ensures the key changes for different strategies or params."""
        manager, dummy_file = temp_cache
        key_rag = manager.generate_key(dummy_file, "RAG", {"chunk_size": 512})
        key_mapreduce = manager.generate_key(
            dummy_file, "MapReduce", {"chunk_size": 512}
        )
        key_rag_different_chunk = manager.generate_key(
            dummy_file, "RAG", {"chunk_size": 1024}
        )

        assert key_rag != key_mapreduce
        assert key_rag != key_rag_different_chunk

    def test_put_and_get_flow(self, temp_cache):
        """Tests the basic put and get functionality."""
        manager, dummy_file = temp_cache
        key = manager.generate_key(dummy_file, "test", {})

        # Should not exist initially
        assert manager.get(key) is None

        # Put a new entry
        new_path = manager.put(key)
        new_path.touch()  # Simulate the cache file being created
        assert new_path.name == f"{key}.cache"

        # Now it should exist
        retrieved_path = manager.get(key)
        assert retrieved_path is not None
        assert retrieved_path == new_path

    def test_get_updates_last_accessed_time(self, temp_cache):
        """Tests that 'get' updates the timestamp in the manifest."""
        manager, dummy_file = temp_cache
        key = manager.generate_key(dummy_file, "test", {})
        cache_file_path = manager.put(key)
        cache_file_path.touch()  # Simulate the cache file being created

        entry1_last_accessed = manager._manifest["entries"][key]["last_accessed"]
        time.sleep(0.01)

        manager.get(key)
        entry2_last_accessed = manager._manifest["entries"][key]["last_accessed"]

        assert entry2_last_accessed > entry1_last_accessed

    def test_get_handles_missing_file_gracefully(self, temp_cache):
        """
        Tests that get() correctly handles cases where the manifest entry
        exists but the file on disk has been deleted.
        """
        manager, dummy_file = temp_cache
        key = manager.generate_key(dummy_file, "test", {})

        # Create an entry and the corresponding dummy file
        cache_file_path = manager.put(key)
        cache_file_path.touch()
        assert cache_file_path.exists()
        assert manager.get(key) is not None

        # Manually delete the cache file
        cache_file_path.unlink()
        assert not cache_file_path.exists()

        # The next get should return None and clean up the manifest
        assert manager.get(key) is None
        assert key not in manager._manifest["entries"]

    def test_prune_by_max_age(self, temp_cache):
        """Tests pruning based on max_age_seconds (TTL)."""
        manager, dummy_file = temp_cache

        # Create two entries
        key1 = manager.generate_key(dummy_file, "stale", {})
        path1 = manager.put(key1)
        path1.touch()

        time.sleep(0.02)

        key2 = manager.generate_key(dummy_file, "fresh", {})
        path2 = manager.put(key2)
        path2.touch()

        # Prune entries older than 0.01 seconds. key1 should be gone.
        manager.prune(max_age_seconds=0.01)

        assert manager.get(key1) is None
        assert manager.get(key2) is not None
        assert not path1.exists()
        assert path2.exists()

    def test_prune_by_max_size(self, temp_cache):
        """Tests pruning based on max_size_bytes (LRU)."""
        manager, dummy_file = temp_cache

        # Create 3 files, each ~10 bytes
        key1 = manager.generate_key(dummy_file, "1", {})
        p1 = manager.put(key1)
        p1.write_text("123456789")
        time.sleep(0.01)

        key2 = manager.generate_key(dummy_file, "2", {})
        p2 = manager.put(key2)
        p2.write_text("123456789")
        time.sleep(0.01)

        key3 = manager.generate_key(dummy_file, "3", {})
        p3 = manager.put(key3)
        p3.write_text("123456789")

        # Total size is ~30 bytes. Set max size to 15.
        # This should delete the two least recently used files (1 and 2).
        manager.prune(max_size_bytes=15)

        assert manager.get(key1) is None
        assert manager.get(key2) is None
        assert manager.get(key3) is not None  # Most recent should survive
        assert not p1.exists()
        assert not p2.exists()
        assert p3.exists()
