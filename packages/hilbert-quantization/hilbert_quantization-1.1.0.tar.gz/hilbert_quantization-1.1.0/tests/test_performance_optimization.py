"""
Performance optimization and monitoring tests.

Tests for performance monitoring, automatic fallback, and optimization metrics
in the generator-based index optimization system.
"""

import pytest
import numpy as np
import time
from unittest.mock import Mock, patch

from hilbert_quantization.core.optimized_index_generator import OptimizedIndexGenerator
from hilbert_quantization.models import OptimizationMetrics
from hilbert_quantization.utils.performance_monitor import PerformanceMonitor, AutoFallbackManager


class TestOptimizationMetrics:
    """Test OptimizationMetrics data structure."""
    
    def test_optimization_metrics_creation(self):
        """Test basic OptimizationMetrics creation and validation."""
        metrics = OptimizationMetrics(
            traditional_calculation_time=1.0,
            generator_based_time=0.5,
            memory_usage_reduction=0.2,
            accuracy_comparison=0.98,
            traditional_memory_mb=100.0,
            generator_memory_mb=80.0
        )
        
        assert metrics.traditional_calculation_time == 1.0
        assert metrics.generator_based_time == 0.5
        assert metrics.speedup_ratio == 2.0  # Calculated in __post_init__
        assert metrics.memory_usage_reduction == 0.2  # Calculated in __post_init__
        assert metrics.optimization_successful == True
    
    def test_optimization_metrics_unsuccessful(self):
        """Test OptimizationMetrics when optimization is not successful."""
        metrics = OptimizationMetrics(
            traditional_calculation_time=1.0,
            generator_based_time=1.5,  # Slower than traditional
            memory_usage_reduction=-0.1,  # Uses more memory
            accuracy_comparison=0.90,  # Lower accuracy
            traditional_memory_mb=100.0,
            generator_memory_mb=110.0
        )
        
        assert metrics.speedup_ratio < 1.0
        assert metrics.optimization_successful == False
    
    def test_optimization_metrics_with_fallback_reason(self):
        """Test OptimizationMetrics with fallback reason."""
        metrics = OptimizationMetrics(
            traditional_calculation_time=1.0,
            generator_based_time=0.5,
            memory_usage_reduction=0.2,
            accuracy_comparison=0.98,
            fallback_reason="Test fallback"
        )
        
        assert metrics.fallback_reason == "Test fallback"


