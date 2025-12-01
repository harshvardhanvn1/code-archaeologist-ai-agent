# Code Archaeologist AI Agent - Technical Architecture

## Overview

Code Archaeologist is a production-ready multi-agent AI system for automated technical debt detection and analysis. Built for the Google Agents Intensive Capstone Project (Enterprise Agents track), it demonstrates advanced AI agent patterns including parallel execution, observability, evaluation, and stateful memory management.

**Key Metrics:**
- 3 custom tools for code analysis
- 5-phase orchestrated workflow
- Full observability stack (logging, tracing, metrics)
- LLM-as-Judge evaluation framework
- Session & memory management
- ~5 second analysis time

---

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface                             │
│                      (src/main.py)                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                            │
│              (Multi-Agent Coordinator)                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Phase 1: Parallel Execution                 │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ Git History  │  │ CVE Scanner  │  │ Doc Parser   │  │  │
│  │  │    Agent     │  │    Agent     │  │    Agent     │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │            Phase 2: Impact Analysis                      │  │
│  │              (AI-Powered Gemini)                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │            Phase 3: Report Generation                    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │            Phase 4: LLM-as-Judge Evaluation             │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Cross-Cutting Concerns                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Observability│  │   Sessions   │  │    Memory    │        │
│  │  (Logs/Trace)│  │   Service    │  │     Bank     │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Multi-Agent Orchestrator (`src/agents/orchestrator.py`)

**Purpose:** Central coordinator implementing the multi-agent workflow pattern.

**Key Features:**
- **Parallel Agent Execution:** Runs 3 analysis agents concurrently using `asyncio.gather()`
- **Sequential Processing:** Coordinates impact analysis, report generation, and evaluation
- **State Management:** Integrates with session service for workflow state tracking
- **Observability:** Full instrumentation with logging, tracing, and metrics

**Workflow Phases:**
1. **Phase 1 - Parallel Data Collection (120ms):**
   - Git History Analysis (analyze commit patterns)
   - CVE Security Scan (check dependencies)
   - Documentation Analysis (measure coverage)

2. **Phase 2 - Impact Analysis (2.5s):**
   - AI-powered analysis using Gemini 2.5 Flash Lite
   - Calculates weighted impact score
   - Determines severity level
   - Generates risk assessment

3. **Phase 3 - Report Generation (<1ms):**
   - Synthesizes findings
   - Creates executive summary
   - Formats recommendations

4. **Phase 4 - Evaluation (2s):**
   - LLM-as-Judge quality assessment
   - 4-dimension scoring (completeness, accuracy, actionability, clarity)
   - Identifies strengths and weaknesses

**Code Pattern:**
```python
# Parallel execution using asyncio
tasks = [
    asyncio.create_task(asyncio.to_thread(analyze_git_history, ...)),
    asyncio.create_task(asyncio.to_thread(scan_dependencies_for_cves, ...)),
    asyncio.create_task(asyncio.to_thread(analyze_documentation, ...))
]
git_results, cve_results, doc_results = await asyncio.gather(*tasks)
```

---

### 2. Custom Tools

#### 2.1 Git Analyzer (`src/tools/git_analyzer.py`)

**Purpose:** Analyzes Git commit history to identify code churn patterns.

**Algorithm:**
1. Retrieve commit history (last 90 days)
2. Track file modification frequencies
3. Identify high-churn files (>20% of commits)
4. Calculate risk score (0-100)

**Output:**
```python
{
    "risk_score": 40,
    "total_commits": 12,
    "high_churn_files": ["src/main.py"],
    "lookback_days": 90,
    "analyzed_at": "2025-11-30T..."
}
```

**Key Insight:** High churn correlates with code complexity and defect density.

#### 2.2 CVE Scanner (`src/tools/cve_scanner.py`)

**Purpose:** Scans dependencies for known security vulnerabilities.

**Supported Files:**
- `requirements.txt` (Python)
- `package.json` (Node.js)
- `Gemfile` (Ruby)
- `pom.xml` (Java)

