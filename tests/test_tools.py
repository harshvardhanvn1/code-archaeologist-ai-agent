"""Basic tests for custom tools."""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.git_analyzer import analyze_git_history
from tools.cve_scanner import scan_dependencies_for_cves
from tools.doc_parser import analyze_documentation


def test_git_analyzer_returns_structure():
    """Test that git analyzer returns expected data structure."""
    result = analyze_git_history(".", lookback_days=30)
    
    assert "risk_score" in result
    assert "total_commits" in result
    assert "high_churn_files" in result
    assert isinstance(result["risk_score"], (int, float))


def test_cve_scanner_returns_structure():
    """Test that CVE scanner returns expected data structure."""
    result = scan_dependencies_for_cves(".")
    
    assert "vulnerabilities" in result
    assert "total_dependencies" in result
    assert "severity_summary" in result
    assert isinstance(result["vulnerabilities"], list)


def test_doc_parser_returns_structure():
    """Test that documentation parser returns expected data structure."""
    result = analyze_documentation(".")
    
    assert "coverage" in result
    assert "total_files" in result
    assert "documented_files" in result
    assert isinstance(result["coverage"], float)
    assert 0 <= result["coverage"] <= 1


def test_git_analyzer_nonexistent_repo():
    """Test git analyzer handles non-existent repos gracefully."""
    result = analyze_git_history("/nonexistent/path")
    
    assert "error" in result or result["total_commits"] == 0


def test_cve_scanner_empty_dependencies():
    """Test CVE scanner handles repos without dependency files."""
    result = scan_dependencies_for_cves("/tmp")
    
    assert result["total_dependencies"] == 0
    assert result["scan_status"] == "no_dependency_files_found"
