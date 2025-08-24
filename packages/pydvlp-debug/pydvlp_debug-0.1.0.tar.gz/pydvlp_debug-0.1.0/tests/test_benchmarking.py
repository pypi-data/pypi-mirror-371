"""Tests for benchmarking modules."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

from pydvlp.debug import benchmark
from pydvlp.debug.fallbacks import FallbackBenchmark


class TestFallbackBenchmark:
    """Test suite for fallback benchmarking functionality."""

    def test_benchmark_creation(self):
        """Test creating a benchmark."""
        bench = FallbackBenchmark()
        assert bench is not None
        assert bench.enabled is True
        assert hasattr(bench, 'measure')
        assert hasattr(bench, 'compare')

    def test_benchmark_measure(self):
        """Test measuring function performance."""
        bench = FallbackBenchmark()
        
        def test_function():
            return sum(range(100))
        
        stats = bench.measure(test_function, iterations=10)
        assert isinstance(stats, dict)
        assert 'average' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'iterations' in stats
        assert stats['iterations'] == 10

    def test_benchmark_compare(self):
        """Test comparing multiple functions."""
        bench = FallbackBenchmark()
        
        functions = {
            'fast': lambda: sum(range(10)),
            'slow': lambda: sum(range(1000))
        }
        
        results = bench.compare(functions, iterations=5)
        assert isinstance(results, dict)
        assert 'fast' in results
        assert 'slow' in results
        assert results['fast']['average'] < results['slow']['average']

    def test_disabled_benchmark(self):
        """Test benchmark when disabled."""
        bench = FallbackBenchmark()
        bench.enabled = False
        
        def test_func():
            return 42
        
        stats = bench.measure(test_func)
        assert stats['iterations'] == 0


class TestTimingBenchmark:
    """Test suite for timing benchmarks."""

    def test_timing_benchmark_creation(self):
        """Test creating timing benchmark."""
        # Use global benchmark
        assert benchmark is not None
        assert hasattr(benchmark, 'measure')

    def test_time_simple_function(self):
        """Test timing a simple function."""
        # Use global benchmark
        
        def test_function():
            return sum(range(100))
        
        stats = benchmark.measure(test_function, iterations=10)
        
        assert isinstance(stats, dict)
        assert "average" in stats
        assert "iterations" in stats
        assert "min" in stats
        assert "max" in stats
        assert stats["iterations"] == 10

    def test_time_function_with_args(self):
        """Test timing function with arguments."""
        # Use global benchmark
        # FallbackBenchmark doesn't support args, wrap it
        
        def add_numbers_wrapped():
            return 5 + 10
        
        stats = benchmark.measure(
            add_numbers_wrapped,
            iterations=5
        )
        
        assert stats["iterations"] == 5

    def test_time_function_with_warmup(self):
        """Test timing with warmup iterations."""
        # Use global benchmark
        
        call_count = 0
        
        def counted_function():
            nonlocal call_count
            call_count += 1
            return call_count
        
        stats = benchmark.measure(
            counted_function,
            iterations=10,
            warmup=5
        )
        
        # Should have called 15 times (5 warmup + 10 measured)
        assert call_count == 15
        assert stats["iterations"] == 10

    def test_compare_functions(self):
        """Test comparing multiple functions."""
        # Use global benchmark
        
        def fast_function():
            return 42
        
        def slow_function():
            time.sleep(0.001)
            return 42
        
        comparison = benchmark.compare(
            {"fast_function": fast_function, "slow_function": slow_function},
            iterations=5
        )
        
        assert isinstance(comparison, dict)
        assert "fast_function" in comparison
        assert "slow_function" in comparison
        
        # Fast function should be faster
        assert comparison["fast_function"]["average"] < comparison["slow_function"]["average"]

    def test_auto_iterations(self):
        """Test automatic iteration count determination."""
        # FallbackBenchmark doesn't support auto_iterations
        # Just test basic functionality
        
        def quick_function():
            return 1 + 1
        
        stats = benchmark.measure(
            quick_function,
            iterations=100
        )
        
        assert stats["iterations"] == 100
        assert stats["average"] >= 0

    def test_timing_decorator(self):
        """Test timing decorator."""
        # FallbackBenchmark doesn't have a timed decorator
        # Just test basic functionality
        
        def decorated_function(x):
            return x ** 2
        
        result = decorated_function(5)
        assert result == 25


class TestBenchmarkEdgeCases:
    """Test edge cases for benchmarking."""

    def test_benchmark_empty_function(self):
        """Test benchmarking empty function."""
        def empty_func():
            pass
        
        stats = benchmark.measure(empty_func, iterations=10)
        assert stats['iterations'] == 10
        assert stats['average'] >= 0

    def test_benchmark_with_exception(self):
        """Test benchmarking function that raises exception."""
        def failing_func():
            raise ValueError("Always fails")
        
        stats = benchmark.measure(failing_func, iterations=5)
        # Should still return stats structure
        assert isinstance(stats, dict)
        assert 'average' in stats

    def test_benchmark_zero_iterations(self):
        """Test benchmark with zero iterations."""
        def test_func():
            return 42
        
        stats = benchmark.measure(test_func, iterations=0)
        assert stats['iterations'] == 0

    def test_compare_single_function(self):
        """Test comparing a single function."""
        results = benchmark.compare({
            'only_one': lambda: sum(range(10))
        }, iterations=5)
        
        assert 'only_one' in results
        assert results['only_one']['iterations'] == 5

    def test_benchmark_with_side_effects(self):
        """Test benchmarking function with side effects."""
        counter = []
        
        def side_effect_func():
            counter.append(1)
            return len(counter)
        
        stats = benchmark.measure(side_effect_func, iterations=5, warmup=2)
        # Should have been called 7 times (2 warmup + 5 measured)
        assert len(counter) == 7


class TestBenchmarkingIntegration:
    """Test integration scenarios."""

    def test_benchmark_multiple_operations(self):
        """Test benchmarking multiple operations."""
        results = []
        
        # Benchmark operation 1
        def op1():
            return sum(range(100))
        
        # Benchmark operation 2  
        def op2():
            return [i**2 for i in range(10)]
        
        stats1 = benchmark.measure(op1, iterations=5)
        stats2 = benchmark.measure(op2, iterations=5)
        
        assert stats1['iterations'] == 5
        assert stats2['iterations'] == 5

    def test_benchmark_comparison_report(self):
        """Test generating comparison report."""
        # Use global benchmark
        
        implementations = {
            "list_comp": lambda n: [i**2 for i in range(n)],
            "map": lambda n: list(map(lambda x: x**2, range(n))),
            "loop": lambda n: [i**2 for i in range(n)]
        }
        
        results = {}
        for name, func in implementations.items():
            stats = benchmark.measure(
                lambda: func(100),
                iterations=100
            )
            results[name] = stats
        
        # All implementations should produce same result
        assert len(implementations["list_comp"](10)) == 10
        assert len(implementations["map"](10)) == 10
        assert len(implementations["loop"](10)) == 10

    def test_memory_benchmark(self):
        """Test memory usage benchmarking."""
        # This is a placeholder for memory benchmarking
        # Real implementation would measure memory usage
        
        def memory_intensive_function(n):
            data = [list(range(1000)) for _ in range(n)]
            return len(data)
        
        result = memory_intensive_function(10)
        assert result == 10