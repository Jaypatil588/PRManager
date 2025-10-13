import requests
import os
import json

def analyze_commits(webhook_data):
    """
    Analyze commits from webhook data and post comments to GitHub PR
    
    Args:
        webhook_data: List of webhook data containing commits, PR info, etc.
    """
    try:
        # The webhook data is a list, get the first item
        data = webhook_data[0] if isinstance(webhook_data, list) else webhook_data
        
        # Extract commit and PR information
        commits = data.get("commits", [])
        pr_number = data.get("pr_number")
        pr_title = data.get("pr_title", "No title provided")
        repo_owner = data.get("repo_owner")
        repo_name = data.get("repo_name")
        
        if not commits:
            return "No commits found in webhook data"
        
        # Combine all commit messages and code changes
        commit_messages = []
        code_changes = []
        
        for commit in commits:
            commit_messages.append(commit.get("message", ""))
            code_changes.append(commit.get("code_changes", ""))
        
        combined_messages = "\n".join(commit_messages)
        combined_diff = "\n\n".join(code_changes)
        
        # Construct the GitHub PR comments URL
        comments_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
        
        # Create the prompt for LLM
        prompt = f"""Analyze this pull request and determine if the code changes match the PR title and commit messages.

PR Title: {pr_title}
Commit Messages: 
{combined_messages}

Code Changes:
{combined_diff}

Respond ONLY with a valid JSON object in this exact format:
{{
    "answer": "yes" or "no",
    "suggestion": "your suggestion text here"
}}"""
        
        # Send to LLM for analysis
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        api_key = os.getenv("NVIDIA_API_KEY")
        
        if not api_key:
            return "Error: NVIDIA_API_KEY environment variable not set"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "nvidia/llama-3.1-nemotron-70b-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1024
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"]
            
            try:
                analysis = json.loads(llm_response)
                suggestion = analysis.get("suggestion", "")
                
                # Post comment to GitHub PR
                github_token = os.getenv("GITHUB_TOKEN")
                
                if not github_token:
                    return "Error: GITHUB_TOKEN environment variable not set"
                
                comment_headers = {
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json"
                }
                
                comment_payload = {
                    "body": suggestion
                }
                
                comment_response = requests.post(comments_url, json=comment_payload, headers=comment_headers)
                
                if comment_response.status_code == 201:
                    print("Comment posted successfully")
                    return {"status": "success", "analysis": analysis, "comment_posted": True}
                else:
                    print(f"Failed to post comment: {comment_response.status_code} - {comment_response.text}")
                    return {"status": "partial_success", "analysis": analysis, "comment_posted": False, "error": comment_response.text}
                    
            except json.JSONDecodeError:
                return {"status": "success", "raw_response": llm_response}
        else:
            return f"Error calling LLM: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error processing webhook data: {str(e)}"


def send_prompt_to_llama():
    """
    Legacy function - reads from message.txt for backwards compatibility
    """
    with open("message.txt", "r") as f:
        data = json.load(f)
    
    pr_data = data[0]["pull_request"]
    pr_title = pr_data["title"]
    pr_body = pr_data["body"] if pr_data["body"] else "No description provided"
    diff_url = pr_data["diff_url"]
    comments_url = pr_data["comments_url"]
    
    diff_response = requests.get(diff_url)
    code_diff = diff_response.text if diff_response.status_code == 200 else "Unable to fetch diff"
    
    prompt = f"""Analyze this pull request and determine if the code changes match the PR message.

PR Title: {pr_title}
PR Description: {pr_body}

Code Diff:
{code_diff}

Respond ONLY with a valid JSON object in this exact format:
{{
    "answer": "yes" or "no",
    "suggestion": "your suggestion text here"
}}"""
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    api_key = os.getenv("NVIDIA_API_KEY")
    
    if not api_key:
        return "Error: NVIDIA_API_KEY environment variable not set"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "nvidia/llama-3.1-nemotron-70b-instruct",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 1024
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        llm_response = result["choices"][0]["message"]["content"]
        
        try:
            analysis = json.loads(llm_response)
            suggestion = analysis.get("suggestion", "")
            
            github_token = os.getenv("GITHUB_TOKEN")
            comment_headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json"
            }
            
            comment_payload = {
                "body": suggestion
            }
            
            comment_response = requests.post(comments_url, json=comment_payload, headers=comment_headers)
            
            if comment_response.status_code == 201:
                print("Comment posted successfully")
            else:
                print(f"Failed to post comment: {comment_response.status_code} - {comment_response.text}")
                
            return llm_response
        except json.JSONDecodeError:
            return llm_response
    else:
        return f"Error: {response.status_code} - {response.text}"


if __name__ == "__main__":
    result = send_prompt_to_llama()
    print(result)

