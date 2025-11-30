# Code Archaeologist AI Agent

**Multi-Agent System for Automated Technical Debt Detection**

A production-ready AI agent system that analyzes codebases to detect, quantify, and prioritize technical debt using parallel analysis and AI-powered impact assessment.

## Problem Statement

Technical debt costs the software industry an estimated $85 billion annually. Traditional technical debt detection methods are:
- Manual and time-consuming (weeks of effort)
- Inconsistent and subjective
- Limited in scope and coverage
- Reactive rather than proactive

## Solution

Code Archaeologist automates technical debt detection using a multi-agent AI system that:
- Analyzes repositories in minutes instead of weeks
- Provides comprehensive, objective analysis
- Quantifies business impact with AI-powered assessment
- Generates actionable recommendations

## Architecture

### Multi-Agent System Design
```
┌─────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                    │
│           (Coordinates workflow & synthesis)             │
└────────────┬────────────────────────────────────────────┘
             │
             ├─ PHASE 1: Parallel Analysis (3 agents)
             │  ├─→ Git History Agent (code churn detection)
             │  ├─→ CVE Scanner Agent (vulnerability detection)
             │  └─→ Documentation Gap Agent (doc coverage)
             │
             ├─ PHASE 2: Sequential Analysis
             │  └─→ Impact Analyzer Agent (AI-powered assessment)
             │
             └─ PHASE 3: Report Generation
                └─→ Report Writer Agent (synthesis & formatting)
```

### Custom Tools

1. **Git Analyzer Tool**
   - Analyzes commit history and file change frequency
   - Identifies high-churn files (code smell indicator)
   - Calculates risk scores based on change patterns

2. **CVE Scanner Tool**
   - Scans dependency files (requirements.txt, package.json, etc.)
   - Checks against vulnerability databases
   - Categorizes findings by severity (Critical/High/Medium/Low)

3. **Documentation Parser Tool**
   - Analyzes code documentation coverage using AST parsing
   - Measures docstring presence at module, class, and function levels
   - Calculates coverage percentages and identifies gaps

## Installation

### Prerequisites

- Python 3.11 or higher
- Git
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/code-archaeologist-ai-agent.git
cd code-archaeologist-ai-agent
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API key:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

## Usage

### Basic Analysis

Analyze the current directory:
```bash
python -m src.main
```

### Analyze Specific Repository
```bash
python -m src.main --repo-path /path/to/your/repository
```

### Save Report to File
```bash
python -m src.main --output reports/my_analysis.json
```

### Analysis Types
```bash
# Quick analysis (faster, less detailed)
python -m src.main --analysis-type quick

# Comprehensive analysis (default)
python -m src.main --analysis-type comprehensive

# Security-focused analysis
python -m src.main --analysis-type security-focused
```

### Example Output
```
======================================================================
  CODE ARCHAEOLOGIST AI AGENT
  Technical Debt Detection & Analysis System
======================================================================

EXECUTIVE SUMMARY
----------------------------------------------------------------------
Repository: /path/to/project
Analysis Type: comprehensive
Impact Score: 42.5/100
Severity: MEDIUM
Total Issues: 15

KEY RISKS:
  1. High code churn detected - potential stability issues
  2. Low documentation coverage - maintainability concern
  3. 3 vulnerable dependencies found

RECOMMENDATIONS:
  1. Review and refactor 8 high-churn files
  2. Improve documentation coverage to at least 70%
  3. Update vulnerable dependencies immediately

DETAILED FINDINGS
----------------------------------------------------------------------
Git History Analysis:
  Risk Score: 65/100
  Total Commits (last 90 days): 342
  High Churn Files: 8

Security Vulnerability Scan:
  Total Dependencies: 47
  Vulnerabilities: 3
    Critical: 0
    High: 1
    Medium: 2
    Low: 0

Documentation Analysis:
  Coverage: 42.0%
  Has README: True
  Total Files: 89
  Function Coverage: 67.0%
======================================================================
```

## Features

- **Multi-Agent Orchestration**: Coordinates 6 specialized AI agents
- **Parallel Execution**: Runs analysis agents concurrently for speed
- **AI-Powered Assessment**: Uses Gemini AI for impact analysis
- **Comprehensive Reporting**: Generates detailed JSON and human-readable reports
- **Custom Tool Integration**: Three production-ready analysis tools
- **Flexible CLI**: Multiple analysis modes and output formats
- **Production-Ready**: Error handling, logging, and graceful degradation

## Technical Stack

- **AI Framework**: Google Generative AI (Gemini)
- **Language**: Python 3.12
- **Key Libraries**:
  - `google-generativeai` - Gemini API integration
  - `GitPython` - Git repository analysis
  - `requests` - HTTP requests for CVE data
  - `beautifulsoup4` - HTML parsing
  - `pydantic` - Data validation
  - `pytest` - Testing framework

## Project Structure
```
code-archaeologist-ai-agent/
├── src/
│   ├── agents/
│   │   └── orchestrator.py      # Main orchestrator agent
│   ├── tools/
│   │   ├── git_analyzer.py      # Git history analysis
│   │   ├── cve_scanner.py       # Vulnerability scanning
│   │   └── doc_parser.py        # Documentation analysis
│   ├── config.py                # Configuration management
│   └── main.py                  # CLI entry point
├── tests/                       # Test suite
├── reports/                     # Generated reports
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not committed)
└── README.md                    # This file
```

## Competition Information

**Competition**: Google Agents Intensive Capstone  
**Track**: Enterprise Agents  
**Submission Date**: December 2025

### Key Concepts Demonstrated

1. **Multi-Agent Systems**: Orchestrator coordinates 6 specialized agents
2. **Custom Tools**: Three production-ready tools for analysis
3. **Session Management**: State management across agent interactions
4. **Parallel Execution**: Concurrent agent execution for performance
5. **AI Integration**: Gemini AI for intelligent impact assessment

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black src/
ruff check src/
```

### Type Checking
```bash
mypy src/
```

## Future Enhancements

- Web dashboard for visualization
- Integration with CI/CD pipelines
- Real-time monitoring and alerts
- Machine learning for trend prediction
- Support for more languages (Java, JavaScript, etc.)
- Advanced security scanning with SAST/DAST

## License

MIT License - See LICENSE file for details

## Author

Created for the Google Agents Intensive Capstone Competition

## Acknowledgments

- Google Gemini API for AI capabilities
- Google Agent Developer Kit documentation
- Kaggle 5-Day Agents Course materials

## Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/code-archaeologist-ai-agent/issues)
- Kaggle Discussion: [Competition page](https://www.kaggle.com/competitions/google-agents-intensive)

---

**Built with Google Gemini AI**
