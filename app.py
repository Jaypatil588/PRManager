import os
import json
import requests
from flask import Flask, request, redirect, url_for, session, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from github_service import github_service, GitHubService

# Load environment variables
load_dotenv()

# Debug: Check if environment variables are loaded
print(f"GITHUB_CLIENT_ID: {os.getenv('GITHUB_CLIENT_ID')}")
print(f"GITHUB_CLIENT_SECRET: {'***' if os.getenv('GITHUB_CLIENT_SECRET') else 'None'}")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
CORS(app)

# OAuth configuration
oauth = OAuth(app)

# GitHub OAuth configuration
github = oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Backend API Routes
@app.route('/api/user')
def api_user():
    """API endpoint to get current user info"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify(session['user'])

@app.route('/api/repositories')
def api_repositories():
    """API endpoint to get user repositories"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get user's access token and create GitHub service instance
        access_token = session['user']['access_token']
        user_github_service = GitHubService(token=access_token)
        
        # Use GitHub service to fetch repositories
        repos = user_github_service.get_user_repositories()
        
        # Filter and format repository data
        formatted_repos = []
        for repo in repos:
            formatted_repos.append({
                'id': repo['id'],
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo['description'],
                'html_url': repo['html_url'],
                'language': repo['language'],
                'stargazers_count': repo['stargazers_count'],
                'forks_count': repo['forks_count'],
                'updated_at': repo['updated_at'],
                'private': repo['private']
            })
        
        return jsonify(formatted_repos)
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch repositories: {str(e)}'}), 500

@app.route('/api/repository/<path:repo_name>/prs')
def api_repository_prs(repo_name):
    """API endpoint to get repository pull requests"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Decode URL-encoded repository name
    from urllib.parse import unquote
    repo_name = unquote(repo_name)
    print(f"Fetching PRs for repository: {repo_name}")
    
    try:
        # Split repository name into owner and repo
        if '/' not in repo_name:
            return jsonify({'error': 'Invalid repository name format'}), 400
        
        repo_owner, repo_name_only = repo_name.split('/', 1)
        
        # Get user's access token and create GitHub service instance
        access_token = session['user']['access_token']
        user_github_service = GitHubService(token=access_token)
        
        # Fetch open PRs
        open_prs = user_github_service.get_repository_pull_requests(repo_owner, repo_name_only, state='open')
        
        # Fetch closed PRs
        closed_prs = user_github_service.get_repository_pull_requests(repo_owner, repo_name_only, state='closed')
        
        # Format PR data
        def format_pr(pr):
            return {
                'number': pr['number'],
                'title': pr['title'],
                'body': pr['body'],
                'state': pr['state'],
                'html_url': pr['html_url'],
                'user': {'login': pr['user']['login']},
                'created_at': pr['created_at'],
                'comments': pr['comments'],
                'commits': pr['commits']
            }
        
        return jsonify({
            'open': [format_pr(pr) for pr in open_prs],
            'closed': [format_pr(pr) for pr in closed_prs]
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch pull requests: {str(e)}'}), 500

@app.route('/api/repository/<path:repo_name>/pr/<int:pr_number>/commits')
def api_pr_commits(repo_name, pr_number):
    """API endpoint to get PR commits"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Decode URL-encoded repository name
    from urllib.parse import unquote
    repo_name = unquote(repo_name)
    
    try:
        # Split repository name into owner and repo
        if '/' not in repo_name:
            return jsonify({'error': 'Invalid repository name format'}), 400
        
        repo_owner, repo_name_only = repo_name.split('/', 1)
        
        # Get user's access token and create GitHub service instance
        access_token = session['user']['access_token']
        user_github_service = GitHubService(token=access_token)
        
        # Get commits using GitHub service
        commits = user_github_service.get_pull_request_commits(repo_owner, repo_name_only, pr_number)
        
        # Format commit data
        formatted_commits = []
        for commit in commits:
            formatted_commits.append({
                'sha': commit['sha'],
                'commit': {
                    'message': commit['commit']['message']
                }
            })
        
        return jsonify(formatted_commits)
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch commits: {str(e)}'}), 500

@app.route('/api/repository/<path:repo_name>/pr/<int:pr_number>/analysis')
def api_pr_analysis(repo_name, pr_number):
    """API endpoint to get PR analysis data"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Decode URL-encoded repository name
    from urllib.parse import unquote
    repo_name = unquote(repo_name)
    
    try:
        # Split repository name into owner and repo
        if '/' not in repo_name:
            return jsonify({'error': 'Invalid repository name format'}), 400
        
        repo_owner, repo_name_only = repo_name.split('/', 1)
        
        # Get user's access token and create GitHub service instance
        access_token = session['user']['access_token']
        user_github_service = GitHubService(token=access_token)
        
        # Get comprehensive PR analysis using GitHub service
        analysis = user_github_service.get_comprehensive_pr_analysis(repo_owner, repo_name_only, pr_number)
        
        if not analysis:
            return jsonify({'error': 'Failed to analyze PR'}), 500
        
        # Return the analysis data
        return jsonify({
            'commits': analysis['commit_analysis'],
            'vulnerabilities': analysis['vulnerabilities'],
            'summary': analysis['summary'],
            'pr_details': {
                'title': analysis['pr_details']['title'],
                'body': analysis['pr_details']['body'],
                'state': analysis['pr_details']['state'],
                'created_at': analysis['pr_details']['created_at'],
                'user': analysis['pr_details']['user']['login']
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to analyze PR: {str(e)}'}), 500

# Keep the original PR analysis functionality
def main():
    """Original PR analysis functionality"""
    from pr_analyzer import PRAnalyzer
    
    # Initialize the analyzer
    analyzer = PRAnalyzer()
    
    # Example usage
    repo_owner = "Jaypatil588"
    repo_name = "PRManager"
    pr_number = 1
    
    print(f"Analyzing PR #{pr_number} in {repo_owner}/{repo_name}")
    
    # Analyze the PR
    result = analyzer.analyze_pr(repo_owner, repo_name, pr_number)
    
    if result:
        print("Analysis completed successfully!")
        print(f"Summary: {result.get('summary', 'No summary available')}")
    else:
        print("Analysis failed!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)