import os
import json
import requests
from flask import Flask, request, redirect, url_for, session, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🚀 PR Manager</div>
        <div class="subtitle">Automated Pull Request Analysis</div>
        <a href="/login/github" class="github-btn">
            <svg class="github-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            Continue with GitHub
        </a>
    </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PR Manager - Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            margin: 0;
            padding: 0;
            min-height: 100vh;
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
            color: #333;
        }
        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
        }
        .logout-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
        }
        .logout-btn:hover {
            background: #c82333;
        }
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        .welcome-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .welcome-title {
            font-size: 2rem;
            color: #333;
            margin-bottom: 0.5rem;
        }
        .welcome-subtitle {
            color: #666;
            font-size: 1.1rem;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .feature-title {
            font-size: 1.5rem;
            color: #333;
            margin-bottom: 1rem;
        }
        .feature-description {
            color: #666;
            line-height: 1.6;
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
        <div class="welcome-card">
            <h1 class="welcome-title">Welcome to PR Manager!</h1>
            <p class="welcome-subtitle">You're successfully logged in with GitHub. Start analyzing your pull requests with AI-powered insights.</p>
        </div>
        
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <h3 class="feature-title">AI Code Analysis</h3>
                <p class="feature-description">Get intelligent code reviews and suggestions powered by advanced AI models.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3 class="feature-title">PR Analytics</h3>
                <p class="feature-description">Track pull request metrics and identify patterns in your development workflow.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3 class="feature-title">Automated Reviews</h3>
                <p class="feature-description">Automatically review pull requests and provide detailed feedback and recommendations.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main login page - serve React frontend"""
    return send_from_directory('.', 'index.html')

@app.route('/app.js')
def serve_app_js():
    """Serve React app JavaScript"""
    return send_from_directory('.', 'app.js')

@app.route('/login/github')
def github_login():
    """Initiate GitHub OAuth login"""
    redirect_uri = url_for('github_callback', _external=True)
    return github.authorize_redirect(redirect_uri)

@app.route('/callback/github')
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        token = github.authorize_access_token()
        if token is None:
            return jsonify({'error': 'Failed to obtain access token'}), 400
        
        # Get user information from GitHub
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
        
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        return jsonify({'error': f'OAuth callback failed: {str(e)}'}), 400

@app.route('/dashboard')
def dashboard():
    """User dashboard after successful login"""
    if 'user' not in session:
        return redirect(url_for('index'))
    
    return render_template_string(DASHBOARD_PAGE, user=session['user'])

@app.route('/logout')
def logout():
    """Logout user and clear session"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/user')
def api_user():
    """API endpoint to get current user info"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify(session['user'])

# Keep the original PR analysis functionality
def main():
    """Original PR analysis functionality"""
    from pr_analyzer import PRAnalyzer
    webhook_url = "https://flask-hello-world-eight-lac.vercel.app/webhookCommits"

    try:
        resp = requests.get(webhook_url, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        print(json.dumps({"error": f"Failed to fetch webhook data: {exc}"}))
        return

    if not isinstance(payload, list) or not payload:
        print(json.dumps({"error": "Webhook returned empty or invalid payload"}))
        return

    latest = payload[-1]
    code_diff = None

    commits = latest.get("commits")
    if isinstance(commits, list) and commits:
        code_diff = commits[-1].get("code_changes")
    if not code_diff:
        code_diff = latest.get("code_changes")

    # If only testing comment posting, skip analyzer entirely
    test_only = os.getenv("TEST_COMMENT") == "1"
    if not code_diff and not test_only:
        print(json.dumps({"error": "No code_changes diff found in payload"}))
        return

    review = None
    if not test_only:
        analyzer = PRAnalyzer()
        review = analyzer.analyze(code_diff)
        print(json.dumps(review, indent=2))

    # Post a PR comment (test mode posts a simple message)
    repo_owner = latest.get("repo_owner")
    repo_name = latest.get("repo_name")
    pr_number = latest.get("pr_number")
    github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

    if repo_owner and repo_name and pr_number and github_token:
        def _format_comment(r: dict | None) -> str:
            if test_only or not r:
                return "Test comment from PRManager: integration check ✅"
            if "error" in r:
                return f"PR Review failed: {r.get('error', 'Unknown error')}"
            overall = r.get("overall_assessment", "No assessment produced.")
            approve = r.get("approve", False)
            concerns = r.get("concerns", [])
            lines = [
                "Automated PR Review (NVIDIA RAG)",
                f"Overall: {overall}",
                f"Decision: {'Approve' if approve else 'Request changes'}",
                f"Concerns: {len(concerns)}",
            ]
            for idx, c in enumerate(concerns[:3], start=1):
                fp = c.get("file_path", "unknown")
                sev = c.get("severity", "-")
                typ = c.get("type", "-")
                desc = c.get("description", "")
                lines.append(f"{idx}. [{sev}/{typ}] {fp} - {desc}")
            return "\n".join(lines)

        comment_body = _format_comment(review)
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{int(pr_number)}/comments"
        try:
            # Preferred scheme for GitHub REST v3 with classic PATs
            headers_token = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            resp = requests.post(api_url, headers=headers_token, json={"body": comment_body}, timeout=15)
            if resp.status_code == 401:
                # Fallback for fine-grained tokens that expect Bearer
                headers_bearer = {
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
                resp = requests.post(api_url, headers=headers_bearer, json={"body": comment_body}, timeout=15)

            if resp.status_code == 201:
                print("Posted PR review comment successfully.")
            else:
                print(f"Failed to post PR comment: {resp.status_code} - {resp.text}")
        except Exception as exc:
            print(f"Error posting PR comment: {exc}")
    else:
        print("Skipping PR comment: missing repo details or GITHUB_TOKEN.")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)