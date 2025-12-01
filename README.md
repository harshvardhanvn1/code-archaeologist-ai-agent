# Code Archaeologist AI Agent

A production-ready multi-agent AI system for automated technical debt detection and analysis, built with Google Gemini and advanced agent orchestration patterns.

**Competition:** Google Agents Intensive Capstone Project 2025  
**Track:** Enterprise Agents  
**Repository:** https://github.com/harshvardhanvn1/code-archaeologist-ai-agent

---

## Problem Statement

Technical debt costs the software industry an estimated $85 billion annually. Yet most organizations lack automated, intelligent systems to detect and prioritize technical debt before it becomes critical.

Code Archaeologist solves this by:
- Automatically analyzing repositories for technical debt patterns
- Using AI to assess business impact and prioritize remediation
- Providing actionable, evidence-based recommendations
- Learning from historical analyses to improve over time

---

## Solution Overview

Code Archaeologist is a multi-agent AI system that orchestrates parallel analysis workflows, integrates observability patterns, and uses LLM-as-Judge evaluation to ensure high-quality outputs.

**Key Capabilities:**
- Parallel execution of 3 specialized analysis agents
- AI-powered impact assessment using Gemini 2.5 Flash Lite
- Full observability stack (structured logging, distributed tracing, metrics)
- Quality evaluation with LLM-as-Judge pattern
- Session management and long-term memory for continuous learning
- Complete analysis in approximately 5 seconds

---

## Architecture
```
User Command
    |
    v
CLI Interface (main.py)
    |
    v
Orchestrator Agent
    |
    +---> PHASE 1: Parallel Execution (133ms)
    |     |
    |     +---> Git History Analyzer
    |     +---> CVE Security Scanner  
    |     +---> Documentation Parser
    |
    +---> PHASE 2: AI Impact Analysis (2.7s)
    |     |
    |     +---> Gemini 2.5 Flash Lite
    |
    +---> PHASE 3: Report Generation (<1ms)
    |
    +---> PHASE 4: LLM-as-Judge Evaluation (1.5s)
    |
    v
Results + Session Storage + Memory Bank
```

For detailed technical architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Features

### Multi-Agent System
- **Orchestrator Agent:** Coordinates 5-phase workflow with parallel and sequential execution
- **Git History Agent:** Analyzes commit patterns and identifies high-churn files
- **CVE Scanner Agent:** Detects security vulnerabilities in dependencies
- **Documentation Agent:** Measures code documentation coverage using AST analysis
- **Impact Analyzer:** AI-powered business impact assessment
- **Report Writer:** Synthesizes findings into actionable reports

### Custom Tools (3 Required)
1. **Git Analyzer** - Commit pattern analysis with risk scoring
2. **CVE Scanner** - Multi-language dependency vulnerability detection
3. **Documentation Parser** - Python AST-based coverage measurement

### Observability (Production-Grade)
- **Structured Logging:** JSON logs with correlation IDs (Structlog)
- **Distributed Tracing:** OpenTelemetry spans with parent-child relationships
- **Metrics Collection:** Performance tracking and aggregation
- **Full Request Tracing:** Track analysis from start to finish

### Evaluation & Quality
- **LLM-as-Judge:** Gemini evaluates analysis quality on 4 dimensions
- **Quality Scoring:** Completeness, Accuracy, Actionability, Clarity (0-100)
- **Automated Feedback:** Identifies strengths and weaknesses

### State Management
- **Session Service:** InMemorySessionService pattern for active workflow tracking
- **Memory Bank:** Long-term storage with pattern detection
- **Historical Learning:** System learns from past analyses
- **Pattern Recognition:** Automatically identifies recurring issues

---

## Installation

