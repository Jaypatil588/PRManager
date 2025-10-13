import requests
import json

# Test posting comments to GitHub using Bearer token
pat = "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"
headers = {
    "Authorization": f"Bearer {pat}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json"
}

# Use actual repo details from your webhook data
owner = "Jaypatil588"
repo_name = "PRManager"
pull_number = 5  # PR #5 from your webhook data

print(f"Testing comments for {owner}/{repo_name}#{pull_number}")

# Test 1: Regular comment (goes to issues endpoint)
print("\n=== Testing Regular Comment ===")
regular_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{pull_number}/comments"
regular_data = {"body": "🧪 Test regular comment from PRManager using Bearer token"}

try:
    response = requests.post(regular_url, headers=headers, json=regular_data)
    if response.status_code == 201:
        print(f"✅ Regular comment posted successfully!")
        comment_data = response.json()
        print(f"Comment URL: {comment_data.get('html_url', 'N/A')}")
    else:
        print(f"❌ Regular comment failed: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Get PR details first, then post inline comment
print("\n=== Testing Inline Review Comment ===")
try:
    # First get PR details to find commit SHA
    pr_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pull_number}"
    pr_response = requests.get(pr_url, headers=headers)
    
    if pr_response.status_code == 200:
        pr_data = pr_response.json()
        commit_sha = pr_data.get("head", {}).get("sha")
        print(f"✅ Found commit SHA: {commit_sha[:8]}...")
        
        # Post inline review comment
        inline_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pull_number}/comments"
        inline_data = {
            "body": "🔍 Test inline review comment using Bearer token",
            "commit_id": commit_sha,
            "path": "app.py",  # One of the files in the PR
            "position": 1
        }
        
        response = requests.post(inline_url, headers=headers, json=inline_data)
        if response.status_code == 201:
            print(f"✅ Inline comment posted successfully!")
            comment_data = response.json()
            print(f"Comment URL: {comment_data.get('html_url', 'N/A')}")
        else:
            print(f"❌ Inline comment failed: {response.status_code}")
            print(f"Response: {response.text}")
    else:
        print(f"❌ Failed to get PR details: {pr_response.status_code}")
        print(f"Response: {pr_response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== Test Complete ===")