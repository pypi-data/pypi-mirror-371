#!/usr/bin/env python3
"""
Comprehensive tests for OctaneDB vector database.

Tests cover:
- Basic functionality
- CRUD operations
- Search operations
- Performance characteristics
- Error handling
"""

import unittest
import numpy as np
import tempfile
import shutil
import time
from pathlib import Path

from octanedb import OctaneDB, Collection, HNSWIndex, VectorUtils


class TestOctaneDB(unittest.TestCase):
    """Test cases for OctaneDB main class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db = OctaneDB(
            dimension=64,
            index_type="hnsw",
            m=8,
            ef_construction=100,
            ef_search=50,
            storage_path=self.temp_dir
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test database initialization."""
        self.assertEqual(self.db.dimension, 64)
        self.assertEqual(self.db.index_type, "hnsw")
        self.assertEqual(self.db.m, 8)
        self.assertEqual(self.db.ef_construction, 100)
        self.assertEqual(self.db.ef_search, 50)
        self.assertEqual(self.db.distance_metric, "cosine")
    
    def test_collection_creation(self):
        """Test collection creation."""
        collection = self.db.create_collection("test_collection")
        self.assertIsInstance(collection, Collection)
        self.assertEqual(collection.name, "test_collection")
        self.assertEqual(collection.dimension, 64)
        
        # Test duplicate collection creation
        with self.assertRaises(ValueError):
            self.db.create_collection("test_collection")
    
    def test_collection_management(self):
        """Test collection management operations."""
        # Create collections
        self.db.create_collection("collection1")
        self.db.create_collection("collection2")
        
        # List collections
        collections = self.db.list_collections()
        self.assertIn("collection1", collections)
        self.assertIn("collection2", collections)
        self.assertEqual(len(collections), 2)
        
        # Switch collections
        self.db.use_collection("collection2")
        self.assertEqual(self.db._current_collection.name, "collection2")
        
        # Get collection
        collection = self.db.get_collection("collection1")
        self.assertEqual(collection.name, "collection1")
        
        # Delete collection
        self.db.delete_collection("collection1")
        collections = self.db.list_collections()
        self.assertNotIn("collection1", collections)
    
    def test_vector_operations(self):
        """Test vector operations."""
        # Create collection
        self.db.create_collection("test_collection")
        
        # Insert vectors
        vectors = np.random.rand(10, 64).astype(np.float32)
        ids = self.db.insert(vectors)
        self.assertEqual(len(ids), 10)
        
        # Count vectors
        count = self.db.count()
        self.assertEqual(count, 10)
        
        # Get vector
        vector = self.db.get_vector(ids[0])
        self.assertEqual(vector.shape, (64,))
        
        # Update vector
        new_vector = np.random.rand(64).astype(np.float32)
        self.db.update(ids[0], new_vector)
        
        # Delete vector
        self.db.delete(ids[0])
        count = self.db.count()
        self.assertEqual(count, 9)
    
    def test_search_operations(self):
        """Test search operations."""
        # Create collection and insert vectors
        self.db.create_collection("test_collection")
        vectors = np.random.rand(100, 64).astype(np.float32)
        ids = self.db.insert(vectors)
        
        # Search
        query = np.random.rand(64).astype(np.float32)
        results = self.db.search(query, k=5)
        self.assertEqual(len(results), 5)
        
        # Check result format
        for vector_id, distance, metadata in results:
            self.assertIsInstance(vector_id, int)
            self.assertIsInstance(distance, float)
            self.assertIsInstance(metadata, type(None))  # No metadata requested
        
        # Search with metadata
        results = self.db.search(query, k=3, include_metadata=True)
        self.assertEqual(len(results), 3)
        
        # Batch search
        queries = np.random.rand(3, 64).astype(np.float32)
        batch_results = self.db.search_batch(queries, k=2)
        self.assertEqual(len(batch_results), 3)
        for results in batch_results:
            self.assertEqual(len(results), 2)
    
    def test_persistence(self):
        """Test database persistence."""
        # Create collection and insert vectors
        self.db.create_collection("test_collection")
        vectors = np.random.rand(50, 64).astype(np.float32)
        self.db.insert(vectors)
        
        # Save database
        save_path = Path(self.temp_dir) / "test_db.oct"
        self.db.save(save_path)
        self.assertTrue(save_path.exists())
        
        # Load database
        loaded_db = OctaneDB.load(save_path)
        self.assertEqual(loaded_db.dimension, 64)
        self.assertEqual(len(loaded_db.list_collections()), 1)
        
        # Verify data
        collection = loaded_db.get_collection("test_collection")
        self.assertEqual(collection.count(), 50)
    
    def test_error_handling(self):
        """Test error handling."""
        # Test operations without collection
        with self.assertRaises(RuntimeError):
            self.db.insert(np.random.rand(64).astype(np.float32))
        
        with self.assertRaises(RuntimeError):
            self.db.search(np.random.rand(64).astype(np.float32))
        
        # Test invalid collection
        with self.assertRaises(ValueError):
            self.db.use_collection("nonexistent")
        
        # Test invalid vector dimension
        self.db.create_collection("test_collection")
        with self.assertRaises(ValueError):
            self.db.insert(np.random.rand(32).astype(np.float32))  # Wrong dimension


