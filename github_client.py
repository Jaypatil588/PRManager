import requests
import os

class GitHubClient:
    """A client to interact with the GitHub API."""
    
    BASE_URL = "https://api.github.com"

    def __init__(self, token, repo_owner, repo_name):
        """Initializes the client with authentication and repo details."""
        if not token:
            raise ValueError("GitHub token is required for authentication.")
        
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        # Prefer 'token' scheme for classic PATs; many setups still expect it.
        # Callers using fine-grained tokens will also work; GitHub accepts both in most cases.
        self._headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def get_open_prs(self):
        """Fetches all open pull requests for the repository."""
        url = f"{self.BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/pulls?state=open"
        response = requests.get(url, headers=self._headers)
        response.raise_for_status()  # Will raise an exception for bad responses (4xx or 5xx)
        print("Successfully fetched open pull requests.")
        return response.json()

    def get_pr_diff(self, pr_number):
        """Fetches the diff (file changes) for a specific pull request."""
        # We add a special 'Accept' header for the diff format
        diff_headers = self._headers.copy()
        diff_headers["Accept"] = "application/vnd.github.v3.diff"
        
        url = f"{self.BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
        response = requests.get(url, headers=diff_headers)
        response.raise_for_status()
        print(f"Successfully fetched diff for PR #{pr_number}.")
        return response.text

    def post_comment(self, pr_number, body):
        """Posts a comment on a specific pull request."""
        # Comments are posted to the 'issues' endpoint associated with the PR
        url = f"{self.BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/comments"
        payload = {"body": body}
        response = requests.post(url, json=payload, headers=self._headers)
        response.raise_for_status()
        print(f"Successfully posted comment to PR #{pr_number}.")
        return response.json()