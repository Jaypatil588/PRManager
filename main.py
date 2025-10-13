#!/usr/bin/env python3
"""
Main entry point for PR Manager application.
This file combines both frontend and backend functionality.
"""

import os
import sys
import requests
from flask import Flask, request, redirect, url_for, session, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from github_service import GitHubService

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

# HTML templates
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PR Manager - Login</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 90%;
        }
        .logo {
            font-size: 2.5rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }
        .github-btn {
            background: #24292e;
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s ease;
            width: 100%;
            justify-content: center;
        }
        .github-btn:hover {
            background: #1a1e22;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
        .github-icon {
            width: 20px;
            height: 20px;
        }
        .features {
            margin-top: 2rem;
            text-align: left;
        }
        .feature {
            display: flex;
            align-items: center;
            margin-bottom: 0.8rem;
            color: #555;
        }
        .feature-icon {
            margin-right: 0.8rem;
            font-size: 1.2rem;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🚀 PR Manager</div>
        <div class="subtitle">Analyze and manage your GitHub pull requests with AI-powered insights</div>
        
        <a href="/login/github" class="github-btn">
            <svg class="github-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            Continue with GitHub
        </a>
        
        <div class="features">
            <div class="feature">
                <span class="feature-icon">🔍</span>
                <span>Analyze PR quality and commits</span>
            </div>
            <div class="feature">
                <span class="feature-icon">🛡️</span>
                <span>Detect security vulnerabilities</span>
            </div>
            <div class="feature">
                <span class="feature-icon">📊</span>
                <span>Get actionable insights</span>
            </div>
            <div class="feature">
                <span class="feature-icon">⚡</span>
                <span>Auto-merge recommendations</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

LOGIN_SUCCESS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Successful - PR Manager</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .success-container {
            background: white;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
            width: 90%;
        }
        .success-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .success-title {
            font-size: 2rem;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 1rem;
        }
        .success-message {
            color: #666;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }
        .redirect-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            color: #555;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="success-container">
        <div class="success-icon">✅</div>
        <div class="success-title">Login Successful!</div>
        <div class="success-message">
            Welcome to PR Manager! You're now authenticated with GitHub.
        </div>
        <div class="redirect-info">
            Redirecting to your repositories...
        </div>
    </div>
    
    <script>
        // Redirect to repositories page after 2 seconds
        setTimeout(() => {
            window.location.href = '/repositories';
        }, 2000);
    </script>
</body>
</html>
"""

# Import the HTML templates from the frontend file
import sys
sys.path.append('client')
from frontend import REPOSITORIES_PAGE, PR_LISTING_PAGE, PR_ANALYSIS_PAGE

# Commits page template
COMMITS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Commits - {{ repo_name }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #333;
        }
        
        .header {
            background: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .user-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
        }
        
        .logout-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
            transition: background 0.3s;
        }
        
        .logout-btn:hover {
            background: #c82333;
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .breadcrumb {
            margin-bottom: 1rem;
            color: #666;
        }
        
        .breadcrumb a {
            color: #0366d6;
            text-decoration: none;
        }
        
        .breadcrumb a:hover {
            text-decoration: underline;
        }
        
        .page-title {
            font-size: 2rem;
            margin-bottom: 2rem;
            color: #333;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            margin-top: 0.5rem;
        }
        
        .commits-container {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .commit-item {
            display: flex;
            gap: 1rem;
            padding: 1rem;
            border-bottom: 1px solid #e1e4e8;
            transition: background 0.3s;
        }
        
        .commit-item:hover {
            background: #f8f9fa;
        }
        
        .commit-item:last-child {
            border-bottom: none;
        }
        
        .commit-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        
        .commit-content {
            flex: 1;
        }
        
        .commit-message {
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        .commit-meta {
            display: flex;
            gap: 1rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .commit-sha {
            font-family: monospace;
            color: #0366d6;
            text-decoration: none;
        }
        
        .commit-sha:hover {
            text-decoration: underline;
        }
        
        .loading {
            text-align: center;
            padding: 3rem;
            color: #666;
            font-size: 1.1rem;
        }
        
        .loading::after {
            content: '';
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            margin: 2rem 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🚀 PR Manager</div>
        <div class="user-info">
            <img src="{{ user.avatar_url }}" alt="Avatar" class="user-avatar">
            <span>{{ user.name or user.login }}</span>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="breadcrumb">
            <a href="/repositories">Repositories</a> > 
            <a href="/repository/{{ repo_name }}/prs">{{ repo_name }}</a> > 
            <span>Commits</span>
        </div>
        
        <h1 class="page-title">Repository Commits</h1>
        
        <div id="stats-container" class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="total-commits">-</div>
                <div class="stat-label">Total Commits</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="good-commits">-</div>
                <div class="stat-label">Good Commits</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="bad-commits">-</div>
                <div class="stat-label">Bad Commits</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="quality-score">-</div>
                <div class="stat-label">Quality Score</div>
            </div>
        </div>
        
        <div class="commits-container">
            <div id="commits-list" class="loading">
                Loading commits...
            </div>
        </div>
    </div>
    
    <script>
        // Load commits data
        fetch('/api/repository/{{ repo_name }}/commits', {
            credentials: 'same-origin'
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('commits-list').innerHTML = 
                        `<div class="error">Error: ${data.error}</div>`;
                    return;
                }
                
                displayStats(data.analysis);
                displayCommits(data.commits);
            })
            .catch(error => {
                document.getElementById('commits-list').innerHTML = 
                    '<div class="error">Error loading commits. Please try again.</div>';
                console.error('Error:', error);
            });
        
        function displayStats(analysis) {
            document.getElementById('total-commits').textContent = analysis.total;
            document.getElementById('good-commits').textContent = analysis.good;
            document.getElementById('bad-commits').textContent = analysis.bad;
            
            const qualityScore = Math.round((analysis.good / analysis.total) * 100);
            document.getElementById('quality-score').textContent = qualityScore + '%';
        }
        
        function displayCommits(commits) {
            const container = document.getElementById('commits-list');
            
            if (commits.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #666;">No commits found.</p>';
                return;
            }
            
            container.innerHTML = commits.map(commit => {
                const author = commit.author || commit.commit.author;
                const avatar = author.avatar_url || 'https://via.placeholder.com/40';
                const authorName = author.login || author.name || 'Unknown';
                const commitDate = new Date(commit.commit.author.date).toLocaleDateString();
                const shortSha = commit.sha.substring(0, 7);
                
                return `
                    <div class="commit-item">
                        <img src="${avatar}" alt="${authorName}" class="commit-avatar">
                        <div class="commit-content">
                            <div class="commit-message">${commit.commit.message.split('\\n')[0]}</div>
                            <div class="commit-meta">
                                <a href="${commit.html_url}" target="_blank" class="commit-sha">${shortSha}</a>
                                <span>by ${authorName}</span>
                                <span>on ${commitDate}</span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
    </script>
</body>
</html>
"""

# Frontend Routes
@app.route('/')
def index():
    """Main page - serves React app or redirects to login"""
    if 'user' in session:
        return redirect(url_for('repositories'))
    
    return LOGIN_PAGE

@app.route('/app.js')
def serve_app_js():
    """Serve the React app JavaScript"""
    return send_from_directory('client', 'app.js')

@app.route('/login/github')
def login_github():
    """Initiate GitHub OAuth login"""
    redirect_uri = url_for('github_callback', _external=True)
    print(f"Redirect URI: {redirect_uri}")
    return github.authorize_redirect(redirect_uri)

@app.route('/callback/github')
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        token = github.authorize_access_token()
        if token is None:
            return "Access denied: You denied the request to authenticate.", 400
        
        # Get user info
        resp = github.get('user', token=token)
        user_info = resp.json()
        
        # Store user info in session
        session['user'] = {
            'id': user_info['id'],
            'login': user_info['login'],
            'name': user_info.get('name'),
            'email': user_info.get('email'),
            'avatar_url': user_info['avatar_url'],
            'access_token': token['access_token']
        }
        
        return LOGIN_SUCCESS_PAGE
        
    except Exception as e:
        return f"Error during authentication: {str(e)}", 400

@app.route('/repositories')
def repositories():
    """User repositories page"""
    if 'user' not in session:
        return redirect(url_for('index'))
    
    return render_template_string(REPOSITORIES_PAGE, user=session['user'])

@app.route('/repository/<path:repo_name>/prs')
def repository_prs(repo_name):
    """Repository PR listing page"""
    if 'user' not in session:
        return redirect(url_for('index'))
    
    # Decode URL-encoded repository name
    from urllib.parse import unquote
    repo_name = unquote(repo_name)
    
    return render_template_string(PR_LISTING_PAGE, user=session['user'], repo_name=repo_name)

@app.route('/repository/<path:repo_name>/commits')
def repository_commits(repo_name):
    """Repository commits page"""
    if 'user' not in session:
        return redirect(url_for('index'))
    
    # Decode URL-encoded repository name
    from urllib.parse import unquote
    repo_name = unquote(repo_name)
    
    return render_template_string(COMMITS_PAGE, user=session['user'], repo_name=repo_name)

@app.route('/repository/<path:repo_name>/pr/<int:pr_number>/analyze')
def pr_analysis(repo_name, pr_number):
    """PR analysis page"""
    if 'user' not in session:
        return redirect(url_for('index'))
    
    # Decode URL-encoded repository name
    from urllib.parse import unquote
    repo_name = unquote(repo_name)
    
    # Get PR title for display
    try:
        access_token = session['user']['access_token']
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(f'https://api.github.com/repos/{repo_name}/pulls/{pr_number}', headers=headers)
        response.raise_for_status()
        pr_data = response.json()
        pr_title = pr_data['title']
        
    except Exception as e:
        pr_title = f"PR #{pr_number}"
    
    return render_template_string(PR_ANALYSIS_PAGE, user=session['user'], repo_name=repo_name, pr_number=pr_number, pr_title=pr_title)

@app.route('/dashboard')
def dashboard():
    """User dashboard after successful login"""
    if 'user' not in session:
        return redirect(url_for('index'))
    
    return redirect(url_for('repositories'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/debug')
def debug_session():
    """Debug session page"""
    with open('debug_session.html', 'r') as f:
        return f.read()

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
                'comments_url': pr.get('comments_url', ''),
                'commits_url': pr.get('commits_url', ''),
                'updated_at': pr.get('updated_at', ''),
                'closed_at': pr.get('closed_at', ''),
                'merged_at': pr.get('merged_at', '')
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

@app.route('/api/repository/<path:repo_name>/commits')
def api_repository_commits(repo_name):
    """API endpoint to get all commits for a repository"""
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
        
        # Get all commits for the repository
        commits = user_github_service.get_repository_commits(repo_owner, repo_name_only)
        
        # Analyze commits
        commit_analysis = user_github_service.analyze_commits(commits)
        
        return jsonify({
            'commits': commits,
            'analysis': commit_analysis,
            'total_count': len(commits)
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch commits: {str(e)}'}), 500

@app.route('/api/repository/<path:repo_name>/commit/<commit_sha>/patch')
def api_commit_patch(repo_name, commit_sha):
    """API endpoint to get patch for a specific commit"""
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
        
        # Get commit patch
        patch = user_github_service.get_commit_patch(repo_owner, repo_name_only, commit_sha)
        
        if patch is None:
            return jsonify({'error': 'Failed to fetch commit patch'}), 500
        
        return jsonify({
            'patch': patch,
            'commit_sha': commit_sha
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch commit patch: {str(e)}'}), 500

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