class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality."""
    
    def test_performance_monitor_creation(self):
        """Test PerformanceMonitor initialization."""
        monitor = PerformanceMonitor()
        assert monitor.process is not None
        assert monitor.baseline_memory >= 0
    
    def test_measure_performance_context_manager(self):
        """Test performance measurement context manager."""
        monitor = PerformanceMonitor()
        
        with monitor.measure_performance("test_operation") as metrics:
            time.sleep(0.01)  # Small delay to measure
            assert metrics['operation_name'] == "test_operation"
        
        assert metrics['duration_seconds'] > 0
        assert metrics['start_time'] > 0
        assert metrics['end_time'] > metrics['start_time']
        assert 'memory_delta_mb' in metrics
    
    def test_compare_approaches_success(self):
        """Test comparing two successful approaches."""
        monitor = PerformanceMonitor()
        
        def slow_func():
            time.sleep(0.01)
            return np.array([1, 2, 3, 4])
        
        def fast_func():
            time.sleep(0.005)
            return np.array([1, 2, 3, 4])
        
        metrics = monitor.compare_approaches(slow_func, fast_func)
        
        assert isinstance(metrics, OptimizationMetrics)
        assert metrics.traditional_calculation_time > 0
        assert metrics.generator_based_time > 0
        assert metrics.accuracy_comparison == 1.0  # Identical results
        assert metrics.speedup_ratio > 1.0  # Fast function should be faster
    
    def test_compare_approaches_with_failure(self):
        """Test comparing approaches when one fails."""
        monitor = PerformanceMonitor()
        
        def working_func():
            return np.array([1, 2, 3, 4])
        
        def failing_func():
            raise ValueError("Test error")
        
        metrics = monitor.compare_approaches(working_func, failing_func)
        
        assert isinstance(metrics, OptimizationMetrics)
        assert metrics.accuracy_comparison == 0.0
        assert metrics.fallback_reason is not None
        assert "Test error" in metrics.fallback_reason
    
    def test_numpy_array_comparison(self):
        """Test numpy array accuracy comparison."""
        monitor = PerformanceMonitor()
        
        arr1 = np.array([1.0, 2.0, 3.0, 4.0])
        arr2 = np.array([1.0, 2.0, 3.0, 4.0])
        arr3 = np.array([1.1, 2.1, 3.1, 4.1])
        
        # Identical arrays
        accuracy = monitor._compare_numpy_arrays(arr1, arr2)
        assert accuracy == 1.0
        
        # Similar arrays
        accuracy = monitor._compare_numpy_arrays(arr1, arr3)
        assert 0.8 < accuracy < 1.0
        
        # Different shapes
        arr4 = np.array([1.0, 2.0])
        accuracy = monitor._compare_numpy_arrays(arr1, arr4)
        assert accuracy == 0.0
    
    def test_should_use_optimization_decision(self):
        """Test optimization decision logic."""
        monitor = PerformanceMonitor()
        
        # Good optimization
        good_metrics = OptimizationMetrics(
            traditional_calculation_time=1.0,
            generator_based_time=0.5,
            memory_usage_reduction=0.1,
            accuracy_comparison=0.98
        )
        assert monitor.should_use_optimization(good_metrics) is True
        
        # Poor optimization
        poor_metrics = OptimizationMetrics(
            traditional_calculation_time=1.0,
            generator_based_time=1.2,  # Slower
            memory_usage_reduction=-0.2,  # Uses more memory
            accuracy_comparison=0.90  # Lower accuracy
        )
        assert monitor.should_use_optimization(poor_metrics) is False
    
    def test_create_performance_report(self):
        """Test performance report generation."""
        monitor = PerformanceMonitor()
        
        metrics = OptimizationMetrics(
            traditional_calculation_time=1.0,
            generator_based_time=0.5,
            memory_usage_reduction=0.2,
            accuracy_comparison=0.98,
            traditional_memory_mb=100.0,
            generator_memory_mb=80.0
        )
        
        report = monitor.create_performance_report(metrics)
        
        assert 'summary' in report
        assert 'timing' in report
        assert 'memory' in report
        assert 'quality' in report
        
        assert report['summary']['optimization_recommended'] == True
        assert '2.00x' in report['summary']['speedup_ratio']
        assert report['quality']['accuracy_comparison'] == 0.98


class TestAutoFallbackManager:
    """Test AutoFallbackManager functionality."""
    
    def test_auto_fallback_manager_creation(self):
        """Test AutoFallbackManager initialization."""
        manager = AutoFallbackManager()
        assert manager.performance_history == []
        assert manager.history_size == 100
        assert manager.min_speedup == 1.1
        assert manager.min_accuracy == 0.95
    
    def test_record_performance(self):
        """Test recording performance metrics."""
        manager = AutoFallbackManager(performance_history_size=5)
        
        for i in range(10):
            metrics = OptimizationMetrics(
                traditional_calculation_time=1.0,
                generator_based_time=0.5,
                memory_usage_reduction=0.1,
                accuracy_comparison=0.98
            )
            manager.record_performance(metrics)
        
        # Should keep only last 5 records
        assert len(manager.performance_history) == 5
    
    def test_should_use_optimization_with_history(self):
        """Test optimization decision based on historical data."""
        manager = AutoFallbackManager()
        
        # Add good performance history
        for _ in range(5):
            good_metrics = OptimizationMetrics(
                traditional_calculation_time=1.0,
                generator_based_time=0.4,  # Good speedup
                memory_usage_reduction=0.1,
                accuracy_comparison=0.98  # Good accuracy
            )
            manager.record_performance(good_metrics)
        
        assert manager.should_use_optimization() == True
        
        # Add poor performance history
        for _ in range(10):
            poor_metrics = OptimizationMetrics(
                traditional_calculation_time=1.0,
                generator_based_time=1.5,  # Poor speedup
                memory_usage_reduction=0.1,
                accuracy_comparison=0.90  # Poor accuracy
            )
            manager.record_performance(poor_metrics)
        
        assert manager.should_use_optimization() == False
    
    def test_get_performance_summary(self):
        """Test performance summary generation."""
        manager = AutoFallbackManager()
        
        # Empty history
        summary = manager.get_performance_summary()
        assert 'No performance data available' in summary['status']
        
        # Add some metrics
        for i in range(3):
            metrics = OptimizationMetrics(
                traditional_calculation_time=1.0,
                generator_based_time=0.5,
                memory_usage_reduction=0.1,
                accuracy_comparison=0.98
            )
            manager.record_performance(metrics)
        
        summary = manager.get_performance_summary()
        assert summary['total_measurements'] == 3
        assert '2.00x' in summary['average_speedup']
        assert '0.980' in summary['average_accuracy']


class TestOptimizedIndexGeneratorPerformance:
    """Test OptimizedIndexGenerator performance monitoring integration."""
    
    def test_optimized_generator_with_performance_monitoring(self):
        """Test OptimizedIndexGenerator with performance monitoring enabled."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        assert generator.enable_auto_fallback == True
        assert generator.performance_monitor is not None
        assert generator.auto_fallback_manager is not None
    
    def test_optimized_generator_without_performance_monitoring(self):
        """Test OptimizedIndexGenerator with performance monitoring disabled."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=False)
        
        assert generator.enable_auto_fallback == False
        assert generator.performance_monitor is not None  # Always available
        assert generator.auto_fallback_manager == None
    
    def test_performance_report_generation(self):
        """Test performance report generation."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Create test image
        image = np.random.rand(16, 16)
        index_space_size = 64
        
        # Mock the performance measurement to avoid actual computation
        with patch.object(generator, '_measure_performance_comparison') as mock_measure:
            mock_metrics = OptimizationMetrics(
                traditional_calculation_time=1.0,
                generator_based_time=0.5,
                memory_usage_reduction=0.2,
                accuracy_comparison=0.98
            )
            mock_measure.return_value = mock_metrics
            
            report = generator.get_performance_report(image, index_space_size)
            
            assert 'summary' in report
            assert 'timing' in report
            assert 'memory' in report
            assert 'quality' in report
    
    def test_performance_report_without_monitoring(self):
        """Test performance report when monitoring is disabled."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=False)
        
        image = np.random.rand(16, 16)
        index_space_size = 64
        
        report = generator.get_performance_report(image, index_space_size)
        assert 'error' in report
        assert 'Performance monitoring not enabled' in report['error']
    
    def test_historical_performance_summary(self):
        """Test historical performance summary."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Initially empty
        summary = generator.get_historical_performance_summary()
        assert 'No performance data available' in summary['status']
        
        # Add some performance data
        metrics = OptimizationMetrics(
            traditional_calculation_time=1.0,
            generator_based_time=0.5,
            memory_usage_reduction=0.2,
            accuracy_comparison=0.98
        )
        generator.auto_fallback_manager.record_performance(metrics)
        
        summary = generator.get_historical_performance_summary()
        assert summary['total_measurements'] == 1
        assert 'Use optimization' in summary['current_recommendation']
    
    def test_reset_performance_history(self):
        """Test resetting performance history."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Add some data
        metrics = OptimizationMetrics(
            traditional_calculation_time=1.0,
            generator_based_time=0.5,
            memory_usage_reduction=0.2,
            accuracy_comparison=0.98
        )
        generator.auto_fallback_manager.record_performance(metrics)
        
        assert len(generator.auto_fallback_manager.performance_history) == 1
        
        generator.reset_performance_history()
        assert len(generator.auto_fallback_manager.performance_history) == 0
    
    def test_set_performance_thresholds(self):
        """Test setting performance thresholds."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        generator.set_performance_thresholds(
            min_speedup=1.5,
            min_accuracy=0.99,
            max_memory_increase=0.05
        )
        
        assert generator.auto_fallback_manager.min_speedup == 1.5
        assert generator.auto_fallback_manager.min_accuracy == 0.99


