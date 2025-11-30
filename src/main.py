"""Main entry point for Code Archaeologist AI Agent."""
import asyncio
import json
from pathlib import Path
from tools.git_analyzer import analyze_git_history
from tools.cve_scanner import scan_dependencies_for_cves
from tools.doc_parser import analyze_documentation
import config


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


async def main():
    """Run basic tool analysis."""
    print("\nCODE ARCHAEOLOGIST AI AGENT")
    print("Technical Debt Detection System")
    
    # Get repository path (current directory for now)
    repo_path = "."
    
    # Run Git Analysis
    print_section("GIT HISTORY ANALYSIS")
    git_results = analyze_git_history(repo_path, lookback_days=config.GIT_LOOKBACK_DAYS)
    print(f"Risk Score: {git_results.get('risk_score', 0)}/100")
    print(f"Total Commits: {git_results.get('total_commits', 0)}")
    print(f"High Churn Files: {len(git_results.get('high_churn_files', []))}")
    
    # Run CVE Scan
    print_section("SECURITY VULNERABILITY SCAN")
    cve_results = scan_dependencies_for_cves(repo_path, config.NVD_API_KEY)
    print(f"Total Dependencies: {cve_results.get('total_dependencies', 0)}")
    print(f"Vulnerabilities Found: {len(cve_results.get('vulnerabilities', []))}")
    severity = cve_results.get('severity_summary', {})
    print(f"  - Critical: {severity.get('CRITICAL', 0)}")
    print(f"  - High: {severity.get('HIGH', 0)}")
    print(f"  - Medium: {severity.get('MEDIUM', 0)}")
    print(f"  - Low: {severity.get('LOW', 0)}")
    
    # Run Documentation Analysis
    print_section("DOCUMENTATION ANALYSIS")
    doc_results = analyze_documentation(repo_path)
    print(f"Documentation Coverage: {doc_results.get('coverage', 0):.1%}")
    print(f"Has README: {doc_results.get('has_readme', False)}")
    print(f"Files Analyzed: {doc_results.get('total_files', 0)}")
    print(f"Documented Files: {doc_results.get('documented_files', 0)}")
    print(f"Function Coverage: {doc_results.get('function_coverage', 0):.1%}")
    
    # Summary
    print_section("ANALYSIS COMPLETE")
    print("\nNext Steps:")
    print("  1. Review high-churn files for refactoring opportunities")
    print("  2. Update vulnerable dependencies")
    print("  3. Improve documentation coverage")
    print()
    
    return {
        "git": git_results,
        "cve": cve_results,
        "docs": doc_results
    }


if __name__ == "__main__":
    results = asyncio.run(main())