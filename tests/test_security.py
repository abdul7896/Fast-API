import subprocess
import pytest

def test_bandit_scan():
    """Run bandit security scan using subprocess"""
    result = subprocess.run(
        ["bandit", "-r", "app", "-ll"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Bandit found security issues:\n{result.stdout}"