**Output:**
```python
{
    "vulnerabilities": [],
    "total_dependencies": 15,
    "severity_summary": {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }
}
```

**Implementation:** Parses dependency files and checks against known vulnerability database (expandable to use NVD API).

#### 2.3 Documentation Parser (`src/tools/doc_parser.py`)

**Purpose:** Analyzes code documentation coverage using Python AST.

**Metrics:**
- Overall coverage percentage
- Function-level docstrings
- Class-level docstrings
- README presence

**Algorithm:**
1. Walk directory tree for .py files
2. Parse each file using Python AST
3. Check for docstrings in modules, functions, classes
4. Calculate coverage ratios

**Output:**
```python
{
    "coverage": 0.65,
    "has_readme": true,
    "total_files": 23,
    "documented_files": 15,
    "function_coverage": 0.94,
    "class_coverage": 1.0
}
```

---

### 3. Observability Layer

#### 3.1 Structured Logging (`src/observability/logger.py`)

**Framework:** Structlog with JSON formatting

**Features:**
- Correlation ID tracking across requests
- Contextual logging with automatic field binding
- Log levels: DEBUG, INFO, WARNING, ERROR
- ISO timestamp formatting

**Example Output:**
```json
{
  "correlation_id": "req_6a024f266367_1764554034",
  "repo_path": ".",
  "analysis_type": "comprehensive",
  "event": "analysis_started",
  "level": "info",
  "timestamp": "2025-12-01T01:53:54.879736Z"
}
```

**Pattern:**
```python
logger = get_logger(__name__, correlation_id)
logger.info("event_name", key1="value1", key2="value2")
```

#### 3.2 Distributed Tracing (`src/observability/tracer.py`)

**Framework:** OpenTelemetry

**Features:**
- Trace ID and Span ID generation
- Parent-child span relationships
- Automatic duration measurement
- Exception recording
- Console exporter for development

**Example Span:**
```json
{
  "name": "analyze_repository",
  "trace_id": "0xfc080ed17cdfce1db7ded2a3cf4d99a0",
  "span_id": "0x0b4aa687428eca60",
  "attributes": {
    "function.name": "analyze_repository",
    "status": "success",
    "duration_ms": 9137.614
  }
}
```

**Decorator Pattern:**
```python
@trace_function("operation_name")
async def my_function():
    # Function automatically traced
    pass
```

#### 3.3 Metrics Collection (`src/observability/metrics.py`)

**Purpose:** Performance monitoring and operational metrics

**Metric Types:**
- **Counters:** analyses_completed, analyses_failed
- **Timers:** full_analysis duration, tool execution times
- **Gauges:** Impact scores, quality scores

**Statistics:**
```python
{
    "timers": {
        "full_analysis": {
            "count": 3,
            "mean": 5.2,
            "median": 5.3,
            "p95": 6.3
        }
    }
}
```

---

### 4. Evaluation Framework

#### 4.1 LLM-as-Judge (`src/evaluation/llm_judge.py`)

**Purpose:** AI-powered quality assessment of analysis results

**Model:** Gemini 2.5 Flash Lite (temperature: 0.3 for consistency)

**Evaluation Dimensions:**
1. **Completeness (0-100):** Coverage of all analysis aspects
2. **Accuracy (0-100):** Technical soundness of findings
3. **Actionability (0-100):** Practicality of recommendations
4. **Clarity (0-100):** Report structure and readability

**Process:**
1. Construct evaluation prompt with analysis results
2. Send to Gemini for assessment
3. Parse structured response
4. Extract scores and feedback

**Example Output:**
```python
{
    "overall_score": 85,
    "dimension_scores": {
        "completeness": 80,
        "accuracy": 90,
        "actionability": 95,
        "clarity": 90
    },
    "strengths": [...],
    "weaknesses": [...],
    "recommendations": [...]
}
```

**Innovation:** Meta-evaluation - AI judging AI quality.

#### 4.2 Metrics Aggregation (`src/evaluation/metrics.py`)

