"""CVE scanner tool for detecting vulnerable dependencies."""
from pathlib import Path
from typing import Dict, List, Any
import re
import requests
from datetime import datetime
import time


def scan_dependencies_for_cves(
    repo_path: str,
    nvd_api_key: str = ""
) -> Dict[str, Any]:
    """
    Scan repository dependencies for known CVEs.
    
    Args:
        repo_path: Path to the repository
        nvd_api_key: Optional NVD API key for higher rate limits
        
    Returns:
        Dictionary containing vulnerability findings
    """
    try:
        repo_path = Path(repo_path).resolve()
        
        # Find dependency files
        dependency_files = {
            "requirements.txt": _parse_requirements,
            "package.json": _parse_package_json,
            "Gemfile": _parse_gemfile,
            "pom.xml": _parse_pom_xml,
        }
        
        found_dependencies = []
        for filename, parser in dependency_files.items():
            file_path = repo_path / filename
            if file_path.exists():
                deps = parser(file_path)
                found_dependencies.extend(deps)
        
        if not found_dependencies:
            return {
                "vulnerabilities": [],
                "total_dependencies": 0,
                "scan_status": "no_dependency_files_found",
                "scanned_at": datetime.now().isoformat()
            }
        
        # Scan for CVEs (simplified - in production would use NVD API)
        vulnerabilities = _check_vulnerabilities(found_dependencies, nvd_api_key)
        
        # Calculate severity summary
        severity_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "UNKNOWN")
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return {
            "vulnerabilities": vulnerabilities,
            "total_dependencies": len(found_dependencies),
            "severity_summary": severity_counts,
            "scan_status": "completed",
            "scanned_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Scan failed: {str(e)}",
            "vulnerabilities": [],
            "total_dependencies": 0,
            "scan_status": "error"
        }


def _parse_requirements(file_path: Path) -> List[Dict[str, str]]:
    """Parse Python requirements.txt file."""
    dependencies = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Simple parsing: package==version or package>=version
                    match = re.match(r'([a-zA-Z0-9\-_]+)([>=<]+)([0-9\.]+)', line)
                    if match:
                        dependencies.append({
                            "name": match.group(1),
                            "version": match.group(3),
                            "ecosystem": "pypi"
                        })
    except Exception:
        pass
    return dependencies


def _parse_package_json(file_path: Path) -> List[Dict[str, str]]:
    """Parse Node.js package.json file."""
    dependencies = []
    try:
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
            for dep_type in ["dependencies", "devDependencies"]:
                if dep_type in data:
                    for name, version in data[dep_type].items():
                        # Remove ^ or ~ from version
                        clean_version = version.lstrip('^~')
                        dependencies.append({
                            "name": name,
                            "version": clean_version,
                            "ecosystem": "npm"
                        })
    except Exception:
        pass
    return dependencies


def _parse_gemfile(file_path: Path) -> List[Dict[str, str]]:
    """Parse Ruby Gemfile."""
    dependencies = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                match = re.match(r"gem\s+['\"]([^'\"]+)['\"].*?['\"]([0-9\.]+)['\"]", line)
                if match:
                    dependencies.append({
                        "name": match.group(1),
                        "version": match.group(2),
                        "ecosystem": "rubygems"
                    })
    except Exception:
        pass
    return dependencies


def _parse_pom_xml(file_path: Path) -> List[Dict[str, str]]:
    """Parse Java pom.xml file."""
    # Simplified - would use XML parser in production
    dependencies = []
    return dependencies


def _check_vulnerabilities(
    dependencies: List[Dict[str, str]],
    nvd_api_key: str = ""
) -> List[Dict[str, Any]]:
    """
    Check dependencies against vulnerability databases.
    
    Note: This is a simplified implementation for demonstration.
    In production, would make actual NVD API calls.
    """
    vulnerabilities = []
    
    # Known vulnerable packages for demo (simplified)
    # In production, would query NVD API or OSV API
    known_vulns = {
        "requests": {
            "2.25.0": {
                "cve": "CVE-2021-DEMO",
                "severity": "HIGH",
                "description": "Demonstration vulnerability"
            }
        },
        "django": {
            "2.2.0": {
                "cve": "CVE-2020-DEMO",
                "severity": "CRITICAL",
                "description": "Demonstration SQL injection"
            }
        }
    }
    
    for dep in dependencies:
        name = dep["name"].lower()
        version = dep["version"]
        
        # Check against known vulnerabilities
        if name in known_vulns and version in known_vulns[name]:
            vuln_info = known_vulns[name][version]
            vulnerabilities.append({
                "package": name,
                "version": version,
                "ecosystem": dep["ecosystem"],
                "cve_id": vuln_info["cve"],
                "severity": vuln_info["severity"],
                "description": vuln_info["description"]
            })
    
    # In production, would make API calls like:
    # if nvd_api_key:
    #     headers = {"apiKey": nvd_api_key}
    #     response = requests.get(f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={name}", headers=headers)
    #     # Process response...
    
    return vulnerabilities


# Test function
if __name__ == "__main__":
    import json
    result = scan_dependencies_for_cves(".")
    print(json.dumps(result, indent=2))