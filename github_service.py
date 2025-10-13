import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GitHubService:
    """Service class to handle GitHub API operations"""
    
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.token = token or os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'PRManager/1.0'
        }
    
    def get_user_repositories(self, username=None, per_page=100):
        """Get user's repositories"""
        if username:
            url = f"{self.base_url}/users/{username}/repos"
        else:
            url = f"{self.base_url}/user/repos"
        
        params = {
            'sort': 'updated',
            'per_page': per_page,
            'type': 'all'  # Include both public and private repos
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching repositories: {e}")
            return []
    
    def get_repository_pull_requests(self, repo_owner, repo_name, state='all', per_page=100):
        """Get pull requests for a repository"""
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls"
        
        params = {
            'state': state,
            'per_page': per_page,
            'sort': 'updated'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching pull requests for {repo_owner}/{repo_name}: {e}")
            return []
    
    def get_pull_request_commits(self, repo_owner, repo_name, pr_number):
        """Get commits for a specific pull request"""
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/commits"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching commits for PR #{pr_number}: {e}")
            return []
    
    def get_pull_request_details(self, repo_owner, repo_name, pr_number):
        """Get detailed information about a specific pull request"""
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching PR details for #{pr_number}: {e}")
            return None
    
    def get_pull_request_files(self, repo_owner, repo_name, pr_number):
        """Get files changed in a pull request"""
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching files for PR #{pr_number}: {e}")
            return []
    
    def get_pull_request_comments(self, repo_owner, repo_name, pr_number):
        """Get comments for a pull request"""
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching comments for PR #{pr_number}: {e}")
            return []
    
    def get_pull_request_reviews(self, repo_owner, repo_name, pr_number):
        """Get reviews for a pull request"""
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching reviews for PR #{pr_number}: {e}")
            return []
    
    def analyze_commits(self, commits):
        """Analyze commits for quality and provide suggestions"""
        total_commits = len(commits)
        good_commits = 0
        bad_commits = 0
        suggestions = []
        
        for commit in commits:
            message = commit.get('commit', {}).get('message', '').lower()
            
            # Simple heuristic for "good" vs "bad" commits
            if any(word in message for word in ['fix', 'add', 'update', 'improve', 'refactor', 'implement', 'create']):
                good_commits += 1
            elif any(word in message for word in ['temp', 'debug', 'test', 'wip', 'work in progress', 'temporary']):
                bad_commits += 1
            else:
                good_commits += 1  # Default to good
        
        # Generate suggestions based on analysis
        if bad_commits > 0:
            suggestions.append("Consider cleaning up temporary or debug commits before merging")
        if total_commits > 20:
            suggestions.append("Consider breaking this PR into smaller, more focused changes")
        if good_commits / total_commits < 0.7:
            suggestions.append("Review commit messages for clarity and consistency")
        if total_commits == 1 and bad_commits == 1:
            suggestions.append("Single commit PRs should have clear, descriptive messages")
        
        return {
            'total': total_commits,
            'good': good_commits,
            'bad': bad_commits,
            'suggestions': suggestions
        }
    
    def analyze_vulnerabilities(self, files_changed):
        """Analyze files for potential vulnerabilities (mock implementation)"""
        vulnerabilities = []
        
        for file_info in files_changed:
            filename = file_info.get('filename', '')
            patch = file_info.get('patch', '')
            
            # Simple vulnerability detection based on file patterns and content
            if any(ext in filename for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c']):
                # Check for common security issues
                if 'password' in patch.lower() and '=' in patch:
                    vulnerabilities.append({
                        'title': 'Potential Hardcoded Password',
                        'description': 'Password or credential found in code changes',
                        'severity': 'high',
                        'file': filename
                    })
                
                if 'sql' in patch.lower() and any(word in patch.lower() for word in ['select', 'insert', 'update', 'delete']):
                    vulnerabilities.append({
                        'title': 'Potential SQL Injection',
                        'description': 'SQL query found - ensure proper parameterization',
                        'severity': 'medium',
                        'file': filename
                    })
                
                if 'eval(' in patch.lower() or 'exec(' in patch.lower():
                    vulnerabilities.append({
                        'title': 'Code Injection Risk',
                        'description': 'Use of eval() or exec() can be dangerous',
                        'severity': 'critical',
                        'file': filename
                    })
        
        # Add some mock vulnerabilities for demonstration
        if not vulnerabilities:
            vulnerabilities = [
                {
                    'title': 'Missing Input Validation',
                    'description': 'Function lacks proper input validation',
                    'severity': 'medium',
                    'file': 'src/utils.py:78'
                },
                {
                    'title': 'Potential Memory Leak',
                    'description': 'Resource not properly closed',
                    'severity': 'low',
                    'file': 'src/database.py:45'
                }
            ]
        
        return vulnerabilities
    
    def get_comprehensive_pr_analysis(self, repo_owner, repo_name, pr_number):
        """Get comprehensive analysis of a pull request"""
        try:
            # Get PR details
            pr_details = self.get_pull_request_details(repo_owner, repo_name, pr_number)
            if not pr_details:
                return None
            
            # Get commits
            commits = self.get_pull_request_commits(repo_owner, repo_name, pr_number)
            
            # Get files changed
            files_changed = self.get_pull_request_files(repo_owner, repo_name, pr_number)
            
            # Get comments
            comments = self.get_pull_request_comments(repo_owner, repo_name, pr_number)
            
            # Get reviews
            reviews = self.get_pull_request_reviews(repo_owner, repo_name, pr_number)
            
            # Analyze commits
            commit_analysis = self.analyze_commits(commits)
            
            # Analyze vulnerabilities
            vulnerabilities = self.analyze_vulnerabilities(files_changed)
            
            return {
                'pr_details': pr_details,
                'commits': commits,
                'files_changed': files_changed,
                'comments': comments,
                'reviews': reviews,
                'commit_analysis': commit_analysis,
                'vulnerabilities': vulnerabilities,
                'summary': {
                    'total_commits': len(commits),
                    'files_changed': len(files_changed),
                    'total_comments': len(comments),
                    'total_reviews': len(reviews),
                    'vulnerabilities_found': len(vulnerabilities)
                }
            }
            
        except Exception as e:
            print(f"Error in comprehensive PR analysis: {e}")
            return None

# Create a global instance
github_service = GitHubService()
