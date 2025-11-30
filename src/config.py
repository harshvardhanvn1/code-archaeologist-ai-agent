"""Configuration settings for Code Archaeologist AI Agent."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NVD_API_KEY = os.getenv("NVD_API_KEY", "")

# Gemini Model Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"
TEMPERATURE = 0.7
MAX_TOKENS = 8000

# Project Settings
PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
EXAMPLES_DIR = PROJECT_ROOT / "examples"

# Agent Configuration
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "6"))
AGENT_TIMEOUT = 300  # seconds

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"

# Tool Configuration
GIT_LOOKBACK_DAYS = 90
CVE_SEVERITY_THRESHOLD = "MEDIUM"
DOC_COVERAGE_THRESHOLD = 0.6

# Agent-specific configurations
AGENT_CONFIG = {
    "orchestrator": {
        "name": "Code Archaeologist Orchestrator",
        "description": "Coordinates technical debt analysis across multiple agents",
        "model": GEMINI_MODEL,
        "temperature": 0.3,  # Lower for more deterministic coordination
    },
    "git_history": {
        "name": "Git History Analyzer",
        "description": "Analyzes git history for code churn and risk patterns",
        "model": GEMINI_MODEL,
        "temperature": 0.5,
    },
    "dependency_scanner": {
        "name": "Dependency Scanner",
        "description": "Scans for vulnerable dependencies and CVEs",
        "model": GEMINI_MODEL,
        "temperature": 0.4,
    },
    "doc_gap": {
        "name": "Documentation Gap Analyzer",
        "description": "Identifies missing or outdated documentation",
        "model": GEMINI_MODEL,
        "temperature": 0.6,
    },
    "impact_analyzer": {
        "name": "Impact Analyzer",
        "description": "Assesses business impact of technical debt",
        "model": GEMINI_MODEL,
        "temperature": 0.7,
    },
    "report_writer": {
        "name": "Report Writer",
        "description": "Generates comprehensive technical debt reports",
        "model": GEMINI_MODEL,
        "temperature": 0.8,  # Higher for more creative reporting
    },
}

# Ensure directories exist
REPORTS_DIR.mkdir(exist_ok=True)
EXAMPLES_DIR.mkdir(exist_ok=True)
