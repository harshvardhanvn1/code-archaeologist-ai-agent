"""Git history analysis tool for detecting code churn and risk patterns."""
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import json
from datetime import datetime, timedelta


def analyze_git_history(
    repo_path: str,
    lookback_days: int = 90
) -> Dict[str, Any]:
    """
    Analyze Git history to identify code churn and risk patterns.
    
    Args:
        repo_path: Path to the Git repository
        lookback_days: Number of days to look back in history
        
    Returns:
        Dictionary containing analysis results with risk score and churn data
    """
    try:
        repo_path = Path(repo_path).resolve()
        
        # Check if it's a git repository
        if not (repo_path / ".git").exists():
            return {
                "error": "Not a git repository",
                "risk_score": 0,
                "high_churn_files": [],
                "total_commits": 0
            }
        
        # Calculate date range
        since_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        # Get commit count
        commit_count_cmd = [
            "git", "-C", str(repo_path),
            "rev-list", "--count", f"--since={since_date}", "HEAD"
        ]
        total_commits = int(subprocess.check_output(commit_count_cmd).decode().strip() or "0")
        
        if total_commits == 0:
            return {
                "risk_score": 0,
                "high_churn_files": [],
                "total_commits": 0,
                "message": "No commits in the specified time range"
            }
        
        # Get file change frequencies
        log_cmd = [
            "git", "-C", str(repo_path),
            "log", f"--since={since_date}",
            "--name-only", "--pretty=format:", "HEAD"
        ]
        output = subprocess.check_output(log_cmd).decode()
        
        # Count changes per file
        file_changes = {}
        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith('.'):
                file_changes[line] = file_changes.get(line, 0) + 1
        
        # Identify high churn files (changed more than 20% of commits)
        churn_threshold = max(3, total_commits * 0.2)
        high_churn_files = [
            {"file": file, "changes": count}
            for file, count in file_changes.items()
            if count >= churn_threshold
        ]
        
        # Sort by number of changes
        high_churn_files.sort(key=lambda x: x["changes"], reverse=True)
        
        # Calculate risk score (0-100)
        if not high_churn_files:
            risk_score = 10
        else:
            # Risk increases with number of high-churn files
            risk_score = min(100, 30 + (len(high_churn_files) * 10))
        
        return {
            "risk_score": risk_score,
            "total_commits": total_commits,
            "high_churn_files": high_churn_files[:10],  # Top 10
            "lookback_days": lookback_days,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except subprocess.CalledProcessError as e:
        return {
            "error": f"Git command failed: {str(e)}",
            "risk_score": 0,
            "high_churn_files": [],
            "total_commits": 0
        }
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "risk_score": 0,
            "high_churn_files": [],
            "total_commits": 0
        }


# Test function
if __name__ == "__main__":
    # Test on current directory
    result = analyze_git_history(".", lookback_days=30)
    print(json.dumps(result, indent=2))