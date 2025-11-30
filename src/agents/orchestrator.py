"""Orchestrator agent that coordinates the technical debt analysis workflow."""
from typing import Dict, Any, List
import google.generativeai as genai
from .. import config
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=config.GOOGLE_API_KEY)


class TechDebtOrchestrator:
    """
    Orchestrates the multi-agent technical debt analysis workflow.
    
    This agent coordinates three parallel analysis agents and two sequential agents:
    1. Parallel: Git History, CVE Scanner, Documentation Gap analyzers
    2. Sequential: Impact Analyzer -> Report Writer
    """
    
    def __init__(self):
        """Initialize the orchestrator with configuration."""
        self.config = config.AGENT_CONFIG["orchestrator"]
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel(
            model_name=self.config["model"],
            generation_config={
                "temperature": self.config["temperature"],
                "max_output_tokens": config.MAX_TOKENS,
            }
        )
        
        logger.info(f"Initialized {self.config['name']}")
    
    async def analyze_repository(
        self,
        repo_path: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Orchestrate a complete technical debt analysis.
        
        Args:
            repo_path: Path to the repository to analyze
            analysis_type: Type of analysis ('quick', 'comprehensive', 'security-focused')
            
        Returns:
            Dictionary containing complete analysis results
        """
        logger.info(f"Starting {analysis_type} analysis of {repo_path}")
        
        try:
            # Phase 1: Parallel data collection
            logger.info("Phase 1: Running parallel analysis agents")
            parallel_results = await self._run_parallel_agents(repo_path)
            
            # Phase 2: Impact analysis
            logger.info("Phase 2: Analyzing business impact")
            impact_results = await self._analyze_impact(parallel_results)
            
            # Phase 3: Report generation
            logger.info("Phase 3: Generating final report")
            final_report = await self._generate_report(
                parallel_results,
                impact_results
            )
            
            logger.info("Analysis complete")
            return {
                "status": "success",
                "analysis_type": analysis_type,
                "repo_path": repo_path,
                "timestamp": datetime.now().isoformat(),
                "results": {
                    "parallel_analysis": parallel_results,
                    "impact_analysis": impact_results,
                    "final_report": final_report
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "repo_path": repo_path,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _run_parallel_agents(
        self,
        repo_path: str
    ) -> Dict[str, Any]:
        """
        Run Git, CVE, and Documentation agents in parallel.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Combined results from all parallel agents
        """
        # Import tools
        from ..tools.git_analyzer import analyze_git_history
        from ..tools.cve_scanner import scan_dependencies_for_cves
        from ..tools.doc_parser import analyze_documentation
        
        # Run all three analyses in parallel
        tasks = [
            asyncio.create_task(
                asyncio.to_thread(
                    analyze_git_history,
                    repo_path,
                    config.GIT_LOOKBACK_DAYS
                )
            ),
            asyncio.create_task(
                asyncio.to_thread(
                    scan_dependencies_for_cves,
                    repo_path,
                    config.NVD_API_KEY
                )
            ),
            asyncio.create_task(
                asyncio.to_thread(
                    analyze_documentation,
                    repo_path
                )
            )
        ]
        
        # Wait for all to complete
        git_results, cve_results, doc_results = await asyncio.gather(*tasks)
        
        return {
            "git_analysis": git_results,
            "cve_analysis": cve_results,
            "documentation_analysis": doc_results
        }
    
    async def _analyze_impact(
        self,
        parallel_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze business impact of findings using AI.
        
        Args:
            parallel_results: Results from parallel agents
            
        Returns:
            Impact analysis results
        """
        # Calculate basic metrics
        git_risk = parallel_results["git_analysis"].get("risk_score", 0)
        cve_count = len(parallel_results["cve_analysis"].get("vulnerabilities", []))
        doc_coverage = parallel_results["documentation_analysis"].get("coverage", 0)
        
        # Use AI to analyze impact
        prompt = f"""Analyze the business impact of these technical debt findings:

GIT ANALYSIS:
- Risk Score: {git_risk}/100
- High Churn Files: {len(parallel_results["git_analysis"].get("high_churn_files", []))}

SECURITY ANALYSIS:
- Vulnerabilities: {cve_count}
- Severity Distribution: {parallel_results["cve_analysis"].get("severity_summary", {})}

DOCUMENTATION ANALYSIS:
- Coverage: {doc_coverage:.1%}
- Total Files: {parallel_results["documentation_analysis"].get("total_files", 0)}

Provide:
1. Overall impact score (0-100)
2. Severity level (low/medium/high/critical)
3. Top 3 key risks
4. Top 3 recommendations

Format as a brief analysis."""

        try:
            response = self.model.generate_content(prompt)
            ai_analysis = response.text
        except Exception as e:
            logger.error(f"AI impact analysis failed: {e}")
            ai_analysis = "AI analysis unavailable"
        
        # Calculate overall impact score
        impact_score = (
            git_risk * 0.3 +
            min(cve_count * 20, 50) * 0.4 +
            (1 - doc_coverage) * 100 * 0.3
        )
        
        severity = "low"
        if impact_score > 70:
            severity = "critical"
        elif impact_score > 50:
            severity = "high"
        elif impact_score > 30:
            severity = "medium"
        
        return {
            "impact_score": round(impact_score, 2),
            "severity": severity,
            "key_risks": self._identify_key_risks(parallel_results),
            "recommendations": self._generate_recommendations(parallel_results),
            "ai_analysis": ai_analysis
        }
    
    def _identify_key_risks(
        self,
        parallel_results: Dict[str, Any]
    ) -> List[str]:
        """Identify top risks from analysis results."""
        risks = []
        
        # Check Git risks
        git_risk = parallel_results["git_analysis"].get("risk_score", 0)
        if git_risk > 50:
            risks.append("High code churn detected - potential stability issues")
        
        # Check CVE risks
        vulns = parallel_results["cve_analysis"].get("vulnerabilities", [])
        critical_vulns = [v for v in vulns if v.get("severity") == "CRITICAL"]
        if critical_vulns:
            risks.append(f"Critical security vulnerabilities found: {len(critical_vulns)}")
        
        # Check documentation risks
        doc_coverage = parallel_results["documentation_analysis"].get("coverage", 0)
        if doc_coverage < 0.5:
            risks.append("Low documentation coverage - maintainability concern")
        
        return risks if risks else ["No critical risks identified"]
    
    def _generate_recommendations(
        self,
        parallel_results: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Git recommendations
        high_churn_files = parallel_results["git_analysis"].get("high_churn_files", [])
        if high_churn_files:
            recommendations.append(
                f"Review and refactor {len(high_churn_files)} high-churn files"
            )
        
        # CVE recommendations
        vulns = parallel_results["cve_analysis"].get("vulnerabilities", [])
        if vulns:
            recommendations.append(
                f"Update {len(vulns)} vulnerable dependencies immediately"
            )
        
        # Documentation recommendations
        doc_coverage = parallel_results["documentation_analysis"].get("coverage", 0)
        if doc_coverage < 0.7:
            recommendations.append(
                "Improve documentation coverage to at least 70%"
            )
        
        return recommendations if recommendations else ["Continue maintaining current standards"]
    
    async def _generate_report(
        self,
        parallel_results: Dict[str, Any],
        impact_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate final comprehensive report.
        
        Args:
            parallel_results: Results from parallel agents
            impact_results: Impact analysis results
            
        Returns:
            Final report structure
        """
        return {
            "executive_summary": {
                "impact_score": impact_results["impact_score"],
                "severity": impact_results["severity"],
                "total_issues": (
                    len(parallel_results["git_analysis"].get("high_churn_files", [])) +
                    len(parallel_results["cve_analysis"].get("vulnerabilities", [])) +
                    len(parallel_results["documentation_analysis"].get("undocumented_files", []))
                )
            },
            "detailed_findings": {
                "git_analysis": parallel_results["git_analysis"],
                "security_analysis": parallel_results["cve_analysis"],
                "documentation_analysis": parallel_results["documentation_analysis"]
            },
            "impact_assessment": impact_results,
            "recommendations": impact_results["recommendations"]
        }


# For testing
if __name__ == "__main__":
    async def test():
        orchestrator = TechDebtOrchestrator()
        result = await orchestrator.analyze_repository(".", "comprehensive")
        
        import json
        print(json.dumps(result, indent=2, default=str))
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())