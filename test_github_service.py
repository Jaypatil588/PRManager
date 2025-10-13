#!/usr/bin/env python3
"""
Test script to verify GitHub service functionality
"""
from github_service import github_service
import json

def test_github_service():
    """Test the GitHub service functions"""
    print("🔍 Testing GitHub Service...")
    
    # Test 1: Get user repositories
    print("\n1. Testing get_user_repositories()...")
    repos = github_service.get_user_repositories(per_page=5)
    if repos:
        print(f"✅ Found {len(repos)} repositories")
        for repo in repos[:3]:  # Show first 3
            print(f"   - {repo['full_name']}: {repo['description'] or 'No description'}")
    else:
        print("❌ No repositories found")
    
    # Test 2: Get PRs for a specific repository (if we have repos)
    if repos:
        test_repo = repos[0]
        repo_owner, repo_name = test_repo['full_name'].split('/', 1)
        
        print(f"\n2. Testing get_repository_pull_requests() for {test_repo['full_name']}...")
        prs = github_service.get_repository_pull_requests(repo_owner, repo_name, state='open', per_page=5)
        if prs:
            print(f"✅ Found {len(prs)} open PRs")
            for pr in prs[:2]:  # Show first 2
                print(f"   - PR #{pr['number']}: {pr['title']}")
        else:
            print("ℹ️  No open PRs found")
        
        # Test 3: Get commits for a PR (if we have PRs)
        if prs:
            test_pr = prs[0]
            print(f"\n3. Testing get_pull_request_commits() for PR #{test_pr['number']}...")
            commits = github_service.get_pull_request_commits(repo_owner, repo_name, test_pr['number'])
            if commits:
                print(f"✅ Found {len(commits)} commits")
                for commit in commits[:2]:  # Show first 2
                    message = commit['commit']['message'].split('\n')[0]
                    print(f"   - {commit['sha'][:7]}: {message}")
            else:
                print("ℹ️  No commits found")
            
            # Test 4: Comprehensive analysis
            print(f"\n4. Testing get_comprehensive_pr_analysis() for PR #{test_pr['number']}...")
            analysis = github_service.get_comprehensive_pr_analysis(repo_owner, repo_name, test_pr['number'])
            if analysis:
                print("✅ Comprehensive analysis completed")
                print(f"   - Total commits: {analysis['summary']['total_commits']}")
                print(f"   - Files changed: {analysis['summary']['files_changed']}")
                print(f"   - Comments: {analysis['summary']['total_comments']}")
                print(f"   - Reviews: {analysis['summary']['total_reviews']}")
                print(f"   - Vulnerabilities: {analysis['summary']['vulnerabilities_found']}")
                
                # Show commit analysis
                commit_analysis = analysis['commit_analysis']
                print(f"   - Good commits: {commit_analysis['good']}")
                print(f"   - Bad commits: {commit_analysis['bad']}")
                print(f"   - Suggestions: {len(commit_analysis['suggestions'])}")
            else:
                print("❌ Analysis failed")
    
    print("\n🎉 GitHub Service test completed!")

if __name__ == "__main__":
    test_github_service()
