import os
import json
import requests
from flask import Flask, request, redirect, url_for, session, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

REPOSITORIES_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Repositories - PR Manager</title>
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
        
        .page-title {
            font-size: 2rem;
            margin-bottom: 2rem;
            color: #333;
        }
        
        .repos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }
        
        .repo-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .repo-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        
        .repo-name {
            font-size: 1.2rem;
            font-weight: 600;
            color: #0366d6;
            text-decoration: none;
            margin-bottom: 0.5rem;
            display: block;
        }
        
        .repo-name:hover {
            text-decoration: underline;
        }
        
        .repo-description {
            color: #666;
            margin-bottom: 1rem;
            line-height: 1.5;
        }
        
        .repo-meta {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .repo-language {
            background: #e1e4e8;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        
        .analyze-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
            width: 100%;
        }
        
        .analyze-btn:hover {
            background: #218838;
        }
        
        .auto-merge-section {
            background: #f8f9fa;
            border: 2px solid #e1e4e8;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .auto-merge-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #333;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .auto-merge-controls {
            display: flex;
            align-items: center;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        .toggle-switch {
            position: relative;
            width: 50px;
            height: 24px;
            background: #ccc;
            border-radius: 12px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .toggle-switch.active {
            background: #28a745;
        }
        
        .toggle-slider {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            transition: transform 0.3s;
        }
        
        .toggle-switch.active .toggle-slider {
            transform: translateX(26px);
        }
        
        .slider-container {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            min-width: 200px;
        }
        
        .slider {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
        }
        
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
        }
        
        .slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
            border: none;
        }
        
        .slider-value {
            text-align: center;
            font-weight: 600;
            color: #667eea;
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
        <h1 class="page-title">Your Repositories</h1>
        
        <!-- Auto-Merge Settings Section -->
        <div class="auto-merge-section">
            <div class="auto-merge-title">
                ⚙️ Global Auto-Merge Settings
            </div>
            <div class="auto-merge-controls">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-weight: 600;">Auto Merge:</span>
                    <div class="toggle-switch" onclick="toggleGlobalAutoMerge()">
                        <div class="toggle-slider"></div>
                    </div>
                </div>
                
                <div class="slider-container">
                    <label style="font-weight: 600;">Vulnerability Threshold (%)</label>
                    <input type="range" class="slider" min="0" max="100" value="10" id="globalVulnThreshold" oninput="updateGlobalThreshold(this.value)">
                    <div class="slider-value" id="globalThresholdValue">10%</div>
                </div>
            </div>
        </div>
        
        <div id="repos-container" class="loading">
            Loading your repositories...
        </div>
    </div>
    
    <script>
        // Global auto-merge settings
        let globalAutoMerge = false;
        let globalVulnThreshold = 10;
        
        function toggleGlobalAutoMerge() {
            globalAutoMerge = !globalAutoMerge;
            const toggle = document.querySelector('.toggle-switch');
            toggle.classList.toggle('active', globalAutoMerge);
            console.log('Global Auto Merge:', globalAutoMerge ? 'ON' : 'OFF');
        }
        
        function updateGlobalThreshold(value) {
            globalVulnThreshold = parseInt(value);
            document.getElementById('globalThresholdValue').textContent = value + '%';
            console.log('Global Vulnerability Threshold:', globalVulnThreshold + '%');
        }
        
        // Fetch repositories from the API
        fetch('/api/repositories', {
            credentials: 'same-origin'
        })
            .then(response => response.json())
            .then(repos => {
                const container = document.getElementById('repos-container');
                
                if (repos.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #666;">No repositories found.</p>';
                    return;
                }
                
                container.innerHTML = '<div class="repos-grid">' + 
                    repos.map(repo => `
                        <div class="repo-card">
                            <a href="${repo.html_url}" target="_blank" class="repo-name">${repo.name}</a>
                            <p class="repo-description">${repo.description || 'No description available'}</p>
                            <div class="repo-meta">
                                <span>⭐ ${repo.stargazers_count}</span>
                                <span>🍴 ${repo.forks_count}</span>
                                ${repo.language ? `<span class="repo-language">${repo.language}</span>` : ''}
                            </div>
                            <div style="display: flex; gap: 0.5rem;">
                                <button class="analyze-btn" onclick="analyzeRepo('${repo.full_name}')" style="flex: 1;">
                                    🔍 Analyze PRs
                                </button>
                                <button class="analyze-btn" onclick="viewCommits('${repo.full_name}')" style="flex: 1; background: #17a2b8;">
                                    📝 View Commits
                                </button>
                            </div>
                        </div>
                    `).join('') + '</div>';
            })
            .catch(error => {
                document.getElementById('repos-container').innerHTML = 
                    '<p style="text-align: center; color: #dc3545;">Error loading repositories. Please try again.</p>';
                console.error('Error:', error);
            });
        
        function analyzeRepo(repoFullName) {
            // Redirect to PR listing page for the selected repository
            window.location.href = `/repository/${encodeURIComponent(repoFullName)}/prs`;
        }
        
        function viewCommits(repoFullName) {
            // Redirect to commits page for the selected repository
            window.location.href = `/repository/${encodeURIComponent(repoFullName)}/commits`;
        }
    </script>
</body>
</html>
"""

PR_LISTING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PRs - {{ repo_name }}</title>
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
        
        .tabs {
            display: flex;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e1e4e8;
        }
        
        .tab {
            padding: 1rem 2rem;
            background: none;
            border: none;
            font-size: 1rem;
            cursor: pointer;
            color: #666;
            border-bottom: 2px solid transparent;
            transition: all 0.3s;
        }
        
        .tab.active {
            color: #0366d6;
            border-bottom-color: #0366d6;
        }
        
        .tab:hover {
            color: #0366d6;
        }
        
        .prs-container {
            display: none;
        }
        
        .prs-container.active {
            display: block;
        }
        
        .pr-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .pr-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        
        .pr-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }
        
        .pr-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #0366d6;
            text-decoration: none;
            margin-bottom: 0.5rem;
        }
        
        .pr-title:hover {
            text-decoration: underline;
        }
        
        .pr-number {
            color: #666;
            font-size: 0.9rem;
        }
        
        .pr-meta {
            display: flex;
            gap: 1rem;
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 1rem;
        }
        
        .pr-description {
            color: #555;
            margin-bottom: 1rem;
            line-height: 1.5;
        }
        
        .commits-section {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .commits-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        .commits-list {
            max-height: 200px;
            overflow-y: auto;
        }
        
        .commit-item {
            display: flex;
            gap: 0.5rem;
            padding: 0.3rem 0;
            border-bottom: 1px solid #e1e4e8;
            font-size: 0.9rem;
        }
        
        .commit-item:last-child {
            border-bottom: none;
        }
        
        .commit-sha {
            color: #0366d6;
            font-family: monospace;
            min-width: 60px;
        }
        
        .commit-message {
            color: #555;
            flex: 1;
        }
        
        .commit-controls {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-top: 0.5rem;
        }
        
        .commit-toggle-switch {
            position: relative;
            width: 40px;
            height: 20px;
            background: #ccc;
            border-radius: 10px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .commit-toggle-switch.active {
            background: #28a745;
        }
        
        .commit-toggle-slider {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 16px;
            height: 16px;
            background: white;
            border-radius: 50%;
            transition: transform 0.3s;
        }
        
        .commit-toggle-switch.active .commit-toggle-slider {
            transform: translateX(20px);
        }
        
        .commit-patch {
            background: #f8f9fa;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 0.8rem;
            margin-top: 0.5rem;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.8rem;
            line-height: 1.4;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }
        
        .commit-patch-header {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .patch-toggle {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.3rem 0.8rem;
            border-radius: 4px;
            font-size: 0.7rem;
            cursor: pointer;
        }
        
        .patch-toggle:hover {
            background: #5a6fd8;
        }
        
        .analyze-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .analyze-btn:hover {
            background: #5a6fd8;
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
            <span>{{ repo_name }}</span>
        </div>
        
        <h1 class="page-title">Pull Requests</h1>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('open')">Open PRs</button>
            <button class="tab" onclick="showTab('closed')">Closed PRs</button>
        </div>
        
        <div id="prs-container" class="loading">
            Loading pull requests...
        </div>
    </div>
    
    <script>
        let prsData = null;
        
        function showTab(tab) {
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            // Show corresponding PRs
            displayPRs(tab);
        }
        
        function displayPRs(activeTab = 'open') {
            if (!prsData) return;
            
            const container = document.getElementById('prs-container');
            const prs = activeTab === 'open' ? prsData.open : prsData.closed;
            
            if (prs.length === 0) {
                container.innerHTML = `<p style="text-align: center; color: #666;">No ${activeTab} pull requests found.</p>`;
                return;
            }
            
            container.innerHTML = prs.map(pr => `
                <div class="pr-card">
                    <div class="pr-header">
                        <div>
                            <a href="${pr.html_url}" target="_blank" class="pr-title">${pr.title}</a>
                            <div class="pr-number">#${pr.number}</div>
                        </div>
                        <button class="analyze-btn" onclick="analyzePR(${pr.number}, '${pr.title.replace(/'/g, "\\'")}')">
                            🔍 Analyze PR
                        </button>
                    </div>
                    
                    <div class="pr-meta">
                        <span>👤 ${pr.user.login}</span>
                        <span>📅 ${new Date(pr.created_at).toLocaleDateString()}</span>
                        <span>💬 ${pr.comments} comments</span>
                    </div>
                    
                    <div class="pr-description">
                        ${pr.body ? pr.body.substring(0, 200) + (pr.body.length > 200 ? '...' : '') : 'No description available'}
                    </div>
                    
                    ${activeTab === 'open' ? `
                        <div class="commits-section">
                            <div class="commits-title">📝 Commits (${pr.commits})</div>
                            <div class="commits-list" id="commits-${pr.number}">
                                <div style="text-align: center; color: #666; padding: 1rem;">Loading commits...</div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `).join('');
            
            // Load commits for each PR
            prs.forEach(pr => loadCommits(pr.number));
        }
        
        function loadCommits(prNumber) {
            fetch(`/api/repository/{{ repo_name }}/pr/${prNumber}/commits`, {
                credentials: 'same-origin'
            })
                .then(response => response.json())
                .then(commits => {
                    const container = document.getElementById(`commits-${prNumber}`);
                    if (commits.length === 0) {
                        container.innerHTML = '<p style="color: #666; text-align: center;">No commits found</p>';
                        return;
                    }
                    
                    container.innerHTML = commits.map((commit, index) => `
                        <div class="commit-item">
                            <span class="commit-sha">${commit.sha.substring(0, 7)}</span>
                            <span class="commit-message">${commit.commit.message.split('\\n')[0]}</span>
                            
                            <div class="commit-controls">
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <span style="font-size: 0.8rem; color: #666;">Auto-merge:</span>
                                    <div class="commit-toggle-switch" onclick="toggleCommitAutoMerge(${prNumber}, ${index})">
                                        <div class="commit-toggle-slider"></div>
                                    </div>
                                </div>
                                <button class="patch-toggle" onclick="toggleCommitPatch(${prNumber}, ${index})">
                                    📄 Show Patch
                                </button>
                            </div>
                            
                            <div class="commit-patch" id="patch-${prNumber}-${index}" style="display: none;">
                                <div class="commit-patch-header">
                                    <span>Code Changes</span>
                                    <button class="patch-toggle" onclick="toggleCommitPatch(${prNumber}, ${index})">
                                        ✕ Hide
                                    </button>
                                </div>
                                <div id="patch-content-${prNumber}-${index}">
                                    Loading patch...
                                </div>
                            </div>
                        </div>
                    `).join('');
                })
                .catch(error => {
                    document.getElementById(`commits-${prNumber}`).innerHTML = 
                        '<p style="color: #dc3545; text-align: center;">Error loading commits</p>';
                });
        }
        
        function toggleCommitAutoMerge(prNumber, commitIndex) {
            const toggle = document.querySelector(`#commits-${prNumber} .commit-item:nth-child(${commitIndex + 1}) .commit-toggle-switch`);
            toggle.classList.toggle('active');
            const isActive = toggle.classList.contains('active');
            console.log(`PR ${prNumber}, Commit ${commitIndex}: Auto-merge ${isActive ? 'ON' : 'OFF'}`);
        }
        
        function toggleCommitPatch(prNumber, commitIndex) {
            const patchDiv = document.getElementById(`patch-${prNumber}-${commitIndex}`);
            const isVisible = patchDiv.style.display !== 'none';
            
            if (isVisible) {
                patchDiv.style.display = 'none';
            } else {
                patchDiv.style.display = 'block';
                // Load patch content if not already loaded
                const patchContent = document.getElementById(`patch-content-${prNumber}-${commitIndex}`);
                if (patchContent.textContent === 'Loading patch...') {
                    loadCommitPatch(prNumber, commitIndex);
                }
            }
        }
        
        function loadCommitPatch(prNumber, commitIndex) {
            const patchContent = document.getElementById(`patch-content-${prNumber}-${commitIndex}`);
            patchContent.innerHTML = '<div style="color: #666;">Loading patch...</div>';
            
            // Get the commit SHA from the commit item
            const commitItem = document.querySelector(`#commits-${prNumber} .commit-item:nth-child(${commitIndex + 1})`);
            const commitSha = commitItem.querySelector('.commit-sha').textContent.trim();
            
            // Fetch the actual patch from the API
            fetch(`/api/repository/{{ repo_name }}/commit/${commitSha}/patch`, {
                credentials: 'same-origin'
            })
                .then(response => response.json())
                .then(data => {
                    if (data.patch) {
                        // Format the patch for better display
                        const formattedPatch = data.patch
                            .replace(/</g, '&lt;')
                            .replace(/>/g, '&gt;')
                            .replace(/^\+/gm, '<span style="color: #28a745; background: #d4edda;">+')
                            .replace(/^-/gm, '<span style="color: #dc3545; background: #f8d7da;">-')
                            .replace(/(<span[^>]*>.*<\/span>)/gm, '$1</span>');
                        
                        patchContent.innerHTML = `
                            <div style="font-family: monospace; font-size: 0.8rem; line-height: 1.4; white-space: pre-wrap; word-break: break-all;">
                                ${formattedPatch}
                            </div>
                        `;
                    } else {
                        patchContent.innerHTML = '<div style="color: #dc3545;">Failed to load patch</div>';
                    }
                })
                .catch(error => {
                    console.error('Error loading patch:', error);
                    patchContent.innerHTML = '<div style="color: #dc3545;">Error loading patch</div>';
                });
        }
        
        function analyzePR(prNumber, prTitle) {
            window.location.href = `/repository/{{ repo_name }}/pr/${prNumber}/analyze`;
        }
        
        // Load PRs on page load
        fetch('/api/repository/{{ repo_name }}/prs', {
            credentials: 'same-origin'
        })
            .then(response => response.json())
            .then(data => {
                prsData = data;
                displayPRs();
            })
            .catch(error => {
                document.getElementById('prs-container').innerHTML = 
                    '<p style="text-align: center; color: #dc3545;">Error loading pull requests. Please try again.</p>';
                console.error('Error:', error);
            });
    </script>
</body>
</html>
"""

PR_ANALYSIS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PR Analysis - {{ pr_title }}</title>
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
        
        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
        }
        
        .analysis-card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .card-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: #333;
            border-bottom: 2px solid #e1e4e8;
            padding-bottom: 0.5rem;
        }
        
        .settings-section {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .setting-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .setting-label {
            font-weight: 500;
            color: #333;
        }
        
        .toggle-switch {
            position: relative;
            width: 50px;
            height: 24px;
            background: #ccc;
            border-radius: 12px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .toggle-switch.active {
            background: #28a745;
        }
        
        .toggle-slider {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            transition: transform 0.3s;
        }
        
        .toggle-switch.active .toggle-slider {
            transform: translateX(26px);
        }
        
        .slider-container {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .slider {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
        }
        
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
        }
        
        .slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
            border: none;
        }
        
        .slider-value {
            text-align: center;
            font-weight: 600;
            color: #667eea;
        }
        
        .commits-stats {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.8rem;
            border-radius: 8px;
            font-weight: 500;
        }
        
        .stat-item.total {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .stat-item.good {
            background: #e8f5e8;
            color: #2e7d32;
        }
        
        .stat-item.bad {
            background: #ffebee;
            color: #c62828;
        }
        
        .stat-number {
            font-size: 1.2rem;
            font-weight: 700;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e1e4e8;
            border-radius: 10px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        
        .suggestions {
            margin-top: 1.5rem;
        }
        
        .suggestions h4 {
            margin-bottom: 1rem;
            color: #333;
        }
        
        .suggestion-item {
            padding: 0.5rem 0;
            color: #555;
            border-bottom: 1px solid #e1e4e8;
        }
        
        .suggestion-item:last-child {
            border-bottom: none;
        }
        
        .vulnerabilities {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .vuln-item {
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .vuln-item.critical {
            background: #ffebee;
            border-left-color: #f44336;
        }
        
        .vuln-item.high {
            background: #fff3e0;
            border-left-color: #ff9800;
        }
        
        .vuln-item.medium {
            background: #e3f2fd;
            border-left-color: #2196f3;
        }
        
        .vuln-item.low {
            background: #e8f5e8;
            border-left-color: #4caf50;
        }
        
        .vuln-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        .vuln-description {
            color: #555;
            margin-bottom: 0.5rem;
            line-height: 1.5;
        }
        
        .vuln-file {
            font-size: 0.9rem;
            color: #666;
            font-family: monospace;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
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
            <span>{{ pr_title }}</span>
        </div>
        
        <h1 class="page-title">PR Analysis</h1>
        
        <div class="analysis-grid">
            <!-- Settings Section -->
            <div class="analysis-card">
                <h2 class="card-title">⚙️ Settings</h2>
                <div class="settings-section">
                    <div class="setting-item">
                        <span class="setting-label">Auto Merge</span>
                        <div class="toggle-switch" onclick="toggleAutoMerge()">
                            <div class="toggle-slider"></div>
                        </div>
                    </div>
                    
                    <div class="slider-container">
                        <label class="setting-label">Vulnerability Threshold (%)</label>
                        <input type="range" class="slider" min="0" max="100" value="10" id="vulnThreshold" oninput="updateThreshold(this.value)">
                        <div class="slider-value" id="thresholdValue">10%</div>
                    </div>
                </div>
            </div>
            
            <!-- Commits Analysis Section -->
            <div class="analysis-card">
                <h2 class="card-title">📝 Commits Analysis</h2>
                <div class="commits-stats" id="commitsAnalysis">
                    <div class="loading">Analyzing commits...</div>
                </div>
            </div>
            
            <!-- Vulnerabilities Section -->
            <div class="analysis-card">
                <h2 class="card-title">🔒 Vulnerabilities</h2>
                <div class="vulnerabilities" id="vulnerabilities">
                    <div class="loading">Scanning for vulnerabilities...</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let autoMergeEnabled = false;
        let vulnerabilityThreshold = 10;
        
        function toggleAutoMerge() {
            autoMergeEnabled = !autoMergeEnabled;
            const toggle = document.querySelector('.toggle-switch');
            toggle.classList.toggle('active', autoMergeEnabled);
        }
        
        function updateThreshold(value) {
            vulnerabilityThreshold = value;
            document.getElementById('thresholdValue').textContent = value + '%';
        }
        
        // Load analysis data
        fetch('/api/repository/{{ repo_name }}/pr/{{ pr_number }}/analysis', {
            credentials: 'same-origin'
        })
            .then(response => response.json())
            .then(data => {
                displayCommitsAnalysis(data.commits);
                displayVulnerabilities(data.vulnerabilities);
            })
            .catch(error => {
                console.error('Error loading analysis:', error);
                document.getElementById('commitsAnalysis').innerHTML = 
                    '<p style="color: #dc3545;">Error loading commits analysis</p>';
                document.getElementById('vulnerabilities').innerHTML = 
                    '<p style="color: #dc3545;">Error loading vulnerabilities</p>';
            });
        
        function displayCommitsAnalysis(commitsData) {
            const container = document.getElementById('commitsAnalysis');
            const { good, bad, total, suggestions } = commitsData;
            const goodPercentage = Math.round((good / total) * 100);
            
            container.innerHTML = `
                <div class="stat-item total">
                    <span>Total Commits</span>
                    <span class="stat-number">${total}</span>
                </div>
                
                <div class="stat-item good">
                    <span>Good Commits</span>
                    <span class="stat-number">${good}</span>
                </div>
                
                <div class="stat-item bad">
                    <span>Bad Commits</span>
                    <span class="stat-number">${bad}</span>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${goodPercentage}%"></div>
                </div>
                
                <div style="text-align: center; font-weight: bold; color: #333;">
                    ${goodPercentage}% Good Commits
                </div>
                
                <div class="suggestions">
                    <h4>💡 Suggestions:</h4>
                    ${suggestions.map(s => `<div class="suggestion-item">• ${s}</div>`).join('')}
                </div>
            `;
        }
        
        function displayVulnerabilities(vulns) {
            const container = document.getElementById('vulnerabilities');
            
            if (vulns.length === 0) {
                container.innerHTML = '<p style="color: #28a745; text-align: center;">✅ No vulnerabilities found!</p>';
                return;
            }
            
            container.innerHTML = vulns.map(vuln => `
                <div class="vuln-item ${vuln.severity}">
                    <div class="vuln-title">${vuln.title}</div>
                    <div class="vuln-description">${vuln.description}</div>
                    <div class="vuln-file">📁 ${vuln.file}</div>
                </div>
            `).join('');
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
