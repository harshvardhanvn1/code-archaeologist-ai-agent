"""Performance and quality metrics for evaluation."""
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    analysis_id: str
    timestamp: datetime
    
    # Quality scores
    overall_quality: float = 0.0
    completeness: float = 0.0
    accuracy: float = 0.0
    actionability: float = 0.0
    clarity: float = 0.0
    
    # Performance metrics
    total_duration: float = 0.0
    tool_execution_time: Dict[str, float] = field(default_factory=dict)
    agent_execution_time: Dict[str, float] = field(default_factory=dict)
    
    # Outcome metrics
    issues_found: int = 0
    high_priority_issues: int = 0
    vulnerabilities_found: int = 0
    
    # User feedback
    user_rating: float = 0.0
    user_feedback: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "analysis_id": self.analysis_id,
            "timestamp": self.timestamp.isoformat(),
            "quality": {
                "overall": self.overall_quality,
                "completeness": self.completeness,
                "accuracy": self.accuracy,
                "actionability": self.actionability,
                "clarity": self.clarity
            },
            "performance": {
                "total_duration": self.total_duration,
                "tool_times": self.tool_execution_time,
                "agent_times": self.agent_execution_time
            },
            "outcomes": {
                "total_issues": self.issues_found,
                "high_priority": self.high_priority_issues,
                "vulnerabilities": self.vulnerabilities_found
            },
            "feedback": {
                "rating": self.user_rating,
                "comments": self.user_feedback
            }
        }


class MetricsAggregator:
    """Aggregates metrics across multiple analyses."""
    
    def __init__(self):
        """Initialize metrics aggregator."""
        self.metrics_history: List[EvaluationMetrics] = []
    
    def add_metrics(self, metrics: EvaluationMetrics) -> None:
        """
        Add metrics to history.
        
        Args:
            metrics: EvaluationMetrics instance
        """
        self.metrics_history.append(metrics)
    
    def get_average_quality(self) -> float:
        """
        Calculate average quality score across all analyses.
        
        Returns:
            Average quality score (0-100)
        """
        if not self.metrics_history:
            return 0.0
        
        total = sum(m.overall_quality for m in self.metrics_history)
        return total / len(self.metrics_history)
    
    def get_average_duration(self) -> float:
        """
        Calculate average analysis duration.
        
        Returns:
            Average duration in seconds
        """
        if not self.metrics_history:
            return 0.0
        
        total = sum(m.total_duration for m in self.metrics_history)
        return total / len(self.metrics_history)
    
    def get_total_issues_found(self) -> int:
        """
        Get total number of issues found across all analyses.
        
        Returns:
            Total issue count
        """
        return sum(m.issues_found for m in self.metrics_history)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics summary.
        
        Returns:
            Dictionary containing aggregated metrics
        """
        if not self.metrics_history:
            return {
                "total_analyses": 0,
                "average_quality": 0,
                "average_duration": 0,
                "total_issues": 0
            }
        
        return {
            "total_analyses": len(self.metrics_history),
            "quality_metrics": {
                "average_overall": self.get_average_quality(),
                "average_completeness": sum(m.completeness for m in self.metrics_history) / len(self.metrics_history),
                "average_accuracy": sum(m.accuracy for m in self.metrics_history) / len(self.metrics_history),
                "average_actionability": sum(m.actionability for m in self.metrics_history) / len(self.metrics_history),
                "average_clarity": sum(m.clarity for m in self.metrics_history) / len(self.metrics_history)
            },
            "performance_metrics": {
                "average_duration": self.get_average_duration(),
                "min_duration": min(m.total_duration for m in self.metrics_history),
                "max_duration": max(m.total_duration for m in self.metrics_history)
            },
            "outcome_metrics": {
                "total_issues_found": self.get_total_issues_found(),
                "total_vulnerabilities": sum(m.vulnerabilities_found for m in self.metrics_history),
                "average_issues_per_analysis": self.get_total_issues_found() / len(self.metrics_history)
            },
            "user_satisfaction": {
                "average_rating": sum(m.user_rating for m in self.metrics_history if m.user_rating > 0) / 
                                 max(1, sum(1 for m in self.metrics_history if m.user_rating > 0))
            }
        }


def calculate_quality_score(
    llm_judge_score: float,
    user_feedback_score: float = 0.0,
    weight_llm: float = 0.7,
    weight_user: float = 0.3
) -> float:
    """
    Calculate weighted quality score.
    
    Args:
        llm_judge_score: Score from LLM judge (0-100)
        user_feedback_score: Score from user feedback (0-100)
        weight_llm: Weight for LLM judge score
        weight_user: Weight for user feedback score
        
    Returns:
        Weighted quality score (0-100)
    """
    if user_feedback_score > 0:
        return (llm_judge_score * weight_llm) + (user_feedback_score * weight_user)
    else:
        return llm_judge_score