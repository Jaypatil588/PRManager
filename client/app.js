const { useState, useEffect } = React;

// Login Page Component
function LoginPage({ onLogin }) {
    const handleGitHubLogin = () => {
        window.location.href = '/login/github';
    };

    return (
        <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: 0,
            padding: 0
        }}>
            <div style={{
                background: 'white',
                padding: '3rem',
                borderRadius: '12px',
                boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
                textAlign: 'center',
                maxWidth: '400px',
                width: '90%'
            }}>
                <div style={{
                    fontSize: '2.5rem',
                    fontWeight: 'bold',
                    color: '#333',
                    marginBottom: '0.5rem'
                }}>
                    🚀 PR Manager
                </div>
                <div style={{
                    color: '#666',
                    marginBottom: '2rem',
                    fontSize: '1.1rem'
                }}>
                    Automated Pull Request Analysis
                </div>
                <button
                    onClick={handleGitHubLogin}
                    style={{
                        background: '#24292e',
                        color: 'white',
                        border: 'none',
                        padding: '1rem 2rem',
                        borderRadius: '8px',
                        fontSize: '1.1rem',
                        fontWeight: '600',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        width: '100%',
                        justifyContent: 'center',
                        transition: 'all 0.3s ease'
                    }}
                    onMouseOver={(e) => {
                        e.target.style.background = '#1a1e22';
                        e.target.style.transform = 'translateY(-2px)';
                        e.target.style.boxShadow = '0 8px 20px rgba(0,0,0,0.2)';
                    }}
                    onMouseOut={(e) => {
                        e.target.style.background = '#24292e';
                        e.target.style.transform = 'translateY(0)';
                        e.target.style.boxShadow = 'none';
                    }}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                    Continue with GitHub
                </button>
            </div>
        </div>
    );
}

// Dashboard Component
function Dashboard({ user, onLogout }) {
    const handleLogout = () => {
        window.location.href = '/logout';
    };

    return (
        <div style={{ background: '#f8f9fa', minHeight: '100vh' }}>
            {/* Header */}
            <div style={{
                background: 'white',
                padding: '1rem 2rem',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div style={{
                    fontSize: '1.5rem',
                    fontWeight: 'bold',
                    color: '#333'
                }}>
                    🚀 PR Manager
                </div>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem'
                }}>
                    <img 
                        src={user.avatar_url} 
                        alt="Avatar" 
                        style={{
                            width: '40px',
                            height: '40px',
                            borderRadius: '50%'
                        }}
                    />
                    <span>{user.name || user.login}</span>
                    <button
                        onClick={handleLogout}
                        style={{
                            background: '#dc3545',
                            color: 'white',
                            border: 'none',
                            padding: '0.5rem 1rem',
                            borderRadius: '6px',
                            cursor: 'pointer'
                        }}
                    >
                        Logout
                    </button>
                </div>
            </div>
            
            {/* Main Content */}
            <div style={{
                maxWidth: '1200px',
                margin: '2rem auto',
                padding: '0 2rem'
            }}>
                {/* Welcome Card */}
                <div style={{
                    background: 'white',
                    padding: '2rem',
                    borderRadius: '12px',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                    marginBottom: '2rem'
                }}>
                    <h1 style={{
                        fontSize: '2rem',
                        color: '#333',
                        marginBottom: '0.5rem',
                        margin: 0
                    }}>
                        Welcome to PR Manager!
                    </h1>
                    <p style={{
                        color: '#666',
                        fontSize: '1.1rem',
                        margin: '0.5rem 0 0 0'
                    }}>
                        You're successfully logged in with GitHub. Start analyzing your pull requests with AI-powered insights.
                    </p>
                </div>
                
                {/* Features Grid */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '2rem',
                    marginTop: '2rem'
                }}>
                    <div style={{
                        background: 'white',
                        padding: '2rem',
                        borderRadius: '12px',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
                        <h3 style={{
                            fontSize: '1.5rem',
                            color: '#333',
                            marginBottom: '1rem',
                            margin: '0 0 1rem 0'
                        }}>
                            AI Code Analysis
                        </h3>
                        <p style={{
                            color: '#666',
                            lineHeight: '1.6',
                            margin: 0
                        }}>
                            Get intelligent code reviews and suggestions powered by advanced AI models.
                        </p>
                    </div>
                    
                    <div style={{
                        background: 'white',
                        padding: '2rem',
                        borderRadius: '12px',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
                        <h3 style={{
                            fontSize: '1.5rem',
                            color: '#333',
                            marginBottom: '1rem',
                            margin: '0 0 1rem 0'
                        }}>
                            PR Analytics
                        </h3>
                        <p style={{
                            color: '#666',
                            lineHeight: '1.6',
                            margin: 0
                        }}>
                            Track pull request metrics and identify patterns in your development workflow.
                        </p>
                    </div>
                    
                    <div style={{
                        background: 'white',
                        padding: '2rem',
                        borderRadius: '12px',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚡</div>
                        <h3 style={{
                            fontSize: '1.5rem',
                            color: '#333',
                            marginBottom: '1rem',
                            margin: '0 0 1rem 0'
                        }}>
                            Automated Reviews
                        </h3>
                        <p style={{
                            color: '#666',
                            lineHeight: '1.6',
                            margin: 0
                        }}>
                            Automatically review pull requests and provide detailed feedback and recommendations.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Main App Component
function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is logged in
        fetch('/api/user', {
            credentials: 'same-origin'
        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Not authenticated');
            })
            .then(userData => {
                setUser(userData);
            })
            .catch(() => {
                setUser(null);
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div style={{
                height: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#f8f9fa'
            }}>
                <div style={{
                    fontSize: '1.2rem',
                    color: '#666'
                }}>
                    Loading...
                </div>
            </div>
        );
    }

    if (user) {
        return <Dashboard user={user} onLogout={() => setUser(null)} />;
    }

    return <LoginPage onLogin={setUser} />;
}

// Render the app
ReactDOM.render(<App />, document.getElementById('root'));