class TestCollection(unittest.TestCase):
    """Test cases for Collection class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collection = Collection(
            name="test_collection",
            dimension=32,
            index_type="hnsw",
            m=4,
            ef_construction=50,
            ef_search=25
        )
    
    def test_initialization(self):
        """Test collection initialization."""
        self.assertEqual(self.collection.name, "test_collection")
        self.assertEqual(self.collection.dimension, 32)
        self.assertEqual(self.collection.index_type, "hnsw")
        self.assertFalse(self.collection._index_built)
    
    def test_vector_insertion(self):
        """Test vector insertion."""
        # Single vector
        vector = np.random.rand(32).astype(np.float32)
        vector_id = self.collection.insert(vector)
        self.assertIsInstance(vector_id, int)
        self.assertEqual(self.collection.count(), 1)
        
        # Multiple vectors
        vectors = np.random.rand(5, 32).astype(np.float32)
        ids = self.collection.insert(vectors)
        self.assertEqual(len(ids), 5)
        self.assertEqual(self.collection.count(), 6)
        
        # With metadata
        metadata = {"test": "value"}
        vector_id = self.collection.insert(vector, metadata=[metadata])
        self.assertEqual(self.collection.count(), 7)
    
    def test_vector_search(self):
        """Test vector search."""
        # Insert vectors
        vectors = np.random.rand(20, 32).astype(np.float32)
        self.collection.insert(vectors)
        
        # Search
        query = np.random.rand(32).astype(np.float32)
        results = self.collection.search(query, k=5)
        self.assertEqual(len(results), 5)
        
        # Verify index was built
        self.assertTrue(self.collection._index_built)
    
    def test_metadata_operations(self):
        """Test metadata operations."""
        # Insert with metadata
        vector = np.random.rand(32).astype(np.float32)
        metadata = {"category": "test", "value": 42}
        vector_id = self.collection.insert(vector, metadata=[metadata])
        
        # Get with metadata
        retrieved_vector, retrieved_metadata = self.collection.get_vector(
            vector_id, include_metadata=True
        )
        self.assertEqual(retrieved_metadata["category"], "test")
        self.assertEqual(retrieved_metadata["value"], 42)
        
        # Update metadata
        new_metadata = {"category": "updated", "value": 100}
        self.collection.update(vector_id, vector, new_metadata)
        
        # Verify update
        _, updated_metadata = self.collection.get_vector(vector_id, include_metadata=True)
        self.assertEqual(updated_metadata["category"], "updated")
    
    def test_vector_updates(self):
        """Test vector updates."""
        # Insert vector
        vector = np.random.rand(32).astype(np.float32)
        vector_id = self.collection.insert(vector)
        
        # Update vector
        new_vector = np.random.rand(32).astype(np.float32)
        self.collection.update(vector_id, new_vector)
        
        # Verify update
        retrieved_vector = self.collection.get_vector(vector_id)
        np.testing.assert_array_equal(retrieved_vector, new_vector)
        
        # Verify index needs rebuild
        self.assertTrue(self.collection._index_needs_rebuild)
    
    def test_vector_deletion(self):
        """Test vector deletion."""
        # Insert vectors
        vectors = np.random.rand(10, 32).astype(np.float32)
        ids = self.collection.insert(vectors)
        
        # Delete single vector
        self.collection.delete(ids[0])
        self.assertEqual(self.collection.count(), 9)
        
        # Delete multiple vectors
        self.collection.delete_batch(ids[1:3])
        self.assertEqual(self.collection.count(), 7)
        
        # Verify index needs rebuild
        self.assertTrue(self.collection._index_needs_rebuild)
    
    def test_collection_clear(self):
        """Test collection clearing."""
        # Insert vectors
        vectors = np.random.rand(10, 32).astype(np.float32)
        self.collection.insert(vectors)
        
        # Clear collection
        self.collection.clear()
        self.assertEqual(self.collection.count(), 0)
        self.assertFalse(self.collection._index_built)
        self.assertFalse(self.collection._index_needs_rebuild)


class TestHNSWIndex(unittest.TestCase):
    """Test cases for HNSW index."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = HNSWIndex(
            dimension=16,
            m=4,
            ef_construction=20,
            ef_search=10
        )
    
    def test_initialization(self):
        """Test index initialization."""
        self.assertEqual(self.index.dimension, 16)
        self.assertEqual(self.index.m, 4)
        self.assertEqual(self.index.ef_construction, 20)
        self.assertEqual(self.index.ef_search, 10)
        self.assertEqual(self.index.distance_metric, "cosine")
    
    def test_index_building(self):
        """Test index building."""
        # Generate vectors
        vectors = np.random.rand(50, 16).astype(np.float32)
        vector_ids = list(range(50))
        
        # Build index
        self.index.build(vectors, vector_ids)
        
        # Verify index was built
        self.assertIsNotNone(self.index._vectors)
        self.assertIsNotNone(self.index._vector_ids)
        self.assertEqual(len(self.index._layers), 1)  # At least one layer
    
    def test_vector_search(self):
        """Test vector search."""
        # Build index
        vectors = np.random.rand(100, 16).astype(np.float32)
        vector_ids = list(range(100))
        self.index.build(vectors, vector_ids)
        
        # Search
        query = np.random.rand(16).astype(np.float32)
        results = self.index.search(query, k=5)
        
        # Verify results
        self.assertEqual(len(results), 5)
        for vector_id, distance in results:
            self.assertIsInstance(vector_id, int)
            self.assertIsInstance(distance, float)
            self.assertGreaterEqual(distance, 0)
    
    def test_batch_search(self):
        """Test batch search."""
        # Build index
        vectors = np.random.rand(100, 16).astype(np.float32)
        vector_ids = list(range(100))
        self.index.build(vectors, vector_ids)
        
        # Batch search
        queries = np.random.rand(3, 16).astype(np.float32)
        batch_results = self.index.search_batch(queries, k=3)
        
        # Verify results
        self.assertEqual(len(batch_results), 3)
        for results in batch_results:
            self.assertEqual(len(results), 3)
    
    def test_distance_metrics(self):
        """Test different distance metrics."""
        # Test cosine distance
        a = np.array([1, 0, 0], dtype=np.float32)
        b = np.array([0, 1, 0], dtype=np.float32)
        distance = self.index._cosine_distance(a, b)
        self.assertAlmostEqual(distance, 1.0, places=5)
        
        # Test identical vectors
        distance = self.index._cosine_distance(a, a)
        self.assertAlmostEqual(distance, 0.0, places=5)
    
    def test_index_optimization(self):
        """Test index optimization."""
        # Build index
        vectors = np.random.rand(50, 16).astype(np.float32)
        vector_ids = list(range(50))
        self.index.build(vectors, vector_ids)
        
        # Optimize index
        self.index.optimize()
        
        # Verify optimization completed
        stats = self.index.get_stats()
        self.assertIn("index_type", stats)


