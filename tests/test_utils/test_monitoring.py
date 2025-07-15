from dataset_forge.utils.monitoring import HealthChecker


def test_health_checker_runs():
    checker = HealthChecker()
    results = checker.run_all()
    assert isinstance(results, dict)
    assert "ram_total_gb" in results
