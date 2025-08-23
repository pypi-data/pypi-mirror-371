"""
Comprehensive validation and compatibility tests - Part 2: Search Engine Compatibility.

This module implements Task 9: Create comprehensive validation and compatibility tests
- Add search engine compatibility validation tests

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import pytest
import numpy as np
from unittest.mock import Mock

from hilbert_quantization.core.optimized_index_generator import OptimizedIndexGenerator
from hilbert_quantization.core.index_generator import HierarchicalIndexGeneratorImpl
from hilbert_quantization.core.search_engine import ProgressiveSimilaritySearchEngine
from hilbert_quantization.models import QuantizedModel, ModelMetadata, SearchResult
from hilbert_quantization.api import HilbertQuantizer


class TestSearchEngineCompatibility:
    """Test search engine compatibility validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimized_generator = OptimizedIndexGenerator(enable_auto_fallback=False)
        self.traditional_generator = HierarchicalIndexGeneratorImpl()
        self.search_engine = ProgressiveSimilaritySearchEngine()
        self.quantizer = HilbertQuantizer()
        
    def test_search_engine_accepts_optimized_indices(self):
        """Test that search engine accepts indices from optimized generator."""
        # Create test images
        query_image = np.random.randn(16, 16).astype(np.float32)
        candidate_images = [
            np.random.randn(16, 16).astype(np.float32) for _ in range(5)
        ]
        
        index_space_size = 120
        
        # Generate indices with optimized method
        query_indices = self.optimized_generator._generate_with_optimization(
            query_image, index_space_size
        )
        
        candidate_indices_list = []
        for img in candidate_images:
            indices = self.optimized_generator._generate_with_optimization(
                img, index_space_size
            )
            candidate_indices_list.append(indices)
        
        # Create mock quantized models
        candidate_models = []
        for i, indices in enumerate(candidate_indices_list):
            metadata = ModelMetadata(
                model_name=f"test_model_{i}",
                original_size_bytes=1024,
                compressed_size_bytes=512,
                compression_ratio=2.0,
                quantization_timestamp="2024-01-01"
            )
            
            model = Mock(spec=QuantizedModel)
            model.hierarchical_indices = indices
            model.metadata = metadata
            candidate_models.append(model)
        
        # Test progressive search
        search_results = self.search_engine.progressive_search(
            query_indices, candidate_models, max_results=3
        )
        
        # Search should complete successfully
        assert isinstance(search_results, list)
        assert len(search_results) <= 3
        
        # All results should be valid SearchResult objects
        for result in search_results:
            assert hasattr(result, 'model')
            assert hasattr(result, 'similarity_score')
            assert hasattr(result, 'matching_indices')
            assert 0.0 <= result.similarity_score <= 1.0
    
    def test_search_results_consistency_between_methods(self):
        """Test that search results are consistent between traditional and optimized methods."""
        # Create query and candidate images
        np.random.seed(42)  # For reproducible results
        query_image = np.random.randn(8, 8).astype(np.float32)
        
        # Create candidates with varying similarity to query
        candidate_images = []
        # Similar candidates (query + small noise)
        for i in range(3):
            similar = query_image + np.random.randn(8, 8) * 0.1
            candidate_images.append(similar.astype(np.float32))
        
        # Dissimilar candidates (random)
        for i in range(2):
            dissimilar = np.random.randn(8, 8).astype(np.float32)
            candidate_images.append(dissimilar)
        
        index_space_size = 80
        
        # Generate indices with both methods
        query_indices_traditional = self.traditional_generator.generate_optimized_indices(
            query_image, index_space_size
        )
        query_indices_optimized = self.optimized_generator._generate_with_optimization(
            query_image, index_space_size
        )
        
        # Create candidate models for both methods
        traditional_models = []
        optimized_models = []
        
        for i, img in enumerate(candidate_images):
            # Traditional indices
            trad_indices = self.traditional_generator.generate_optimized_indices(
                img, index_space_size
            )
            trad_model = Mock(spec=QuantizedModel)
            trad_model.hierarchical_indices = trad_indices
            trad_model.metadata = Mock()
            trad_model.metadata.model_name = f"traditional_model_{i}"
            traditional_models.append(trad_model)
            
            # Optimized indices
            opt_indices = self.optimized_generator._generate_with_optimization(
                img, index_space_size
            )
            opt_model = Mock(spec=QuantizedModel)
            opt_model.hierarchical_indices = opt_indices
            opt_model.metadata = Mock()
            opt_model.metadata.model_name = f"optimized_model_{i}"
            optimized_models.append(opt_model)
        
        # Perform searches with both methods
        traditional_results = self.search_engine.progressive_search(
            query_indices_traditional, traditional_models, max_results=5
        )
        
        optimized_results = self.search_engine.progressive_search(
            query_indices_optimized, optimized_models, max_results=5
        )
        
        # Both searches should return results
        assert len(traditional_results) > 0, "Traditional search returned no results"
        assert len(optimized_results) > 0, "Optimized search returned no results"
        
        # Results should be properly ranked (descending similarity)
        for results, method_name in [(traditional_results, "traditional"), (optimized_results, "optimized")]:
            similarities = [r.similarity_score for r in results]
            assert similarities == sorted(similarities, reverse=True), f"{method_name} results not properly ranked"
        
        # Similar candidates should generally rank higher than dissimilar ones
        # (This is probabilistic due to quantization effects, so we check trends)
        for results, method_name in [(traditional_results, "traditional"), (optimized_results, "optimized")]:
            if len(results) >= 3:
                # Check that at least one of the top 3 results has reasonable similarity
                top_similarities = [r.similarity_score for r in results[:3]]
                assert max(top_similarities) > 0.1, f"{method_name} search found no similar candidates"
    
    def test_brute_force_vs_progressive_search_compatibility(self):
        """Test compatibility between brute force and progressive search methods."""
        # Create test data
        query_image = np.random.randn(8, 8).astype(np.float32)
        candidate_images = [np.random.randn(8, 8).astype(np.float32) for _ in range(10)]
        
        index_space_size = 60
        
        # Generate indices with optimized method
        query_indices = self.optimized_generator._generate_with_optimization(
            query_image, index_space_size
        )
        
        candidate_models = []
        for i, img in enumerate(candidate_images):
            indices = self.optimized_generator._generate_with_optimization(
                img, index_space_size
            )
            
            model = Mock(spec=QuantizedModel)
            model.hierarchical_indices = indices
            model.metadata = Mock()
            model.metadata.model_name = f"candidate_{i}"
            candidate_models.append(model)
        
        # Perform both types of search
        progressive_results = self.search_engine.progressive_search(
            query_indices, candidate_models, max_results=5
        )
        
        brute_force_results = self.search_engine.brute_force_search(
            query_indices, candidate_models, max_results=5
        )
        
        # Both should return valid results
        assert len(progressive_results) > 0, "Progressive search returned no results"
        assert len(brute_force_results) > 0, "Brute force search returned no results"
        
        # Results should be properly formatted
        for results, method_name in [(progressive_results, "progressive"), (brute_force_results, "brute_force")]:
            for result in results:
                assert isinstance(result, SearchResult), f"{method_name} returned invalid result type"
                assert 0.0 <= result.similarity_score <= 1.0, f"{method_name} similarity out of range"
                assert hasattr(result, 'matching_indices'), f"{method_name} missing matching_indices"
        
        # Progressive search should be at least as good as brute force for top results
        # (Progressive search uses more sophisticated filtering)
        if len(progressive_results) > 0 and len(brute_force_results) > 0:
            prog_top_score = progressive_results[0].similarity_score
            bf_top_score = brute_force_results[0].similarity_score
            
            # Progressive should find results at least as good as brute force
            assert prog_top_score >= bf_top_score - 0.1, "Progressive search significantly worse than brute force"
    
    def test_search_engine_level_comparison_accuracy(self):
        """Test accuracy of level-by-level index comparison in search engine."""
        # Create test indices with known structure
        query_indices = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        
        # Create similar candidate (small differences)
        np.random.seed(42)  # For reproducible results
        similar_indices = query_indices + np.random.randn(len(query_indices)) * 0.1
        
        # Create dissimilar candidate (large differences)
        dissimilar_indices = np.random.randn(len(query_indices)) * 5.0
        
        # Test level-by-level comparison
        for level in range(3):  # Test first few levels
            similar_score = self.search_engine.compare_indices_at_level(
                query_indices, similar_indices, level
            )
            
            dissimilar_score = self.search_engine.compare_indices_at_level(
                query_indices, dissimilar_indices, level
            )
            
            # Scores should be in valid range
            assert 0.0 <= similar_score <= 1.0, f"Level {level} similar score out of range"
            assert 0.0 <= dissimilar_score <= 1.0, f"Level {level} dissimilar score out of range"
            
            # Similar indices should generally score higher than dissimilar ones
            # (Allow for edge cases where both might be 0.0 due to index structure parsing)
            if similar_score > 0.0 or dissimilar_score > 0.0:
                assert similar_score >= dissimilar_score, f"Level {level} comparison failed: similar={similar_score}, dissimilar={dissimilar_score}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])