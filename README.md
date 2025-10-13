# PR Manager

Automated Pull Request Analysis with GitHub SSO Authentication

## Project Structure

```
PRManager/
├── main.py                # Main entry point (frontend + backend)
├── app.py                 # Backend API only
├── github_client.py       # GitHub API client
├── github_service.py      # GitHub service layer
├── pr_analyzer.py         # PR analysis logic
├── requiremets.txt        # Python dependencies
├── test_setup.py          # Setup verification script
├── SETUP.md               # Detailed setup instructions
├── faiss_index/           # Vector database files
├── client/                # Frontend files
│   ├── index.html         # React frontend HTML
│   ├── app.js             # React application
│   └── frontend.py        # Frontend routes and templates
└── README.md              # This file
```

## Quick Start

1. **Set up environment variables:**
   - Create a `.env` file in the root directory (see `SETUP.md` for details)
   - Set up GitHub OAuth app

2. **Install dependencies:**
   ```bash
   pip install -r requiremets.txt
   ```

3. **Test setup:**
   ```bash
   python test_setup.py
   ```

4. **Run the application:**
   
   **Option 1: Run everything together (recommended):**
   ```bash
   python main.py
   ```
   
   **Option 2: Run frontend and backend separately:**
   ```bash
   # Terminal 1 - Backend API
   python app.py
   
   # Terminal 2 - Frontend
   python client/frontend.py
   ```

5. **Open your browser:**
   - Go to `http://localhost:5002`
   - Click "Continue with GitHub" to authenticate
   - Access your dashboard after login

## Features

- 🔐 **GitHub SSO Login** - Secure OAuth 2.0 authentication
- 🎨 **Modern UI** - Beautiful React frontend with responsive design
- 📊 **User Dashboard** - Personalized welcome page with feature overview
- 🤖 **AI PR Analysis** - Automated pull request review and suggestions
- 🔧 **RESTful API** - Clean backend API for frontend integration

## Documentation

For detailed setup instructions, see `client/SETUP.md`

## Support

This is a hackathon project for automated PR management with AI-powered analysis.
