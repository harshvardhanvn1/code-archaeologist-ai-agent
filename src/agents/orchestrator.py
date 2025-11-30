"""Orchestrator agent that coordinates the technical debt analysis workflow."""
from typing import Dict, Any, List
import google.generativeai as genai
from src import config
import asyncio
from datetime import datetime
from src.observability.logger import get_logger, generate_correlation_id
from src.observability.tracer import trace_function, get_tracer
from src.observability.metrics import get_global_metrics
from src.evaluation.llm_judge import LLMJudge
from src.evaluation.metrics import EvaluationMetrics
from src.agents.human_review_loop import HumanReviewLoopAgent
import time

# Configure Gemini
genai.configure(api_key=config.GOOGLE_API_KEY)


class TechDebtOrchestrator:
    """
    Orchestrates the multi-agent technical debt analysis workflow.
    
    This agent coordinates three parallel analysis agents and sequential agents:
    1. Parallel: Git History, CVE Scanner, Documentation Gap analyzers
    2. Sequential: Impact Analyzer -> Report Writer -> Human Review Loop
    """
    
    def __init__(self):
        """Initialize the orchestrator with configuration and observability."""
        self.config = config.AGENT_CONFIG["orchestrator"]
        self.correlation_id = generate_correlation_id()
        self.logger = get_logger(__name__, self.correlation_id)
        self.tracer = get_tracer()
        self.metrics = get_global_metrics()
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel(
            model_name=self.config["model"],
            generation_config={
                "temperature": self.config["temperature"],
                "max_output_tokens": config.MAX_TOKENS,
            }
        )
        
        # Initialize evaluation
        self.llm_judge = LLMJudge()
        self.review_agent = HumanReviewLoopAgent()
        
        self.logger.info(
            "orchestrator_initialized",
            model=self.config["model"],
            correlation_id=self.correlation_id
        )
    
    @trace_function("analyze_repository")
    async def analyze_repository(
        self,
        repo_path: str,
        analysis_type: str = "comprehensive",
        enable_human_review: bool = False
    ) -> Dict[str, Any]:
        """
        Orchestrate a complete technical debt analysis.
        
        Args:
            repo_path: Path to the repository to analyze
            analysis_type: Type of analysis
            enable_human_review: Whether to enable HITL validation
            
        Returns:
            Dictionary containing complete analysis results
        """
        analysis_start = time.time()
        
        self.logger.info(
            "analysis_started",
            repo_path=repo_path,
            analysis_type=analysis_type,
            correlation_id=self.correlation_id
        )
        
        try:
            with self.tracer.start_as_current_span("full_analysis") as span:
                span.set_attribute("repo_path", repo_path)
                span.set_attribute("analysis_type", analysis_type)
                
                # Phase 1: Parallel data collection
                self.logger.info("phase_1_started", phase="parallel_data_collection")
                parallel_results = await self._run_parallel_agents(repo_path)
                self.logger.info("phase_1_completed", phase="parallel_data_collection")
                
                # Phase 2: Impact analysis
                self.logger.info("phase_2_started", phase="impact_analysis")
                impact_results = await self._analyze_impact(parallel_results)
                self.logger.info("phase_2_completed", phase="impact_analysis")
                
                # Phase 3: Report generation
                self.logger.info("phase_3_started", phase="report_generation")
                final_report = await self._generate_report(parallel_results, impact_results)
                self.logger.info("phase_3_completed", phase="report_generation")
                
                # Compile results
                results = {
                    "status": "success",
                    "analysis_type": analysis_type,
                    "repo_path": repo_path,
                    "correlation_id": self.correlation_id,
                    "timestamp": datetime.now().isoformat(),
                    "results": {
                        "parallel_analysis": parallel_results,
                        "impact_analysis": impact_results,
                        "final_report": final_report
                    }
                }
                
                # Phase 4: Evaluation (LLM-as-Judge)
                self.logger.info("evaluation_started")
                evaluation = self.llm_judge.evaluate_analysis(results)
                results["evaluation"] = evaluation
                self.logger.info(
                    "evaluation_completed",
                    overall_score=evaluation.get("overall_score", 0)
                )
                
                # Phase 5: Human review (if enabled)
                if enable_human_review:
                    self.logger.info("human_review_started")
                    review_request = self.review_agent.request_review(results)
                    
                    # Simulate review for demo
                    simulated_feedback = self.review_agent.simulate_review(results)
                    review_result = self.review_agent.process_feedback(
                        review_request["review_id"],
                        simulated_feedback
                    )
                    
                    results["human_review"] = review_result
                    self.logger.info("human_review_completed")
                
                # Record metrics
                duration = time.time() - analysis_start
                self.metrics.record_duration("full_analysis", duration)
                self.metrics.increment("analyses_completed")
                
                self.logger.info(
                    "analysis_completed",
                    duration_seconds=duration,
                    correlation_id=self.correlation_id
                )
                
                return results
                
        except Exception as e:
            self.logger.error(
                "analysis_failed",
                error=str(e),
                correlation_id=self.correlation_id
            )
            self.metrics.increment("analyses_failed")
            
            return {
                "status": "error",
                "error": str(e),
                "repo_path": repo_path,
                "correlation_id": self.correlation_id,
                "timestamp": datetime.now().isoformat()
            }
    
    @trace_function("run_parallel_agents")
    async def _run_parallel_agents(self, repo_path: str) -> Dict[str, Any]:
        """Run Git, CVE, and Documentation agents in parallel."""
        from src.tools.git_analyzer import analyze_git_history
        from src.tools.cve_scanner import scan_dependencies_for_cves
        from src.tools.doc_parser import analyze_documentation
        
        with self.tracer.start_as_current_span("parallel_execution"):
            # Create parallel tasks
            tasks = [
                asyncio.create_task(
                    asyncio.to_thread(analyze_git_history, repo_path, config.GIT_LOOKBACK_DAYS)
                ),
                asyncio.create_task(
                    asyncio.to_thread(scan_dependencies_for_cves, repo_path, config.NVD_API_KEY)
                ),
                asyncio.create_task(
                    asyncio.to_thread(analyze_documentation, repo_path)
                )
            ]
            
            # Wait for all to complete
            git_results, cve_results, doc_results = await asyncio.gather(*tasks)
            
            # Record tool metrics
            self.metrics.increment("git_analyses_completed")
            self.metrics.increment("cve_scans_completed")
            self.metrics.increment("doc_analyses_completed")
            
            return {
                "git_analysis": git_results,
                "cve_analysis": cve_results,
                "documentation_analysis": doc_results
            }
    
    @trace_function("analyze_impact")
    async def _analyze_impact(self, parallel_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business impact of findings using AI."""
        git_risk = parallel_results["git_analysis"].get("risk_score", 0)
        cve_count = len(parallel_results["cve_analysis"].get("vulnerabilities", []))
        doc_coverage = parallel_results["documentation_analysis"].get("coverage", 0)
        
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
            self.metrics.increment("ai_analyses_completed")
        except Exception as e:
            self.logger.error("ai_analysis_failed", error=str(e))
            ai_analysis = "AI analysis unavailable"
            self.metrics.increment("ai_analyses_failed")
        
        # Calculate impact score
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
    
    def _identify_key_risks(self, parallel_results: Dict[str, Any]) -> List[str]:
        """Identify top risks from analysis results."""
        risks = []
        
        git_risk = parallel_results["git_analysis"].get("risk_score", 0)
        if git_risk > 50:
            risks.append("High code churn detected - potential stability issues")
        
        vulns = parallel_results["cve_analysis"].get("vulnerabilities", [])
        critical_vulns = [v for v in vulns if v.get("severity") == "CRITICAL"]
        if critical_vulns:
            risks.append(f"Critical security vulnerabilities found: {len(critical_vulns)}")
        
        doc_coverage = parallel_results["documentation_analysis"].get("coverage", 0)
        if doc_coverage < 0.5:
            risks.append("Low documentation coverage - maintainability concern")
        
        return risks if risks else ["No critical risks identified"]
    
    def _generate_recommendations(self, parallel_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        high_churn_files = parallel_results["git_analysis"].get("high_churn_files", [])
        if high_churn_files:
            recommendations.append(f"Review and refactor {len(high_churn_files)} high-churn files")
        
        vulns = parallel_results["cve_analysis"].get("vulnerabilities", [])
        if vulns:
            recommendations.append(f"Update {len(vulns)} vulnerable dependencies immediately")
        
        doc_coverage = parallel_results["documentation_analysis"].get("coverage", 0)
        if doc_coverage < 0.7:
            recommendations.append("Improve documentation coverage to at least 70%")
        
        return recommendations if recommendations else ["Continue maintaining current standards"]
    
    @trace_function("generate_report")
    async def _generate_report(
        self,
        parallel_results: Dict[str, Any],
        impact_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final comprehensive report."""
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
        result = await orchestrator.analyze_repository(".", "comprehensive", enable_human_review=True)
        
        import json
        print(json.dumps(result, indent=2, default=str))
    
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())