**Purpose:** Track evaluation metrics over time

**Features:**
- Quality score tracking
- Performance baselines
- User feedback integration
- Continuous improvement insights

---

### 5. State Management

#### 5.1 Session Service (`src/sessions/session_service.py`)

**Purpose:** InMemorySessionService pattern for short-term state management

**Features:**
- **Session Creation:** Unique session IDs with metadata
- **Conversation History:** Message tracking (user/assistant/system)
- **State Updates:** Key-value state storage
- **Session Lifecycle:** Creation, retrieval, update, deletion

**Use Case:** Track active analysis workflows

**Example:**
```python
session = session_service.create_session(
    metadata={"repo_path": ".", "analysis_type": "comprehensive"}
)
session.add_message("system", "Starting analysis...")
session.update_state("current_phase", "parallel_data_collection")
```

**Storage:** In-memory with LRU eviction (max 100 sessions)

#### 5.2 Memory Bank (`src/memory/memory_bank.py`)

**Purpose:** Long-term storage of historical analyses

**Features:**
- **Analysis Storage:** Persist complete analysis results
- **Pattern Detection:** Automatically identify trends
- **Memory Search:** Query by repo, severity, tags
- **Insight Learning:** Store learned insights over time

**Pattern Detection:**
- Severity distribution across analyses
- Average impact scores
- Common risk patterns
- Recurring recommendations

**Example Pattern:**
```python
{
    "severity_distribution": {"low": 3, "medium": 1},
    "average_impact_score": 24.9,
    "common_risks": {
        "Low documentation": 4,
        "High code churn": 2
    }
}
```

**Persistence:** Optional disk storage (JSON format)

---

## Technology Stack

### Core Technologies
- **Language:** Python 3.12
- **AI Model:** Google Gemini 2.5 Flash Lite
- **Async Framework:** asyncio
- **CLI Framework:** argparse

### Dependencies
- **google-generativeai:** Gemini API integration
- **GitPython:** Git repository analysis
- **structlog:** Structured logging
- **opentelemetry-api/sdk:** Distributed tracing
- **beautifulsoup4:** HTML parsing
- **pydantic:** Data validation
- **pytest:** Testing framework

### Development Tools
- **black:** Code formatting
- **ruff:** Linting
- **mypy:** Type checking

---

## Design Decisions

### 1. Why Not Use ADK?

**Decision:** Build directly with google-generativeai instead of ADK

**Rationale:**
- ADK not available via PyPI (pre-installed in Kaggle only)
- Direct implementation gives more control and transparency
- All required concepts (multi-agent, tools, sessions) implemented manually
- Competition judges evaluate concepts, not specific frameworks

### 2. Parallel vs Sequential Agents

**Decision:** Run data collection agents in parallel, analysis sequentially

**Rationale:**
- Git/CVE/Doc analyses are independent → parallel execution saves 200ms+
- Impact analysis depends on all three → must be sequential
- Total time: ~5 seconds instead of ~8 seconds

### 3. In-Memory vs Persistent Storage

**Decision:** In-memory for sessions, optional persistence for memory bank

**Rationale:**
- Sessions are short-lived (single analysis)
- Memory bank benefits from persistence across runs
- Hybrid approach balances performance and durability

### 4. LLM-as-Judge Temperature

**Decision:** Use temperature=0.3 for evaluation

**Rationale:**
- Lower temperature = more consistent scoring
- Evaluation should be deterministic
- Reduces randomness in quality assessment

---

## Performance Characteristics

### Timing Breakdown
- **Phase 1 (Parallel):** ~120ms
- **Phase 2 (Impact Analysis):** ~2.5s
- **Phase 3 (Report):** <1ms
- **Phase 4 (Evaluation):** ~2s
- **Total:** ~5 seconds

### Scalability
- **Concurrent Analyses:** Supports multiple simultaneous analyses
- **Memory Footprint:** Low (~50MB per analysis)
- **Session Limit:** 100 active sessions (configurable)
- **Memory Storage:** Unlimited (limited by disk)

