"""Memory Bank for storing and retrieving historical analysis data."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json


class MemoryBank:
    """
    Long-term memory storage for technical debt analyses.
    
    Stores:
    - Historical analysis results
    - Identified patterns
    - Learned insights
    - Repository metadata
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize Memory Bank.
        
        Args:
            storage_path: Path to store memory data (optional, defaults to in-memory)
        """
        self.storage_path = storage_path
        self.memories: List[Dict[str, Any]] = []
        self.patterns: Dict[str, Any] = {}
        self.insights: List[str] = []
        
        if storage_path and storage_path.exists():
            self._load_from_disk()
    
    def store_analysis(
        self,
        repo_path: str,
        analysis_results: Dict[str, Any],
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Store an analysis in memory.
        
        Args:
            repo_path: Repository path
            analysis_results: Complete analysis results
            tags: Optional tags for categorization
            
        Returns:
            Memory ID
        """
        memory_id = f"mem_{datetime.now().timestamp()}"
        
        memory_entry = {
            "memory_id": memory_id,
            "repo_path": repo_path,
            "timestamp": datetime.now().isoformat(),
            "analysis_results": analysis_results,
            "tags": tags or [],
            "metadata": {
                "impact_score": analysis_results.get("results", {}).get("impact_analysis", {}).get("impact_score", 0),
                "severity": analysis_results.get("results", {}).get("impact_analysis", {}).get("severity", "unknown")
            }
        }
        
        self.memories.append(memory_entry)
        
        # Update patterns
        self._update_patterns(memory_entry)
        
        # Save to disk if configured
        if self.storage_path:
            self._save_to_disk()
        
        return memory_id
    
    def retrieve_by_repo(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        Retrieve all analyses for a specific repository.
        
        Args:
            repo_path: Repository path
            
        Returns:
            List of memory entries
        """
        return [
            m for m in self.memories
            if m["repo_path"] == repo_path
        ]
    
    def retrieve_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """
        Retrieve analyses by severity level.
        
        Args:
            severity: Severity level (low/medium/high/critical)
            
        Returns:
            List of memory entries
        """
        return [
            m for m in self.memories
            if m["metadata"]["severity"] == severity
        ]
    
    def retrieve_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve most recent analyses.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent memory entries
        """
        sorted_memories = sorted(
            self.memories,
            key=lambda m: m["timestamp"],
            reverse=True
        )
        return sorted_memories[:limit]
    
    def search_memories(
        self,
        min_impact_score: Optional[float] = None,
        severity: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memories with filters.
        
        Args:
            min_impact_score: Minimum impact score
            severity: Severity level filter
            tags: Tag filters
            limit: Maximum results
            
        Returns:
            Filtered memory entries
        """
        results = self.memories.copy()
        
        if min_impact_score is not None:
            results = [
                m for m in results
                if m["metadata"]["impact_score"] >= min_impact_score
            ]
        
        if severity:
            results = [
                m for m in results
                if m["metadata"]["severity"] == severity
            ]
        
        if tags:
            results = [
                m for m in results
                if any(tag in m["tags"] for tag in tags)
            ]
        
        # Sort by timestamp, most recent first
        results = sorted(
            results,
            key=lambda m: m["timestamp"],
            reverse=True
        )
        
        return results[:limit]
    
    def get_learned_insights(self) -> List[str]:
        """
        Get insights learned from historical data.
        
        Returns:
            List of insights
        """
        return self.insights.copy()
    
    def add_insight(self, insight: str):
        """
        Add a learned insight.
        
        Args:
            insight: Insight text
        """
        self.insights.append({
            "insight": insight,
            "learned_at": datetime.now().isoformat()
        })
    
    def get_patterns(self) -> Dict[str, Any]:
        """
        Get identified patterns from historical data.
        
        Returns:
            Dictionary of patterns
        """
        return self.patterns.copy()
    
    def _update_patterns(self, memory_entry: Dict[str, Any]):
        """Update patterns based on new memory."""
        severity = memory_entry["metadata"]["severity"]
        
        # Track severity distribution
        if "severity_distribution" not in self.patterns:
            self.patterns["severity_distribution"] = {}
        
        self.patterns["severity_distribution"][severity] = \
            self.patterns["severity_distribution"].get(severity, 0) + 1
        
        # Track average impact score
        if "average_impact_score" not in self.patterns:
            self.patterns["average_impact_score"] = 0
            self.patterns["total_analyses"] = 0
        
        total = self.patterns["total_analyses"]
        avg = self.patterns["average_impact_score"]
        new_score = memory_entry["metadata"]["impact_score"]
        
        self.patterns["average_impact_score"] = \
            (avg * total + new_score) / (total + 1)
        self.patterns["total_analyses"] = total + 1
        
        # Track common issues
        results = memory_entry.get("analysis_results", {}).get("results", {})
        impact = results.get("impact_analysis", {})
        
        for risk in impact.get("key_risks", []):
            if "common_risks" not in self.patterns:
                self.patterns["common_risks"] = {}
            
            self.patterns["common_risks"][risk] = \
                self.patterns["common_risks"].get(risk, 0) + 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory bank statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.memories:
            return {
                "total_memories": 0,
                "total_insights": 0,
                "patterns_identified": 0
            }
        
        return {
            "total_memories": len(self.memories),
            "total_insights": len(self.insights),
            "patterns_identified": len(self.patterns),
            "oldest_memory": min(m["timestamp"] for m in self.memories),
            "newest_memory": max(m["timestamp"] for m in self.memories),
            "severity_distribution": self.patterns.get("severity_distribution", {}),
            "average_impact_score": self.patterns.get("average_impact_score", 0)
        }
    
    def clear_memories(self):
        """Clear all memories."""
        self.memories.clear()
        self.patterns.clear()
        self.insights.clear()
    
    def _save_to_disk(self):
        """Save memory bank to disk."""
        if not self.storage_path:
            return
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "memories": self.memories,
            "patterns": self.patterns,
            "insights": self.insights,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_from_disk(self):
        """Load memory bank from disk."""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            self.memories = data.get("memories", [])
            self.patterns = data.get("patterns", {})
            self.insights = data.get("insights", [])
        except Exception:
            # If loading fails, start fresh
            pass


# Global memory bank instance
_global_memory_bank: Optional[MemoryBank] = None


def get_memory_bank(storage_path: Optional[Path] = None) -> MemoryBank:
    """
    Get the global memory bank instance.
    
    Args:
        storage_path: Optional path for persistent storage
        
    Returns:
        Global MemoryBank instance
    """
    global _global_memory_bank
    if _global_memory_bank is None:
        _global_memory_bank = MemoryBank(storage_path)
    return _global_memory_bank