class TestPerformanceBenchmarks:
    """Performance benchmark tests comparing generator vs traditional approaches."""
    
    def test_small_image_performance(self):
        """Test performance with small images."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Small 8x8 image
        image = np.random.rand(8, 8)
        index_space_size = 32
        
        # Mock both approaches to control timing
        with patch.object(generator, 'fallback_to_traditional') as mock_traditional, \
             patch.object(generator, '_generate_with_optimization') as mock_optimized:
            
            mock_traditional.return_value = np.random.rand(32)
            mock_optimized.return_value = np.random.rand(32)
            
            # Simulate traditional being slower
            def slow_traditional(*args, **kwargs):
                time.sleep(0.01)
                return np.random.rand(32)
            
            def fast_optimized(*args, **kwargs):
                time.sleep(0.005)
                return np.random.rand(32)
            
            mock_traditional.side_effect = slow_traditional
            mock_optimized.side_effect = fast_optimized
            
            # Test performance measurement
            metrics = generator._measure_performance_comparison(image, index_space_size)
            
            assert isinstance(metrics, OptimizationMetrics)
            assert metrics.traditional_calculation_time > 0
            assert metrics.generator_based_time > 0
    
    def test_medium_image_performance(self):
        """Test performance with medium-sized images."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Medium 32x32 image
        image = np.random.rand(32, 32)
        index_space_size = 128
        
        with patch.object(generator, 'fallback_to_traditional') as mock_traditional, \
             patch.object(generator, '_generate_with_optimization') as mock_optimized:
            
            mock_traditional.return_value = np.random.rand(128)
            mock_optimized.return_value = np.random.rand(128)
            
            metrics = generator._measure_performance_comparison(image, index_space_size)
            
            assert isinstance(metrics, OptimizationMetrics)
            assert metrics.accuracy_comparison >= 0.0
    
    def test_large_image_performance(self):
        """Test performance with large images."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Large 64x64 image
        image = np.random.rand(64, 64)
        index_space_size = 256
        
        with patch.object(generator, 'fallback_to_traditional') as mock_traditional, \
             patch.object(generator, '_generate_with_optimization') as mock_optimized:
            
            mock_traditional.return_value = np.random.rand(256)
            mock_optimized.return_value = np.random.rand(256)
            
            metrics = generator._measure_performance_comparison(image, index_space_size)
            
            assert isinstance(metrics, OptimizationMetrics)
    
    def test_memory_usage_comparison(self):
        """Test memory usage comparison between approaches."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        image = np.random.rand(16, 16)
        index_space_size = 64
        
        # Mock to simulate different memory usage
        with patch.object(generator.performance_monitor, '_get_memory_usage_mb') as mock_memory:
            # Simulate memory usage pattern: start low, traditional uses more, optimized uses less
            memory_values = [50.0, 80.0, 60.0, 70.0]  # start, after traditional, after optimized, end
            mock_memory.side_effect = memory_values
            
            with patch.object(generator, 'fallback_to_traditional') as mock_traditional, \
                 patch.object(generator, '_generate_with_optimization') as mock_optimized:
                
                mock_traditional.return_value = np.random.rand(64)
                mock_optimized.return_value = np.random.rand(64)
                
                metrics = generator._measure_performance_comparison(image, index_space_size)
                
                assert isinstance(metrics, OptimizationMetrics)
                assert metrics.traditional_memory_mb > 0
                assert metrics.generator_memory_mb > 0
    
    def test_accuracy_preservation_benchmark(self):
        """Test that optimization preserves accuracy."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        image = np.random.rand(16, 16)
        index_space_size = 64
        
        # Create identical results to test accuracy measurement
        identical_result = np.random.rand(64)
        
        with patch.object(generator, 'fallback_to_traditional') as mock_traditional, \
             patch.object(generator, '_generate_with_optimization') as mock_optimized:
            
            mock_traditional.return_value = identical_result
            mock_optimized.return_value = identical_result.copy()
            
            metrics = generator._measure_performance_comparison(image, index_space_size)
            
            assert metrics.accuracy_comparison == 1.0  # Perfect accuracy
    
    def test_fallback_decision_benchmark(self):
        """Test automatic fallback decision making."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        image = np.random.rand(16, 16)
        index_space_size = 64
        
        # Simulate poor optimization performance
        with patch.object(generator, '_measure_performance_comparison') as mock_measure:
            poor_metrics = OptimizationMetrics(
                traditional_calculation_time=0.5,
                generator_based_time=1.0,  # Slower than traditional
                memory_usage_reduction=-0.1,  # Uses more memory
                accuracy_comparison=0.90  # Lower accuracy
            )
            mock_measure.return_value = poor_metrics
            
            with patch.object(generator, 'fallback_to_traditional') as mock_fallback:
                mock_fallback.return_value = np.random.rand(64)
                
                # Should use fallback due to poor performance
                result = generator.generate_optimized_indices(image, index_space_size)
                
                assert mock_fallback.called
                assert len(result) == 64
    
    def test_performance_threshold_sensitivity(self):
        """Test sensitivity to different performance thresholds."""
        generator = OptimizedIndexGenerator(enable_auto_fallback=True)
        
        # Test with strict thresholds
        generator.set_performance_thresholds(
            min_speedup=2.0,  # Very strict
            min_accuracy=0.99,  # Very strict
            max_memory_increase=0.01  # Very strict
        )
        
        # Metrics that would normally be acceptable
        moderate_metrics = OptimizationMetrics(
            traditional_calculation_time=1.0,
            generator_based_time=0.7,  # 1.43x speedup (less than 2.0)
            memory_usage_reduction=0.05,
            accuracy_comparison=0.97  # Less than 0.99
        )
        
        should_optimize = generator.performance_monitor.should_use_optimization(
            moderate_metrics, min_speedup=2.0, min_accuracy=0.99, max_memory_increase=0.01
        )
        assert should_optimize == False  # Should reject due to strict thresholds
        
        # Test with lenient thresholds
        generator.set_performance_thresholds(
            min_speedup=1.1,
            min_accuracy=0.90,
            max_memory_increase=0.2
        )
        
        should_optimize = generator.performance_monitor.should_use_optimization(
            moderate_metrics, min_speedup=1.1, min_accuracy=0.90, max_memory_increase=0.2
        )
        assert should_optimize == True  # Should accept with lenient thresholds


if __name__ == '__main__':
    pytest.main([__file__])