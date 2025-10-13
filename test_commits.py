#!/usr/bin/env python3
"""
Test script to verify the GitHub service commits functionality
"""

import os
from dotenv import load_dotenv
from github_service import GitHubService

# Load environment variables
load_dotenv()

def test_github_service():
    """Test the GitHub service with commits functionality"""
    
    # Check if we have a GitHub token
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ No GITHUB_TOKEN found in environment variables")
        print("Please set GITHUB_TOKEN in your .env file")
        return False
    
    print(f"✅ Found GitHub token: {token[:10]}...")
    
    # Initialize GitHub service
    github_service = GitHubService(token=token)
    
    # Test repository commits
    repo_owner = "Jaypatil588"
    repo_name = "PRManager"
    
    print(f"\n🔍 Testing commits for {repo_owner}/{repo_name}...")
    
    try:
        # Get repository commits
        commits = github_service.get_repository_commits(repo_owner, repo_name, per_page=10)
        
        if commits:
            print(f"✅ Successfully fetched {len(commits)} commits")
            
            # Show first few commits
            for i, commit in enumerate(commits[:3]):
                print(f"\n📝 Commit {i+1}:")
                print(f"   SHA: {commit['sha'][:7]}")
                print(f"   Message: {commit['commit']['message'].split('\\n')[0]}")
                print(f"   Author: {commit['commit']['author']['name']}")
            
            # Test commit analysis
            print(f"\n🔍 Analyzing commits...")
            analysis = github_service.analyze_commits(commits)
            print(f"✅ Analysis complete:")
            print(f"   Total commits: {analysis['total']}")
            print(f"   Good commits: {analysis['good']}")
            print(f"   Bad commits: {analysis['bad']}")
            print(f"   Suggestions: {len(analysis['suggestions'])}")
            
            return True
        else:
            print("❌ No commits found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing commits: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing GitHub Service Commits Functionality")
    print("=" * 50)
    
    success = test_github_service()
    
    if success:
        print("\n✅ All tests passed! GitHub service is working correctly.")
    else:
        print("\n❌ Tests failed. Please check your configuration.")