---

## Testing Strategy

### Test Coverage
1. **Unit Tests:** Individual tools (`tests/test_tools.py`)
2. **Integration Tests:** Observability stack (`tests/test_observability_evaluation.py`)
3. **End-to-End Tests:** Memory persistence (`tests/test_memory_persistence.py`)

### Test Results
- 100% pass rate
- All observability components verified
- Memory/session persistence validated
- Multi-analysis workflows tested

---

## Future Enhancements

### Potential Improvements
1. **Real CVE Integration:** Connect to NVD API for live vulnerability data
2. **Multi-Language Support:** Extend beyond Python to Java, JavaScript, etc.
3. **Cloud Deployment:** Deploy to Google Cloud Run with Agent Engine
4. **Persistent Storage:** Add PostgreSQL/Redis for production scale
5. **Real-time Dashboard:** WebSocket-based monitoring UI
6. **Historical Trend Analysis:** ML-powered pattern recognition

---

## Compliance with Competition Requirements

### Required Features 

**Multi-Agent System:**
- Orchestrator agent coordinating workflow
- Parallel execution of 3 analysis agents
- Sequential impact and evaluation agents

**Custom Tools:**
- Git Analyzer (code churn detection)
- CVE Scanner (security analysis)
- Documentation Parser (coverage analysis)

**Sessions & Memory:**
- InMemorySessionService for state tracking
- Memory Bank for long-term storage
- Pattern detection and learning

**Observability:**
- Structured logging (Structlog)
- Distributed tracing (OpenTelemetry)
- Metrics collection

**Evaluation:**
- LLM-as-Judge framework
- Multi-dimensional quality scoring

**Gemini Usage:**
- Gemini 2.5 Flash Lite for impact analysis
- Gemini for evaluation (LLM-as-Judge)

**Code Quality:**
- Professional formatting (no emojis)
- Comprehensive docstrings
- Error handling
- No hardcoded API keys

**Documentation:**
- README.md with overview
- ARCHITECTURE.md (this document)
- Code comments

---

## Repository Structure
```
code-archaeologist-ai-agent/
├── src/
│   ├── agents/
│   │   └── orchestrator.py          # Multi-agent coordinator
│   ├── tools/
│   │   ├── git_analyzer.py          # Custom tool #1
│   │   ├── cve_scanner.py           # Custom tool #2
│   │   └── doc_parser.py            # Custom tool #3
│   ├── observability/
│   │   ├── logger.py                # Structured logging
│   │   ├── tracer.py                # Distributed tracing
│   │   └── metrics.py               # Performance metrics
│   ├── evaluation/
│   │   ├── llm_judge.py             # LLM-as-Judge
│   │   └── metrics.py               # Evaluation metrics
│   ├── sessions/
│   │   └── session_service.py       # Session management
│   ├── memory/
│   │   └── memory_bank.py           # Long-term memory
│   ├── config.py                    # Configuration
│   └── main.py                      # CLI interface
├── tests/
│   ├── test_tools.py                # Tool tests
│   ├── test_observability_evaluation.py  # Observability tests
│   └── test_memory_persistence.py   # Memory/session tests
├── README.md                         # Project overview
├── ARCHITECTURE.md                   # This document
├── requirements.txt                  # Dependencies
└── .env.example                      # Environment template
```

---

## Getting Started

### Installation
```bash
# Clone repository
git clone https://github.com/harshvardhanvn1/code-archaeologist-ai-agent.git
cd code-archaeologist-ai-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Usage
```bash
# Run analysis
python -m src.main

# Save report
python -m src.main --output report.json

# Run tests
python -m tests.test_tools
python -m tests.test_memory_persistence
```

---

## Contact

**Project:** Code Archaeologist AI Agent  
**Track:** Enterprise Agents  
**Competition:** Google Agents Intensive Capstone 2025  
**Repository:** https://github.com/harshvardhanvn1/code-archaeologist-ai-agent

---

**Built with for the Google Agents Intensive Course**