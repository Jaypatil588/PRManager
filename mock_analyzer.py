"""
Mock PR Analyzer with hardcoded responses for testing and demonstration
Based on the NVIDIA hackathon chat logs and examples
"""

import json
import random
from typing import Dict, List, Any

class MockPRAnalyzer:
    def __init__(self):
        self.pr_review_responses = [
            {
                "overall_assessment": "Review is required for this pull request.",
                "concerns": [],
                "approve": False
            },
            {
                "overall_assessment": "Review is required for this pull request.",
                "concerns": [],
                "approve": False
            },
            {
                "overall_assessment": "Review is required for this pull request.",
                "concerns": [],
                "approve": False
            }
        ]
        
        self.vulnerability_responses = [
            {
                "overall_assessment": "The PR introduces a significant codebase with security, readability, and best practice concerns.",
                "concerns": [
                    {
                        "file_path": "client/app.py",
                        "line_number_start": 1,
                        "line_number_end": 411,
                        "severity": "HIGH",
                        "type": "Security",
                        "vulnerability_type": "Sensitive Data Exposure",
                        "description": "Hardcoded secret keys (e.g., GITHUB_CLIENT_SECRET, SECRET_KEY) are present in the code. These should be loaded from environment variables or a secure secret management system.",
                        "suggestion": "Replace hardcoded secrets with os.getenv() calls, ensuring secrets are never committed to the repository."
                    },
                    {
                        "file_path": "client/app.js",
                        "line_number_start": 1,
                        "line_number_end": 309,
                        "severity": "MEDIUM",
                        "type": "Readability",
                        "vulnerability_type": "Code Quality",
                        "description": "The file contains excessively long lines and inline styles, violating readability standards. Styles should be externalized, and components should be broken down for maintainability.",
                        "suggestion": "Extract inline styles into CSS classes or a stylesheet and consider splitting large components into smaller, reusable pieces."
                    },
                    {
                        "file_path": "github_service.py",
                        "line_number_start": 1,
                        "line_number_end": 256,
                        "severity": "CRITICAL",
                        "type": "Security",
                        "vulnerability_type": "Insecure Deserialization",
                        "description": "The analyze_vulnerabilities method does not properly sanitize input when checking for vulnerabilities, potentially leading to false positives or security misconfigurations.",
                        "suggestion": "Implement robust input validation and consider using established security scanning libraries to improve vulnerability detection accuracy."
                    },
                    {
                        "file_path": "client/index.html",
                        "line_number_start": 1,
                        "line_number_end": 25,
                        "severity": "LOW",
                        "type": "Best Practice",
                        "vulnerability_type": "Other",
                        "description": "The script tags use development versions of React and Babel. Production versions should be used for deployment.",
                        "suggestion": "Update script tags to use production (minified) versions of dependencies."
                    }
                ],
                "approve": False
            },
            {
                "overall_assessment": "Minor security concerns detected with overall good practices.",
                "concerns": [
                    {
                        "file_path": "app.py",
                        "line_number_start": 20,
                        "line_number_end": 25,
                        "severity": "MEDIUM",
                        "type": "Security",
                        "vulnerability_type": "Information Disclosure",
                        "description": "Debug information is being logged in production mode, which could expose sensitive system information.",
                        "suggestion": "Remove or conditionally disable debug logging in production environments."
                    }
                ],
                "approve": True
            },
            {
                "overall_assessment": "No significant security vulnerabilities detected. Code follows security best practices.",
                "concerns": [],
                "approve": True
            }
        ]
        
        self.commit_analysis_responses = [
            {
                "total_commits": 5,
                "good_commits": 4,
                "bad_commits": 1,
                "quality_score": 80,
                "suggestions": [
                    "Consider adding more descriptive commit messages",
                    "One commit has a very generic message that could be improved"
                ],
                "commit_breakdown": [
                    {
                        "sha": "abc1234",
                        "message": "Add user authentication system",
                        "quality": "good",
                        "reason": "Clear, descriptive message with specific functionality"
                    },
                    {
                        "sha": "def5678",
                        "message": "Fix bug",
                        "quality": "bad",
                        "reason": "Too generic, doesn't describe what bug was fixed"
                    },
                    {
                        "sha": "ghi9012",
                        "message": "Update API endpoints with proper error handling",
                        "quality": "good",
                        "reason": "Specific and describes the improvement made"
                    }
                ]
            },
            {
                "total_commits": 3,
                "good_commits": 3,
                "bad_commits": 0,
                "quality_score": 100,
                "suggestions": [
                    "Excellent commit message quality",
                    "All commits follow best practices"
                ],
                "commit_breakdown": [
                    {
                        "sha": "jkl3456",
                        "message": "Implement OAuth2 authentication flow",
                        "quality": "good",
                        "reason": "Clear description of feature implementation"
                    },
                    {
                        "sha": "mno7890",
                        "message": "Add input validation for user registration",
                        "quality": "good",
                        "reason": "Specific security improvement"
                    }
                ]
            }
        ]

    def analyze_pr_review(self, code_diff: str = "", pr_title: str = "", pr_description: str = "") -> Dict[str, Any]:
        """Generate a mock PR review response"""
        # Always return the simple "review is required" response
        return self.pr_review_responses[0]

    def analyze_vulnerabilities(self, code_diff: str = "", pr_title: str = "", pr_description: str = "") -> Dict[str, Any]:
        """Generate a mock vulnerability analysis response"""
        # Select a random response or use the first one for consistency
        response = random.choice(self.vulnerability_responses)
        
        # Add some dynamic elements based on input
        if "security" in pr_title.lower() or "auth" in pr_title.lower():
            # If it's a security-related PR, use the first response (has security concerns)
            response = self.vulnerability_responses[0]
        elif "fix" in pr_title.lower() or "bug" in pr_title.lower():
            # If it's a bug fix, use the second response (minor issues)
            response = self.vulnerability_responses[1]
        else:
            # Default to random selection
            response = random.choice(self.vulnerability_responses)
        
        return response

    def analyze_commits(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a mock commit analysis response"""
        # Select a random response
        response = random.choice(self.commit_analysis_responses)
        
        # Update the response with actual commit count if available
        if commits:
            response["total_commits"] = len(commits)
            response["good_commits"] = max(1, len(commits) - 1)  # Assume most commits are good
            response["bad_commits"] = min(1, len(commits) - 1)   # Assume at least one bad commit
            response["quality_score"] = int((response["good_commits"] / response["total_commits"]) * 100)
        
        return response

    def get_analysis_summary(self, pr_number: int, repo_name: str) -> Dict[str, Any]:
        """Get a comprehensive analysis summary for a PR"""
        pr_review = self.analyze_pr_review()
        vulnerabilities = self.analyze_vulnerabilities()
        commits = self.analyze_commits([])
        
        return {
            "pr_number": pr_number,
            "repo_name": repo_name,
            "pr_review": pr_review,
            "vulnerabilities": vulnerabilities,
            "commits": commits,
            "overall_approval": pr_review["approve"] and vulnerabilities["approve"],
            "risk_level": self._calculate_risk_level(pr_review, vulnerabilities)
        }
    
    def _calculate_risk_level(self, pr_review: Dict, vulnerabilities: Dict) -> str:
        """Calculate overall risk level based on review and vulnerability analysis"""
        high_severity_count = 0
        critical_severity_count = 0
        
        # Count high/critical issues from PR review
        for concern in pr_review.get("concerns", []):
            if concern.get("severity") == "HIGH":
                high_severity_count += 1
            elif concern.get("severity") == "CRITICAL":
                critical_severity_count += 1
        
        # Count high/critical issues from vulnerabilities
        for concern in vulnerabilities.get("concerns", []):
            if concern.get("severity") == "HIGH":
                high_severity_count += 1
            elif concern.get("severity") == "CRITICAL":
                critical_severity_count += 1
        
        if critical_severity_count > 0:
            return "CRITICAL"
        elif high_severity_count > 2:
            return "HIGH"
        elif high_severity_count > 0:
            return "MEDIUM"
        else:
            return "LOW"

# Global instance for easy access
mock_analyzer = MockPRAnalyzer()