### Prerequisites
- Python 3.12 or higher
- Git installed
- Google API key (get one at https://aistudio.google.com/app/api_keys)

### Setup
```bash
# Clone repository
git clone https://github.com/harshvardhanvn1/code-archaeologist-ai-agent.git
cd code-archaeologist-ai-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

---

## Usage

### Basic Analysis
```bash
# Analyze current directory
python -m src.main

# Analyze specific repository
python -m src.main --repo-path /path/to/repo

# Save report to file
python -m src.main --output report.json
```

### Analysis Types
```bash
# Quick analysis
python -m src.main --analysis-type quick

# Comprehensive analysis (default)
python -m src.main --analysis-type comprehensive

# Security-focused analysis
python -m src.main --analysis-type security-focused
```

### Output Options
```bash
# JSON only (no summary)
python -m src.main --json-only

# Verbose logging
python -m src.main --verbose

# Complete example
python -m src.main --repo-path . --output results.json --verbose
```

---

## Example Output
```
======================================================================
  CODE ARCHAEOLOGIST AI AGENT
  Technical Debt Detection & Analysis System
======================================================================

EXECUTIVE SUMMARY
----------------------------------------------------------------------
Repository: .
Impact Score: 21.9/100
Severity: LOW
Total Issues: 1

QUALITY EVALUATION (LLM-as-Judge)
----------------------------------------------------------------------
Overall Quality Score: 75/100
  Completeness: 70/100
  Accuracy: 80/100
  Actionability: 90/100
  Clarity: 80/100

KEY RISKS:
  1. No critical risks identified

RECOMMENDATIONS:
  1. Review and refactor 1 high-churn files
  2. Improve documentation coverage to at least 70%

DETAILED FINDINGS
----------------------------------------------------------------------

Git History Analysis:
  Risk Score: 40/100
  Total Commits (last 90 days): 16
  High Churn Files: 1

Security Vulnerability Scan:
  Total Dependencies: 15
  Vulnerabilities: 0

Documentation Analysis:
  Coverage: 67.0%
  Function Coverage: 94.0%
```

---

## Project Structure
```
code-archaeologist-ai-agent/
├── src/
│   ├── agents/
│   │   └── orchestrator.py          # Multi-agent coordinator
│   ├── tools/
│   │   ├── git_analyzer.py          # Git history analysis
│   │   ├── cve_scanner.py           # Security scanning
│   │   └── doc_parser.py            # Documentation analysis
│   ├── observability/
│   │   ├── logger.py                # Structured logging
│   │   ├── tracer.py                # Distributed tracing
│   │   └── metrics.py               # Performance metrics
│   ├── evaluation/
│   │   ├── llm_judge.py             # LLM-as-Judge evaluation
│   │   └── metrics.py               # Quality metrics
│   ├── sessions/
│   │   └── session_service.py       # Session management
│   ├── memory/
│   │   └── memory_bank.py           # Long-term memory
│   ├── config.py                    # Configuration
│   └── main.py                      # CLI interface
├── tests/
│   ├── test_tools.py                # Tool unit tests
│   ├── test_observability_evaluation.py
│   └── test_memory_persistence.py
├── ARCHITECTURE.md                   # Technical documentation
├── README.md                         # This file
├── requirements.txt                  # Dependencies
└── .env.example                      # Environment template
```

---

## Testing

Run the test suite to verify all components:
```bash
# Test custom tools
python -m tests.test_tools

# Test observability and evaluation
python -m tests.test_observability_evaluation

# Test memory persistence
python -m tests.test_memory_persistence
```

All tests should pass with 100% success rate.

---

## Technology Stack

**Core:**
- Python 3.12
- Google Gemini 2.5 Flash Lite
- asyncio for parallel execution

**Observability:**
- Structlog (structured logging)
- OpenTelemetry (distributed tracing)
- Custom metrics collection

**Analysis:**
- GitPython (repository analysis)
- Python AST (code parsing)
- BeautifulSoup4 (dependency parsing)

**Development:**
- pytest (testing)
- black (formatting)
- ruff (linting)

---

## Performance

- **Analysis Time:** ~4-5 seconds for typical repositories
- **Parallel Execution:** 3 agents run concurrently (saves ~200ms)
- **Memory Usage:** ~50MB per analysis
- **Scalability:** Supports concurrent analyses

---

## Design Principles

1. **Modularity:** Each agent and tool is independent and testable
2. **Observability First:** Every operation is logged, traced, and measured
3. **Quality Assurance:** LLM-as-Judge ensures consistent output quality
4. **Continuous Learning:** Memory Bank improves recommendations over time
5. **Production Ready:** Error handling, validation, and professional code quality

---

## Competition Requirements

This project demonstrates all required concepts for the Google Agents Intensive Capstone:

**Multi-Agent System:**
- [COMPLETE] Orchestrator with parallel and sequential execution
- [COMPLETE] Multiple specialized agents

**Custom Tools:**
- [COMPLETE] Git Analyzer
- [COMPLETE] CVE Scanner
- [COMPLETE] Documentation Parser

**Sessions & Memory:**
- [COMPLETE] InMemorySessionService
- [COMPLETE] Memory Bank with persistence

**Observability:**
- [COMPLETE] Structured logging
- [COMPLETE] Distributed tracing
- [COMPLETE] Metrics collection

**Evaluation:**
- [COMPLETE] LLM-as-Judge framework
- [COMPLETE] Quality scoring

**Gemini Usage:**
- [COMPLETE] Impact analysis
- [COMPLETE] Quality evaluation

---

## Documentation

- **README.md** (this file) - Project overview and usage
- **ARCHITECTURE.md** - Detailed technical architecture and design decisions
- **Code Comments** - Comprehensive inline documentation

---

## Future Enhancements

- Integration with real CVE databases (NVD API)
- Multi-language support (Java, JavaScript, Go)
- Cloud deployment on Google Cloud Run
- Real-time dashboard with WebSocket updates
- Machine learning for pattern prediction

---

## License

This project was created for the Google Agents Intensive Capstone Project 2025.

---

## Acknowledgments

Built for the Google Agents Intensive Course (November 2025), demonstrating advanced AI agent patterns, observability, and production-ready architecture.

**Repository:** https://github.com/harshvardhanvn1/code-archaeologist-ai-agent