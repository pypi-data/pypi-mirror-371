"""
Simple validation test to verify the test framework is working.
"""

import pytest
import numpy as np
from hilbert_quantization.core.optimized_index_generator import OptimizedIndexGenerator
from hilbert_quantization.core.index_generator import HierarchicalIndexGeneratorImpl


def test_simple_validation():
    """Simple test to verify both generators work."""
    optimized_gen = OptimizedIndexGenerator(enable_auto_fallback=False)
    traditional_gen = HierarchicalIndexGeneratorImpl()
    
    # Create small test image
    test_image = np.random.randn(4, 4).astype(np.float32)
    index_space_size = 20
    
    # Test traditional generator
    traditional_indices = traditional_gen.generate_optimized_indices(test_image, index_space_size)
    assert len(traditional_indices) > 0
    assert np.all(np.isfinite(traditional_indices))
    
    # Test optimized generator
    optimized_indices = optimized_gen._generate_with_optimization(test_image, index_space_size)
    assert len(optimized_indices) > 0
    assert np.all(np.isfinite(optimized_indices))
    
    print("Simple validation test passed!")


if __name__ == "__main__":
    test_simple_validation()