"""LLM-as-Judge evaluation framework for assessing analysis quality."""
import google.generativeai as genai
from typing import Dict, Any, List
from datetime import datetime
from src import config


class LLMJudge:
    """
    Uses Gemini as a judge to evaluate analysis quality.
    
    Assesses technical debt analysis reports on:
    - Completeness
    - Accuracy
    - Actionability
    - Clarity
    """
    
    def __init__(self):
        """Initialize LLM judge with Gemini model."""
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            generation_config={
                "temperature": 0.3,  # Lower for more consistent judging
                "max_output_tokens": 2000,
            }
        )
    
    def evaluate_analysis(
        self,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of a technical debt analysis.
        
        Args:
            analysis_results: Complete analysis results from orchestrator
            
        Returns:
            Evaluation scores and feedback
        """
        prompt = self._build_evaluation_prompt(analysis_results)
        
        try:
            response = self.model.generate_content(prompt)
            evaluation = self._parse_evaluation_response(response.text)
            
            return {
                "overall_score": evaluation["overall_score"],
                "dimension_scores": evaluation["dimensions"],
                "strengths": evaluation["strengths"],
                "weaknesses": evaluation["weaknesses"],
                "recommendations": evaluation["recommendations"],
                "evaluated_at": datetime.now().isoformat(),
                "judge_model": "gemini-2.5-flash-lite"
            }
            
        except Exception as e:
            return {
                "overall_score": 0,
                "error": f"Evaluation failed: {str(e)}",
                "evaluated_at": datetime.now().isoformat()
            }
    
    def _build_evaluation_prompt(self, results: Dict[str, Any]) -> str:
        """Build evaluation prompt from analysis results."""
        parallel_analysis = results.get("results", {}).get("parallel_analysis", {})
        impact_analysis = results.get("results", {}).get("impact_analysis", {})
        
        git_data = parallel_analysis.get("git_analysis", {})
        cve_data = parallel_analysis.get("cve_analysis", {})
        doc_data = parallel_analysis.get("documentation_analysis", {})
        
        prompt = f"""You are an expert code quality auditor evaluating a technical debt analysis report.

ANALYSIS RESULTS TO EVALUATE:

Git History Analysis:
- Risk Score: {git_data.get('risk_score', 0)}/100
- Total Commits: {git_data.get('total_commits', 0)}
- High Churn Files: {len(git_data.get('high_churn_files', []))}

Security Analysis:
- Total Dependencies: {cve_data.get('total_dependencies', 0)}
- Vulnerabilities Found: {len(cve_data.get('vulnerabilities', []))}
- Severity Distribution: {cve_data.get('severity_summary', {})}

Documentation Analysis:
- Coverage: {doc_data.get('coverage', 0):.1%}
- Total Files: {doc_data.get('total_files', 0)}
- Documented Files: {doc_data.get('documented_files', 0)}

Impact Assessment:
- Impact Score: {impact_analysis.get('impact_score', 0)}/100
- Severity: {impact_analysis.get('severity', 'unknown')}
- Key Risks: {impact_analysis.get('key_risks', [])}
- Recommendations: {impact_analysis.get('recommendations', [])}

EVALUATION CRITERIA:
Rate each dimension on a scale of 0-100:

1. COMPLETENESS (0-100): Does the analysis cover all important aspects?
2. ACCURACY (0-100): Are the findings technically sound and precise?
3. ACTIONABILITY (0-100): Are recommendations clear and implementable?
4. CLARITY (0-100): Is the report well-structured and understandable?

Provide your evaluation in this EXACT format:

OVERALL_SCORE: [0-100]

COMPLETENESS: [0-100]
ACCURACY: [0-100]
ACTIONABILITY: [0-100]
CLARITY: [0-100]

STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]

WEAKNESSES:
- [weakness 1]
- [weakness 2]

RECOMMENDATIONS:
- [recommendation 1]
- [recommendation 2]
"""
        return prompt
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM judge response into structured data."""
        lines = response_text.strip().split('\n')
        
        evaluation = {
            "overall_score": 0,
            "dimensions": {},
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("OVERALL_SCORE:"):
                try:
                    evaluation["overall_score"] = int(line.split(":")[1].strip())
                except:
                    evaluation["overall_score"] = 0
            
            elif line.startswith("COMPLETENESS:"):
                try:
                    evaluation["dimensions"]["completeness"] = int(line.split(":")[1].strip())
                except:
                    pass
            
            elif line.startswith("ACCURACY:"):
                try:
                    evaluation["dimensions"]["accuracy"] = int(line.split(":")[1].strip())
                except:
                    pass
            
            elif line.startswith("ACTIONABILITY:"):
                try:
                    evaluation["dimensions"]["actionability"] = int(line.split(":")[1].strip())
                except:
                    pass
            
            elif line.startswith("CLARITY:"):
                try:
                    evaluation["dimensions"]["clarity"] = int(line.split(":")[1].strip())
                except:
                    pass
            
            elif line == "STRENGTHS:":
                current_section = "strengths"
            
            elif line == "WEAKNESSES:":
                current_section = "weaknesses"
            
            elif line == "RECOMMENDATIONS:":
                current_section = "recommendations"
            
            elif line.startswith("- ") and current_section:
                item = line[2:].strip()
                if current_section == "strengths":
                    evaluation["strengths"].append(item)
                elif current_section == "weaknesses":
                    evaluation["weaknesses"].append(item)
                elif current_section == "recommendations":
                    evaluation["recommendations"].append(item)
        
        # Calculate overall score if not provided
        if evaluation["overall_score"] == 0 and evaluation["dimensions"]:
            dimension_scores = list(evaluation["dimensions"].values())
            if dimension_scores:
                evaluation["overall_score"] = int(sum(dimension_scores) / len(dimension_scores))
        
        return evaluation
    
    def evaluate_tool_output(
        self,
        tool_name: str,
        tool_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate individual tool output quality.
        
        Args:
            tool_name: Name of the tool
            tool_output: Output data from the tool
            
        Returns:
            Evaluation scores for the tool
        """
        prompt = f"""Evaluate the quality of this {tool_name} tool output:

{tool_output}

Rate the output on:
1. Data completeness (0-100)
2. Data accuracy (0-100)
3. Usefulness (0-100)

Respond in format:
COMPLETENESS: [score]
ACCURACY: [score]
USEFULNESS: [score]
OVERALL: [average score]
"""
        
        try:
            response = self.model.generate_content(prompt)
            # Simple parsing for tool evaluation
            lines = response.text.strip().split('\n')
            scores = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':')
                    try:
                        scores[key.strip().lower()] = int(value.strip())
                    except:
                        pass
            
            return {
                "tool_name": tool_name,
                "scores": scores,
                "overall_score": scores.get("overall", 0),
                "evaluated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "tool_name": tool_name,
                "error": str(e),
                "overall_score": 0
            }