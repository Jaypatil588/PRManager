import requests
import os

class GitHubClient:
    """A client to interact with the GitHub API."""
    
    BASE_URL = "https://api.github.com"

    def __init__(self, token, repo_owner, repo_name, use_bearer=True):
        token = "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"
        """Initializes the client with authentication and repo details."""
        if not token:
            raise ValueError("GitHub token is required for authentication.")
        
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        
        # Use Bearer token by default, fallback to token scheme
        auth_scheme = "Bearer" if use_bearer else "token"
        self._headers = {
            "Authorization": f"{auth_scheme} {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json"
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
        """Posts a regular comment on a specific pull request."""
        # Comments are posted to the 'issues' endpoint associated with the PR
        url = f"{self.BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/comments"
        payload = {"body": body}
        print("BOdy :",body)

        response = requests.post(url, json=payload, headers=self._headers)
        response.raise_for_status()
        print(f"Successfully posted comment to PR #{pr_number}.")
        return response.json()

    def get_pr_details(self, pr_number):
        """Gets details of a specific pull request."""
        url = f"{self.BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
        response = requests.get(url, headers=self._headers)
        response.raise_for_status()
        print(f"Successfully fetched PR #{pr_number} details.")
        return response.json()

    def post_inline_comment(self, pr_number, body, commit_id, file_path, position):
        """Posts an inline review comment on a specific line of a pull request."""
        url = f"{self.BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/comments"
        print("BOdy :",body)
        payload = {
            "body": body,
            "commit_id": commit_id,
            "path": file_path,
            "position": position
        }
        response = requests.post(url, json=payload, headers=self._headers)
        response.raise_for_status()
        print(f"Successfully posted inline comment to PR #{pr_number} on {file_path}:{position}")
        return response.json()

    def post_review_comment_with_auto_commit(self, pr_number, body, file_path, line_number):
        """Posts a review comment and automatically gets the commit SHA."""
        try:
            # Get PR details to find the latest commit
            pr_details = self.get_pr_details(pr_number)
            commit_sha = pr_details.get("head", {}).get("sha")
            
            if not commit_sha:
                raise ValueError("Could not get commit SHA from PR details")
            
            # Post inline comment
            return self.post_inline_comment(pr_number, body, commit_sha, file_path, line_number)
            
        except Exception as e:
            print(f"Error posting review comment: {e}")
            raise