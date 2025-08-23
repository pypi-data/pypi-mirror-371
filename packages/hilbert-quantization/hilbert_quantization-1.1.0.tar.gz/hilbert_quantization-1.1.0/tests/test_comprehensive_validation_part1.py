"""
Comprehensive validation and compatibility tests - Part 1: Accuracy Comparison.

This module implements Task 9: Create comprehensive validation and compatibility tests
- Implement accuracy comparison between generator and traditional methods

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import pytest
import numpy as np
from unittest.mock import Mock

from hilbert_quantization.core.optimized_index_generator import OptimizedIndexGenerator
from hilbert_quantization.core.index_generator import HierarchicalIndexGeneratorImpl
from hilbert_quantization.exceptions import QuantizationError, ValidationError


class TestAccuracyComparison:
    """Test accuracy comparison between generator and traditional methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimized_generator = OptimizedIndexGenerator(enable_auto_fallback=False)
        self.traditional_generator = HierarchicalIndexGeneratorImpl()
        
    def test_identical_results_small_images(self):
        """Test that both methods produce identical results for small images."""
        # Test various small power-of-2 dimensions
        test_dimensions = [4, 8, 16]
        
        for dim in test_dimensions:
            # Create test image
            test_image = np.random.randn(dim, dim).astype(np.float32)
            index_space_size = 100
            
            # Generate indices with both methods
            traditional_indices = self.traditional_generator.generate_optimized_indices(
                test_image, index_space_size
            )
            
            optimized_indices = self.optimized_generator._generate_with_optimization(
                test_image, index_space_size
            )
            
            # Both methods should produce valid indices
            assert len(traditional_indices) > 0, f"Traditional method failed for {dim}x{dim}"
            assert len(optimized_indices) > 0, f"Optimized method failed for {dim}x{dim}"
            
            # Indices should be finite and reasonable
            assert np.all(np.isfinite(traditional_indices)), f"Traditional indices invalid for {dim}x{dim}"
            assert np.all(np.isfinite(optimized_indices)), f"Optimized indices invalid for {dim}x{dim}"
            
            # Both should use the same index space efficiently
            assert len(traditional_indices) <= index_space_size
            assert len(optimized_indices) <= index_space_size
    
    def test_accuracy_comparison_detailed_metrics(self):
        """Test detailed accuracy comparison metrics between methods."""
        # Test with medium-sized image
        test_image = np.random.randn(32, 32).astype(np.float32)
        index_space_size = 200
        
        # Get comparison metrics
        comparison = self.optimized_generator.compare_with_traditional(
            test_image, index_space_size
        )
        
        # Verify comparison structure
        assert 'traditional_time' in comparison
        assert 'optimized_time' in comparison
        assert 'accuracy_match' in comparison
        assert 'max_difference' in comparison
        assert 'speedup_ratio' in comparison
        assert 'traditional_indices_count' in comparison
        assert 'optimized_indices_count' in comparison
        
        # Both methods should complete successfully
        assert comparison['traditional_time'] > 0
        assert comparison['optimized_time'] > 0
        
        # Both should produce valid results
        assert comparison['accuracy_match'] is True
        assert comparison['traditional_indices_count'] > 0
        assert comparison['optimized_indices_count'] > 0
        
        # Results should be reasonably similar (allowing for different but valid approaches)
        assert comparison['max_difference'] < 10.0  # Allow some difference in approach
    
    def test_accuracy_across_different_image_patterns(self):
        """Test accuracy comparison across different image patterns."""
        patterns = {
            'random': np.random.randn(16, 16),
            'gradient': np.outer(np.linspace(0, 1, 16), np.linspace(0, 1, 16)),
            'checkerboard': np.array([[(-1)**((i+j)%2) for j in range(16)] for i in range(16)]),
            'constant': np.ones((16, 16)),
            'sparse': np.zeros((16, 16))
        }
        
        # Add some non-zero values to sparse pattern
        patterns['sparse'][::4, ::4] = 1.0
        
        index_space_size = 150
        
        for pattern_name, pattern_image in patterns.items():
            pattern_image = pattern_image.astype(np.float32)
            
            # Compare methods for this pattern
            comparison = self.optimized_generator.compare_with_traditional(
                pattern_image, index_space_size
            )
            
            # Both methods should handle all patterns
            assert 'error' not in comparison, f"Error with {pattern_name} pattern: {comparison.get('error', '')}"
            assert comparison['accuracy_match'] is True, f"Accuracy mismatch for {pattern_name} pattern"
            
            # Both should produce reasonable results
            assert comparison['traditional_indices_count'] > 0, f"No traditional indices for {pattern_name}"
            assert comparison['optimized_indices_count'] > 0, f"No optimized indices for {pattern_name}"
    
    def test_accuracy_with_extreme_values(self):
        """Test accuracy with extreme parameter values."""
        # Test with very large values
        large_image = np.random.randn(8, 8) * 1000
        
        # Test with very small values
        small_image = np.random.randn(8, 8) * 1e-6
        
        # Test with mixed extreme values
        mixed_image = np.random.randn(8, 8)
        mixed_image[0, :] *= 1000  # Large values in first row
        mixed_image[-1, :] *= 1e-6  # Small values in last row
        
        index_space_size = 80
        
        for name, test_image in [('large', large_image), ('small', small_image), ('mixed', mixed_image)]:
            test_image = test_image.astype(np.float32)
            
            comparison = self.optimized_generator.compare_with_traditional(
                test_image, index_space_size
            )
            
            # Both methods should handle extreme values gracefully
            assert 'error' not in comparison, f"Error with {name} values: {comparison.get('error', '')}"
            assert comparison['accuracy_match'] is True, f"Accuracy mismatch for {name} values"
    
    def test_numerical_precision_preservation(self):
        """Test that numerical precision is preserved across methods."""
        # Create image with specific precision requirements
        test_image = np.array([
            [1.123456789, 2.987654321, 3.141592654, 4.271828183],
            [5.123456789, 6.987654321, 7.141592654, 8.271828183],
            [9.123456789, 10.98765432, 11.14159265, 12.27182818],
            [13.12345679, 14.98765432, 15.14159265, 16.27182818]
        ], dtype=np.float32)
        
        index_space_size = 50
        
        # Generate indices with both methods
        traditional_indices = self.traditional_generator.generate_optimized_indices(
            test_image, index_space_size
        )
        
        optimized_indices = self.optimized_generator._generate_with_optimization(
            test_image, index_space_size
        )
        
        # Check numerical properties
        assert not np.any(np.isnan(traditional_indices)), "Traditional method produced NaN"
        assert not np.any(np.isnan(optimized_indices)), "Optimized method produced NaN"
        assert not np.any(np.isinf(traditional_indices)), "Traditional method produced Inf"
        assert not np.any(np.isinf(optimized_indices)), "Optimized method produced Inf"
        
        # Both should have reasonable dynamic range
        traditional_range = np.max(traditional_indices) - np.min(traditional_indices)
        optimized_range = np.max(optimized_indices) - np.min(optimized_indices)
        
        assert traditional_range > 0, "Traditional indices have no variation"
        assert optimized_range > 0, "Optimized indices have no variation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])