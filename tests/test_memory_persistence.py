"""Test memory bank persistence across multiple analyses."""
import sys
from pathlib import Path
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.agents.orchestrator import TechDebtOrchestrator
from src.memory.memory_bank import get_memory_bank
from src.sessions.session_service import get_session_service


async def run_multiple_analyses():
    """Run multiple analyses and verify memory storage."""
    print("\n" + "="*70)
    print("  TESTING MEMORY BANK PERSISTENCE")
    print("="*70 + "\n")
    
    memory_bank = get_memory_bank()
    session_service = get_session_service()
    
    # Clear previous state
    memory_bank.clear_memories()
    session_service.clear_all_sessions()
    
    print("Starting with clean slate...")
    print(f"Initial memories: {memory_bank.get_statistics()['total_memories']}")
    print(f"Initial sessions: {session_service.get_session_count()}\n")
    
    # Run 3 analyses
    orchestrator = TechDebtOrchestrator()
    
    print("Running Analysis #1...")
    result1 = await orchestrator.analyze_repository(".", "quick")
    print(f"  Session ID: {result1.get('session_id')}")
    print(f"  Memory ID: {result1.get('memory_id')}")
    print(f"  Severity: {result1['results']['impact_analysis']['severity']}\n")
    
    print("Running Analysis #2...")
    result2 = await orchestrator.analyze_repository(".", "comprehensive")
    print(f"  Session ID: {result2.get('session_id')}")
    print(f"  Memory ID: {result2.get('memory_id')}")
    print(f"  Severity: {result2['results']['impact_analysis']['severity']}\n")
    
    print("Running Analysis #3...")
    result3 = await orchestrator.analyze_repository(".", "security-focused")
    print(f"  Session ID: {result3.get('session_id')}")
    print(f"  Memory ID: {result3.get('memory_id')}")
    print(f"  Severity: {result3['results']['impact_analysis']['severity']}\n")
    
    # Check memory bank
    print("="*70)
    print("  MEMORY BANK STATISTICS")
    print("="*70 + "\n")
    
    stats = memory_bank.get_statistics()
    print(f"Total Memories Stored: {stats['total_memories']}")
    print(f"Total Insights: {stats['total_insights']}")
    print(f"Patterns Identified: {stats['patterns_identified']}")
    print(f"Average Impact Score: {stats.get('average_impact_score', 0):.2f}")
    print(f"Severity Distribution: {stats.get('severity_distribution', {})}\n")
    
    # Retrieve memories
    print("="*70)
    print("  RETRIEVING STORED MEMORIES")
    print("="*70 + "\n")
    
    # Get all memories for this repo
    repo_memories = memory_bank.retrieve_by_repo(".")
    print(f"Memories for current repo: {len(repo_memories)}")
    
    for i, mem in enumerate(repo_memories, 1):
        print(f"\nMemory {i}:")
        print(f"  ID: {mem['memory_id']}")
        print(f"  Timestamp: {mem['timestamp']}")
        print(f"  Severity: {mem['metadata']['severity']}")
        print(f"  Impact Score: {mem['metadata']['impact_score']}")
        print(f"  Tags: {mem['tags']}")
    
    # Test searching
    print("\n" + "="*70)
    print("  TESTING MEMORY SEARCH")
    print("="*70 + "\n")
    
    # Search by severity
    low_severity = memory_bank.retrieve_by_severity("low")
    print(f"Low severity analyses: {len(low_severity)}")
    
    # Search recent
    recent = memory_bank.retrieve_recent(limit=2)
    print(f"Most recent 2 analyses:")
    for mem in recent:
        print(f"  - {mem['memory_id']} (severity: {mem['metadata']['severity']})")
    
    # Check sessions
    print("\n" + "="*70)
    print("  SESSION SERVICE STATISTICS")
    print("="*70 + "\n")
    
    session_stats = session_service.get_statistics()
    print(f"Total Sessions: {session_stats['total_sessions']}")
    print(f"Active Sessions: {session_stats['active_sessions']}")
    print(f"Average Conversation Length: {session_stats['average_conversation_length']:.1f}")
    
    # List sessions
    sessions = session_service.list_sessions(limit=5)
    print(f"\nRecent Sessions:")
    for sess in sessions:
        print(f"  - {sess.session_id}")
        print(f"    Created: {sess.created_at}")
        print(f"    State: {sess.state}")
        print(f"    Messages: {len(sess.conversation_history)}")
    
    # Test patterns
    print("\n" + "="*70)
    print("  LEARNED PATTERNS")
    print("="*70 + "\n")
    
    patterns = memory_bank.get_patterns()
    print(f"Patterns detected:")
    for key, value in patterns.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*70)
    print("  ✓ MEMORY BANK TEST COMPLETE")
    print("="*70 + "\n")
    
    return {
        "memories_stored": stats['total_memories'],
        "sessions_created": session_stats['total_sessions'],
        "patterns_identified": stats['patterns_identified']
    }


if __name__ == "__main__":
    result = asyncio.run(run_multiple_analyses())
    
    # Verify
    assert result['memories_stored'] >= 3, "Should have stored at least 3 memories"
    assert result['sessions_created'] >= 3, "Should have created at least 3 sessions"
    
    print("✓ All assertions passed!\n")