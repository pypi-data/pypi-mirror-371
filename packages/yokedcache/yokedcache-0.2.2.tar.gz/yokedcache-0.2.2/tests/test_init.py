"""
Tests for the __init__.py module import handling.
"""

import sys
from unittest.mock import patch, MagicMock
import pytest


class TestInitImports:
    """Test the __init__.py module import handling and fallbacks."""

    def test_version_attributes(self):
        """Test that version attributes are properly set."""
        import yokedcache
        
        assert hasattr(yokedcache, '__version__')
        assert hasattr(yokedcache, '__author__')
        assert hasattr(yokedcache, '__email__')
        assert hasattr(yokedcache, '__license__')
        
        assert yokedcache.__version__ == "0.2.2"
        assert yokedcache.__author__ == "Project Yoked LLC"
        assert yokedcache.__email__ == "twogoodgamer2@gmail.com"
        assert yokedcache.__license__ == "MIT"

    def test_redis_import_fallback(self):
        """Test that Redis import fallback works correctly."""
        # Mock Redis import failure
        with patch.dict('sys.modules', {'redis': None}):
            with patch('yokedcache.cache.redis', side_effect=ImportError("No module named 'redis'")):
                # Force reimport
                if 'yokedcache' in sys.modules:
                    del sys.modules['yokedcache']
                if 'yokedcache.cache' in sys.modules:
                    del sys.modules['yokedcache.cache']
                
                import yokedcache
                
                # Should have fallback YokedCache that raises ImportError
                with pytest.raises(ImportError, match="Redis is required"):
                    yokedcache.YokedCache()

    def test_backends_import_fallback(self):
        """Test that backends import fallback works correctly."""
        with patch('yokedcache.backends', side_effect=ImportError("No backends")):
            # Force reimport
            if 'yokedcache' in sys.modules:
                del sys.modules['yokedcache']
            
            import yokedcache
            
            # Should have None fallbacks
            assert yokedcache.CacheBackend is None
            assert yokedcache.RedisBackend is None
            assert yokedcache.MemoryBackend is None
            assert yokedcache.MemcachedBackend is None

    def test_monitoring_import_fallback(self):
        """Test that monitoring import fallback works correctly."""
        with patch('yokedcache.monitoring', side_effect=ImportError("No monitoring")):
            # Force reimport
            if 'yokedcache' in sys.modules:
                del sys.modules['yokedcache']
            
            import yokedcache
            
            # Should have None fallbacks
            assert yokedcache.CacheMetrics is None
            assert yokedcache.NoOpCollector is None
            assert yokedcache.PrometheusCollector is None
            assert yokedcache.StatsDCollector is None

    def test_vector_search_import_fallback(self):
        """Test that vector search import fallback works correctly."""
        with patch('yokedcache.vector_search', side_effect=ImportError("No vector search")):
            # Force reimport
            if 'yokedcache' in sys.modules:
                del sys.modules['yokedcache']
            
            import yokedcache
            
            # Should have None fallbacks
            assert yokedcache.VectorSimilaritySearch is None
            assert yokedcache.RedisVectorSearch is None

    def test_memcached_backend_conditional_import(self):
        """Test that MemcachedBackend is conditionally imported."""
        # Mock MEMCACHED_AVAILABLE as False
        with patch('yokedcache.backends.MEMCACHED_AVAILABLE', False):
            # Force reimport
            if 'yokedcache' in sys.modules:
                del sys.modules['yokedcache']
            
            import yokedcache
            
            # MemcachedBackend should be None when not available
            assert yokedcache.MemcachedBackend is None

    def test_prometheus_collector_conditional_import(self):
        """Test that PrometheusCollector is conditionally imported."""
        with patch('yokedcache.monitoring.PrometheusCollector', side_effect=ImportError("No prometheus")):
            # Force reimport
            if 'yokedcache' in sys.modules:
                del sys.modules['yokedcache']
            
            import yokedcache
            
            # PrometheusCollector should be None when not available
            assert yokedcache.PrometheusCollector is None

    def test_statsd_collector_conditional_import(self):
        """Test that StatsDCollector is conditionally imported."""
        with patch('yokedcache.monitoring.StatsDCollector', side_effect=ImportError("No statsd")):
            # Force reimport
            if 'yokedcache' in sys.modules:
                del sys.modules['yokedcache']
            
            import yokedcache
            
            # StatsDCollector should be None when not available
            assert yokedcache.StatsDCollector is None

    def test_all_exports(self):
        """Test that __all__ contains all expected exports."""
        import yokedcache
        
        expected_exports = [
            # Core classes
            "YokedCache", "CacheConfig",
            # Decorators and utilities
            "cached", "cached_dependency",
            # Models
            "CacheEntry", "CacheStats", "InvalidationRule",
            # Exceptions
            "YokedCacheError", "CacheConnectionError", "CacheKeyError", "CacheSerializationError",
            # Utilities
            "generate_cache_key", "serialize_data", "deserialize_data",
            # Backends
            "CacheBackend", "RedisBackend", "MemoryBackend", "MemcachedBackend",
            # Monitoring
            "CacheMetrics", "NoOpCollector", "PrometheusCollector", "StatsDCollector",
            # Vector search
            "VectorSimilaritySearch", "RedisVectorSearch",
        ]
        
        for export in expected_exports:
            assert export in yokedcache.__all__
            assert hasattr(yokedcache, export)

    def test_successful_imports(self):
        """Test that all imports work when dependencies are available."""
        import yokedcache
        
        # Core imports should always work
        assert yokedcache.CacheConfig is not None
        assert yokedcache.cached is not None
        assert yokedcache.cached_dependency is not None
        assert yokedcache.CacheEntry is not None
        assert yokedcache.CacheStats is not None
        assert yokedcache.InvalidationRule is not None
        assert yokedcache.YokedCacheError is not None
        assert yokedcache.generate_cache_key is not None
        assert yokedcache.serialize_data is not None
        assert yokedcache.deserialize_data is not None
