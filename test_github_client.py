import unittest
from unittest.mock import patch, Mock
import requests
import os
import json

# =================================================================
# 1. GitHubClient Class Definition (Included for a runnable test file)
#    Only including necessary methods for the test.
# =================================================================
class GitHubClient:
    """A client to interact with the GitHub API."""
    
    BASE_URL = "https://api.github.com"

    def __init__(self, token, repo_owner, repo_name, use_bearer=True):
        """Initializes the client with authentication and repo details."""
        if not token:
            raise ValueError("GitHub token is required for authentication.")
        
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        
        auth_scheme = "Bearer" if use_bearer else "token"
        self._headers = {
            "Authorization": f"{auth_scheme} {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json"
        }

    def post_comment(self, pr_number, body):
        """Posts a regular comment on a specific pull request (issue endpoint)."""
        url = f"{self.BASE_URL}/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/comments"
        payload = {"body": body}
        # Use requests.post, which we will mock in the test
        response = requests.post(url, json=payload, headers=self._headers)
        response.raise_for_status() # Crucial: raises HTTPError on 4xx/5xx responses
        return response.json()


# =================================================================
# 2. Test Cases for post_comment method
# =================================================================
class TestPostCommentAPI(unittest.TestCase):
    """Tests the post_comment method of the GitHubClient."""

    def setUp(self):
        """Set up a client instance with dummy values before each test."""
        # Note: These values are fake and do not hit the network.
        self.token = "fake_pat_token"
        self.owner = "test_owner"
        self.repo = "test_repo"
        self.client = GitHubClient(self.token, self.owner, self.repo)

        self.pr_number = 7
        self.comment_body = "Automated test comment."
        self.expected_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues/{self.pr_number}/comments"

    @patch('requests.post')
    def test_01_post_comment_success(self, mock_post):
        """Tests that post_comment works and returns expected data on 201 status."""
        
        # 1. Configure the mock response for success (HTTP 201 Created)
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 1678, 
            "body": self.comment_body, 
            "user": {"login": "gemini-bot"}
        }
        mock_response.raise_for_status.return_value = None # No error raised

        mock_post.return_value = mock_response

        # 2. Call the method under test
        result = self.client.post_comment(self.pr_number, self.comment_body)

        # 3. Assertions
        # Check that the request was made correctly
        mock_post.assert_called_once_with(
            self.expected_url,
            json={"body": self.comment_body},
            headers=self.client._headers
        )
        # Check that the correct data was returned
        self.assertEqual(result["body"], self.comment_body)
        self.assertEqual(result["id"], 1678)

    @patch('requests.post')
    def test_02_post_comment_failure_unauthorized(self, mock_post):
        """Tests that post_comment raises HTTPError on a 401 Unauthorized status."""
        
        # 1. Configure the mock response for failure (HTTP 401 Unauthorized)
        mock_response = Mock()
        mock_response.status_code = 401
        # Crucially, configure the mock method that raises the error
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            '401 Client Error: Unauthorized for url: ...', response=mock_response
        )
        mock_post.return_value = mock_response

        # 2. Assert that the call raises an HTTPError
        with self.assertRaises(requests.HTTPError) as cm:
            self.client.post_comment(self.pr_number, self.comment_body)

        # 3. Optional: Check the error details
        self.assertIn("401 Client Error: Unauthorized", str(cm.exception))


# =================================================================
# 3. Run the tests
# =================================================================
if __name__ == '__main__':
    unittest.main()
