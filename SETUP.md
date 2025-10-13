# PR Manager - GitHub SSO Setup

## Environment Variables Required

Create a `.env` file in the project root with the following variables:

```env
# GitHub OAuth App Configuration
# Get these from: https://github.com/settings/applications/new
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production

# GitHub Token for PR Analysis (existing)
GITHUB_TOKEN=your_github_token_here
GH_TOKEN=your_github_token_here

# Optional: Test mode for PR comments
TEST_COMMENT=0
```

## GitHub OAuth App Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/applications/new)
2. Create a new OAuth App with these settings:
   - **Application name**: PR Manager
   - **Homepage URL**: `http://localhost:5000`
   - **Authorization callback URL**: `http://localhost:5000/callback/github`
3. Copy the Client ID and Client Secret to your `.env` file

## Installation

1. Install dependencies:
```bash
pip install -r requiremets.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser to `http://localhost:5000`

## Features

- **GitHub SSO Login**: Secure authentication with GitHub OAuth
- **User Dashboard**: Welcome page after successful login
- **Session Management**: Secure user sessions with logout functionality
- **API Endpoints**: RESTful API for user information
- **PR Analysis**: Original PR analysis functionality preserved

## API Endpoints

- `GET /` - Login page
- `GET /login/github` - Initiate GitHub OAuth
- `GET /callback/github` - OAuth callback handler
- `GET /dashboard` - User dashboard (requires authentication)
- `GET /logout` - Logout and clear session
- `GET /api/user` - Get current user info (JSON API)
