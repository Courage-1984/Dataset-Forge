from dataset_forge.utils.monitoring import (
    HealthChecker,
    ErrorTracker,
    PerformanceAnalytics,
)


def test_health_checker_runs():
    """Test that HealthChecker returns expected keys."""
    checker = HealthChecker()
    results = checker.run_all()
    assert isinstance(results, dict)
    assert "ram_total_gb" in results
    assert "disk_total_gb" in results
    assert "cuda_ok" in results


def test_error_tracker():
    """Test that ErrorTracker logs errors and returns summary."""
    tracker = ErrorTracker()
    try:
        raise RuntimeError("fail")
    except Exception as e:
        tracker.log_error(e, critical=False)
    summary = tracker.summary()
    assert summary["count"] == 1
    assert summary["by_type"].get("RuntimeError") == 1


def test_performance_analytics():
    """Test that PerformanceAnalytics records and summarizes operations."""
    analytics = PerformanceAnalytics()
    analytics.record_operation("test", 1.23)
    summary = analytics.summary()
    assert "test" in summary
    assert summary["test"]["count"] == 1