class TestVectorUtils(unittest.TestCase):
    """Test cases for VectorUtils class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.vector_utils = VectorUtils(distance_metric="cosine")
    
    def test_distance_computation(self):
        """Test distance computation."""
        a = np.array([1, 0, 0], dtype=np.float32)
        b = np.array([0, 1, 0], dtype=np.float32)
        
        # Cosine distance
        distance = self.vector_utils.compute_distance(a, b)
        self.assertAlmostEqual(distance, 1.0, places=5)
        
        # Identical vectors
        distance = self.vector_utils.compute_distance(a, a)
        self.assertAlmostEqual(distance, 0.0, places=5)
    
    def test_batch_distance_computation(self):
        """Test batch distance computation."""
        query = np.array([1, 0, 0], dtype=np.float32)
        vectors = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ], dtype=np.float32)
        
        distances = self.vector_utils.compute_distances_batch(query, vectors)
        self.assertEqual(len(distances), 3)
        self.assertAlmostEqual(distances[0], 0.0, places=5)  # Identical
        self.assertAlmostEqual(distances[1], 1.0, places=5)  # Orthogonal
        self.assertAlmostEqual(distances[2], 1.0, places=5)  # Orthogonal
    
    def test_vector_normalization(self):
        """Test vector normalization."""
        vector = np.array([3, 4, 0], dtype=np.float32)
        normalized = VectorUtils.normalize_vector(vector)
        
        # Check norm is 1
        norm = np.linalg.norm(normalized)
        self.assertAlmostEqual(norm, 1.0, places=5)
        
        # Check direction is preserved
        self.assertAlmostEqual(normalized[0], 0.6, places=5)
        self.assertAlmostEqual(normalized[1], 0.8, places=5)
    
    def test_centroid_computation(self):
        """Test centroid computation."""
        vectors = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ], dtype=np.float32)
        
        centroid = VectorUtils.compute_centroid(vectors)
        expected = np.array([1/3, 1/3, 1/3], dtype=np.float32)
        np.testing.assert_array_almost_equal(centroid, expected, decimal=5)


class TestPerformance(unittest.TestCase):
    """Test cases for performance characteristics."""
    
    def test_insert_performance(self):
        """Test insert performance."""
        db = OctaneDB(dimension=64, enable_cache=False)
        collection = db.create_collection("perf_test")
        
        # Measure insert time
        vectors = np.random.rand(1000, 64).astype(np.float32)
        
        start_time = time.time()
        ids = collection.insert(vectors)
        insert_time = time.time() - start_time
        
        # Should be reasonably fast
        self.assertLess(insert_time, 10.0)  # Less than 10 seconds
        self.assertEqual(len(ids), 1000)
    
    def test_search_performance(self):
        """Test search performance."""
        db = OctaneDB(dimension=64, enable_cache=False)
        collection = db.create_collection("perf_test")
        
        # Insert vectors
        vectors = np.random.rand(1000, 64).astype(np.float32)
        collection.insert(vectors)
        
        # Measure search time
        query = np.random.rand(64).astype(np.float32)
        
        start_time = time.time()
        results = collection.search(query, k=10)
        search_time = time.time() - start_time
        
        # Should be very fast
        self.assertLess(search_time, 1.0)  # Less than 1 second
        self.assertEqual(len(results), 10)
    
    def test_memory_efficiency(self):
        """Test memory efficiency."""
        db = OctaneDB(dimension=64, enable_cache=False)
        collection = db.create_collection("memory_test")
        
        # Insert vectors
        vectors = np.random.rand(1000, 64).astype(np.float32)
        collection.insert(vectors)
        
        # Get stats
        stats = collection.get_stats()
        self.assertIn("vector_count", stats)
        self.assertEqual(stats["vector_count"], 1000)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
