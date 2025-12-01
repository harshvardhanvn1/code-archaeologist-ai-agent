"""Command-line interface for Code Archaeologist AI Agent."""
import asyncio
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from src.agents.orchestrator import TechDebtOrchestrator
from src import config


def print_banner():
    """Print application banner."""
    print("\n" + "="*70)
    print("  CODE ARCHAEOLOGIST AI AGENT")
    print("  Technical Debt Detection & Analysis System")
    print("  Multi-Agent AI with Observability & Evaluation")
    print("="*70 + "\n")


def print_summary(results: dict):
    """Print human-readable summary of results."""
    if results["status"] != "success":
        print(f"\nERROR: {results.get('error', 'Unknown error')}\n")
        return
    
    analysis = results["results"]
    impact = analysis["impact_analysis"]
    report = analysis["final_report"]
    evaluation = results.get("evaluation", {})
    human_review = results.get("human_review", {})
    
    print("\nEXECUTIVE SUMMARY")
    print("-" * 70)
    print(f"Repository: {results['repo_path']}")
    print(f"Analysis Type: {results['analysis_type']}")
    print(f"Correlation ID: {results['correlation_id']}")
    print(f"Timestamp: {results['timestamp']}")
    
    print(f"\nImpact Score: {impact['impact_score']}/100")
    print(f"Severity: {impact['severity'].upper()}")
    print(f"Total Issues: {report['executive_summary']['total_issues']}")
    
    # Show evaluation scores if available
    if evaluation.get("overall_score"):
        print(f"\nQUALITY EVALUATION (LLM-as-Judge)")
        print("-" * 70)
        print(f"Overall Quality Score: {evaluation['overall_score']}/100")
        
        if evaluation.get("dimension_scores"):
            dims = evaluation["dimension_scores"]
            print(f"  Completeness: {dims.get('completeness', 0)}/100")
            print(f"  Accuracy: {dims.get('accuracy', 0)}/100")
            print(f"  Actionability: {dims.get('actionability', 0)}/100")
            print(f"  Clarity: {dims.get('clarity', 0)}/100")
    
    
    print("\nKEY RISKS:")
    for i, risk in enumerate(impact['key_risks'], 1):
        print(f"  {i}. {risk}")
    
    print("\nRECOMMENDATIONS:")
    for i, rec in enumerate(impact['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print("\nDETAILED FINDINGS")
    print("-" * 70)
    
    # Git Analysis
    git = analysis["parallel_analysis"]["git_analysis"]
    print(f"\nGit History Analysis:")
    print(f"  Risk Score: {git['risk_score']}/100")
    print(f"  Total Commits (last {git['lookback_days']} days): {git['total_commits']}")
    print(f"  High Churn Files: {len(git['high_churn_files'])}")
    
    # Security Analysis
    cve = analysis["parallel_analysis"]["cve_analysis"]
    print(f"\nSecurity Vulnerability Scan:")
    print(f"  Total Dependencies: {cve['total_dependencies']}")
    print(f"  Vulnerabilities: {len(cve['vulnerabilities'])}")
    severity = cve['severity_summary']
    print(f"    Critical: {severity['CRITICAL']}")
    print(f"    High: {severity['HIGH']}")
    print(f"    Medium: {severity['MEDIUM']}")
    print(f"    Low: {severity['LOW']}")
    
    # Documentation Analysis
    doc = analysis["parallel_analysis"]["documentation_analysis"]
    print(f"\nDocumentation Analysis:")
    print(f"  Coverage: {doc['coverage']:.1%}")
    print(f"  Has README: {doc['has_readme']}")
    print(f"  Total Files: {doc['total_files']}")
    print(f"  Documented Files: {doc['documented_files']}")
    print(f"  Function Coverage: {doc['function_coverage']:.1%}")
    
    print("\n" + "="*70 + "\n")


async def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Code Archaeologist AI Agent - Technical Debt Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Analyze current directory:
    python -m src.main
  
  Analyze with human review:
    python -m src.main --human-review
  
  Save output to file:
    python -m src.main --output report.json
  
  Quick analysis:
    python -m src.main --analysis-type quick
        """
    )
    
    parser.add_argument(
        "--repo-path",
        type=str,
        default=".",
        help="Path to repository to analyze (default: current directory)"
    )
    
    parser.add_argument(
        "--analysis-type",
        type=str,
        choices=["quick", "comprehensive", "security-focused"],
        default="comprehensive",
        help="Type of analysis to perform (default: comprehensive)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Path to save JSON report (optional)"
    )
    
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed logging"
    )
    
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output only JSON (no summary)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    # Print banner unless JSON-only mode
    if not args.json_only:
        print_banner()
        print(f"Analyzing repository: {args.repo_path}")
        print(f"Analysis type: {args.analysis_type}")
        print()
    
    # Run analysis
    try:
        orchestrator = TechDebtOrchestrator()
        results = await orchestrator.analyze_repository(
            repo_path=args.repo_path,
            analysis_type=args.analysis_type
        )
        
        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            if not args.json_only:
                print(f"\nReport saved to: {output_path}")
        
        # Display results
        if args.json_only:
            print(json.dumps(results, indent=2, default=str))
        else:
            print_summary(results)
            if not args.output:
                print("Tip: Use --output report.json to save full results")
        
        # Exit code based on severity
        severity_exit_codes = {
            "low": 0,
            "medium": 1,
            "high": 2,
            "critical": 3
        }
        
        if results["status"] == "success":
            severity = results["results"]["impact_analysis"]["severity"]
            sys.exit(severity_exit_codes.get(severity, 0))
        else:
            sys.exit(4)  # Error exit code
            
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nERROR: {str(e)}\n")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())