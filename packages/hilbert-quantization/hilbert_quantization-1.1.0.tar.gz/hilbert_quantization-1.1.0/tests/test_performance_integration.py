"""
Integration tests for performance optimization with existing system components.

Tests the integration of performance monitoring with the complete
generator-based index optimization system.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from hilbert_quantization.core.optimized_index_generator import OptimizedIndexGenerator
from hilbert_quantization.core.hierarchical_generator import HierarchicalGenerator
from hilbert_quantization.core.generator_tree_builder import GeneratorTreeBuilder
from hilbert_quantization.core.index_extractor import IndexExtractor
from hilbert_quantization.models import OptimizationMetrics


class TestPerformanceIntegration:
    """Integration tests for performance monitoring with the complete system."""
    
    def test_end_to_end_performance_monitoring(self):
        """Test complete end-to-end performance monitoring."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Create a valid test image (power of 2 dimensions)
        image = np.random.rand(16, 16)
        index_space_size = 64
        
        # Mock the internal components to avoid complex setup
        with patch.object(generator, '_generate_with_optimization') as mock_opt, \
             patch.object(generator, 'fallback_to_traditional') as mock_trad:
            
            # Set up mock returns
            mock_opt.return_value = np.random.rand(64)
            mock_trad.return_value = np.random.rand(64)
            
            # Generate indices with performance monitoring
            result = generator.generate_optimized_indices(image, index_space_size)
            
            # Verify result
            assert isinstance(result, np.ndarray)
            assert len(result) == 64
            
            # Verify performance monitoring was used
            assert len(generator.auto_fallback_manager.performance_history) > 0
    
    def test_performance_report_integration(self):
        """Test performance report generation with real components."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        image = np.random.rand(8, 8)  # Small image for faster testing
        index_space_size = 32
        
        # Mock to control the behavior
        with patch.object(generator, '_generate_with_optimization') as mock_opt, \
             patch.object(generator, 'fallback_to_traditional') as mock_trad:
            
            mock_opt.return_value = np.random.rand(32)
            mock_trad.return_value = np.random.rand(32)
            
            # Generate performance report
            report = generator.get_performance_report(image, index_space_size)
            
            # Verify report structure
            assert 'summary' in report
            assert 'timing' in report
            assert 'memory' in report
            assert 'quality' in report
            
            # Verify summary contains expected fields
            summary = report['summary']
            assert 'optimization_recommended' in summary
            assert 'speedup_ratio' in summary
            assert 'accuracy_score' in summary
            assert 'memory_change' in summary
    
    def test_automatic_fallback_integration(self):
        """Test automatic fallback decision making in integrated system."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Set strict thresholds to force fallback
        generator.set_performance_thresholds(
            min_speedup=10.0,  # Unrealistically high
            min_accuracy=0.999,  # Very strict
            max_memory_increase=0.001  # Very strict
        )
        
        image = np.random.rand(8, 8)
        index_space_size = 32
        
        with patch.object(generator, 'fallback_to_traditional') as mock_fallback:
            mock_fallback.return_value = np.random.rand(32)
            
            # Should use fallback due to strict thresholds
            result = generator.generate_optimized_indices(image, index_space_size)
            
            # Verify fallback was called
            assert mock_fallback.called
            assert isinstance(result, np.ndarray)
    
    def test_performance_history_accumulation(self):
        """Test that performance history accumulates over multiple calls."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        image = np.random.rand(8, 8)
        index_space_size = 32
        
        with patch.object(generator, '_generate_with_optimization') as mock_opt, \
             patch.object(generator, 'fallback_to_traditional') as mock_trad:
            
            mock_opt.return_value = np.random.rand(32)
            mock_trad.return_value = np.random.rand(32)
            
            # Make multiple calls
            for i in range(3):
                generator.generate_optimized_indices(image, index_space_size)
            
            # Verify history accumulation
            history_length = len(generator.auto_fallback_manager.performance_history)
            assert history_length == 3
            
            # Verify summary reflects multiple measurements
            summary = generator.get_historical_performance_summary()
            assert summary['total_measurements'] == 3
    
    def test_performance_monitoring_disabled(self):
        """Test system behavior when performance monitoring is disabled."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=False)
        
        image = np.random.rand(8, 8)
        index_space_size = 32
        
        with patch.object(generator, '_generate_with_optimization') as mock_opt:
            mock_opt.return_value = np.random.rand(32)
            
            # Should work without performance monitoring
            result = generator.generate_optimized_indices(image, index_space_size)
            
            assert isinstance(result, np.ndarray)
            assert len(result) == 32
            
            # Performance report should indicate monitoring is disabled
            report = generator.get_performance_report(image, index_space_size)
            assert 'error' in report
            assert 'Performance monitoring not enabled' in report['error']
    
    def test_memory_monitoring_integration(self):
        """Test memory monitoring integration with real operations."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Use larger image to potentially see memory differences
        image = np.random.rand(32, 32)
        index_space_size = 128
        
        with patch.object(generator, '_generate_with_optimization') as mock_opt, \
             patch.object(generator, 'fallback_to_traditional') as mock_trad:
            
            mock_opt.return_value = np.random.rand(128)
            mock_trad.return_value = np.random.rand(128)
            
            # Generate performance report
            report = generator.get_performance_report(image, index_space_size)
            
            # Verify memory metrics are present
            assert 'memory' in report
            memory_info = report['memory']
            assert 'traditional_memory_mb' in memory_info
            assert 'generator_memory_mb' in memory_info
            assert 'memory_saved_mb' in memory_info
    
    def test_accuracy_comparison_integration(self):
        """Test accuracy comparison with controlled results."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        image = np.random.rand(8, 8)
        index_space_size = 32
        
        # Create controlled results for accuracy testing
        base_result = np.random.rand(32)
        similar_result = base_result + np.random.normal(0, 0.01, 32)  # Very similar
        
        with patch.object(generator, '_generate_with_optimization') as mock_opt, \
             patch.object(generator, 'fallback_to_traditional') as mock_trad:
            
            mock_trad.return_value = base_result
            mock_opt.return_value = similar_result
            
            # Generate performance report
            report = generator.get_performance_report(image, index_space_size)
            
            # Verify accuracy is high (should be close to 1.0)
            quality = report['quality']
            assert quality['accuracy_comparison'] > 0.9
    
    def test_performance_threshold_adaptation(self):
        """Test that performance thresholds can be adapted during runtime."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Start with lenient thresholds
        generator.set_performance_thresholds(
            min_speedup=1.1,
            min_accuracy=0.90,
            max_memory_increase=0.2
        )
        
        # Verify thresholds were set
        assert generator.auto_fallback_manager.min_speedup == 1.1
        assert generator.auto_fallback_manager.min_accuracy == 0.90
        
        # Change to strict thresholds
        generator.set_performance_thresholds(
            min_speedup=2.0,
            min_accuracy=0.99,
            max_memory_increase=0.05
        )
        
        # Verify thresholds were updated
        assert generator.auto_fallback_manager.min_speedup == 2.0
        assert generator.auto_fallback_manager.min_accuracy == 0.99
    
    def test_performance_history_reset_integration(self):
        """Test performance history reset functionality."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        image = np.random.rand(8, 8)
        index_space_size = 32
        
        with patch.object(generator, '_generate_with_optimization') as mock_opt, \
             patch.object(generator, 'fallback_to_traditional') as mock_trad:
            
            mock_opt.return_value = np.random.rand(32)
            mock_trad.return_value = np.random.rand(32)
            
            # Generate some history
            generator.generate_optimized_indices(image, index_space_size)
            generator.generate_optimized_indices(image, index_space_size)
            
            # Verify history exists
            assert len(generator.auto_fallback_manager.performance_history) == 2
            
            # Reset history
            generator.reset_performance_history()
            
            # Verify history is cleared
            assert len(generator.auto_fallback_manager.performance_history) == 0
            
            # Verify summary reflects empty history
            summary = generator.get_historical_performance_summary()
            assert 'No performance data available' in summary['status']


if __name__ == '__main__':
    pytest.main([__file__])