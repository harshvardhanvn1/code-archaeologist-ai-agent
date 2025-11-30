"""Human-in-the-Loop review agent for validating analysis results."""
from typing import Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime
from src import config


class HumanReviewLoopAgent:
    """
    Implements Human-in-the-Loop validation for analysis results.
    
    This agent:
    1. Presents findings to human reviewer
    2. Accepts feedback and corrections
    3. Updates analysis based on feedback
    4. Learns from human input for future analyses
    """
    
    def __init__(self):
        """Initialize human review loop agent."""
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": config.MAX_TOKENS,
            }
        )
        self.review_history = []
    
    def request_review(
        self,
        analysis_results: Dict[str, Any],
        focus_areas: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Request human review of analysis results.
        
        Args:
            analysis_results: Complete analysis results
            focus_areas: Optional specific areas to review
            
        Returns:
            Review request with formatted findings
        """
        review_request = {
            "review_id": f"review_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "summary": self._create_review_summary(analysis_results),
            "focus_areas": focus_areas or ["all"],
            "questions": self._generate_review_questions(analysis_results),
            "status": "pending_review"
        }
        
        self.review_history.append(review_request)
        return review_request
    
    def _create_review_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create human-friendly summary of findings."""
        parallel = results.get("results", {}).get("parallel_analysis", {})
        impact = results.get("results", {}).get("impact_analysis", {})
        
        return {
            "overall_severity": impact.get("severity", "unknown"),
            "impact_score": impact.get("impact_score", 0),
            "key_findings": {
                "git_risk": parallel.get("git_analysis", {}).get("risk_score", 0),
                "vulnerabilities": len(parallel.get("cve_analysis", {}).get("vulnerabilities", [])),
                "documentation_coverage": parallel.get("documentation_analysis", {}).get("coverage", 0)
            },
            "top_recommendations": impact.get("recommendations", [])[:3]
        }
    
    def _generate_review_questions(self, results: Dict[str, Any]) -> list:
        """Generate questions for human reviewer."""
        questions = [
            {
                "id": "q1",
                "question": "Do the identified high-churn files align with known problem areas?",
                "type": "yes_no_comment"
            },
            {
                "id": "q2",
                "question": "Are the security vulnerabilities correctly prioritized?",
                "type": "yes_no_comment"
            },
            {
                "id": "q3",
                "question": "Do the recommendations seem actionable and practical?",
                "type": "rating_1_5"
            },
            {
                "id": "q4",
                "question": "Are there any false positives in the findings?",
                "type": "yes_no_list"
            },
            {
                "id": "q5",
                "question": "What additional context should the system consider?",
                "type": "free_text"
            }
        ]
        
        return questions
    
    def process_feedback(
        self,
        review_id: str,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process human feedback and update analysis.
        
        Args:
            review_id: ID of the review
            feedback: Human feedback responses
            
        Returns:
            Updated analysis with incorporated feedback
        """
        # Find the original review
        review = next(
            (r for r in self.review_history if r["review_id"] == review_id),
            None
        )
        
        if not review:
            return {
                "status": "error",
                "message": "Review not found"
            }
        
        # Use AI to incorporate feedback
        refinement_prompt = f"""Based on human reviewer feedback, refine the technical debt analysis.

ORIGINAL FINDINGS:
{review.get("summary", {})}

HUMAN FEEDBACK:
{feedback}

Provide refined analysis incorporating the human feedback. Consider:
1. Validate or correct AI findings
2. Adjust priorities based on human context
3. Update recommendations based on feedback
4. Note any learning points for future analyses

Format response as JSON with:
- validated_findings: corrected findings
- priority_adjustments: any priority changes
- updated_recommendations: refined recommendations
- learning_points: insights for future analyses
"""
        
        try:
            response = self.model.generate_content(refinement_prompt)
            
            return {
                "status": "completed",
                "review_id": review_id,
                "feedback_processed": feedback,
                "refinement": response.text,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "review_id": review_id
            }
    
    def simulate_review(
        self,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate human review for automated testing.
        
        Args:
            analysis_results: Analysis results to review
            
        Returns:
            Simulated feedback
        """
        # For demo purposes - simulate positive review
        impact = analysis_results.get("results", {}).get("impact_analysis", {})
        
        simulated_feedback = {
            "q1": {
                "answer": "yes",
                "comment": "Findings align with team knowledge of problem areas"
            },
            "q2": {
                "answer": "yes",
                "comment": "Security priorities look correct"
            },
            "q3": {
                "answer": 4,
                "comment": "Recommendations are practical and actionable"
            },
            "q4": {
                "answer": "no",
                "items": []
            },
            "q5": {
                "answer": "Consider recent refactoring efforts in core modules"
            },
            "overall_rating": 4,
            "approved": True,
            "reviewer": "automated_simulation"
        }
        
        return simulated_feedback
    
    def get_review_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about review history.
        
        Returns:
            Review statistics
        """
        if not self.review_history:
            return {
                "total_reviews": 0,
                "completed_reviews": 0,
                "pending_reviews": 0
            }
        
        completed = sum(1 for r in self.review_history if r.get("status") == "completed")
        pending = sum(1 for r in self.review_history if r.get("status") == "pending_review")
        
        return {
            "total_reviews": len(self.review_history),
            "completed_reviews": completed,
            "pending_reviews": pending,
            "completion_rate": completed / len(self.review_history) if self.review_history else 0
        }