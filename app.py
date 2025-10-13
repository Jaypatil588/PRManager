import requests
import json
import os
from dotenv import load_dotenv
from slack_client import SlackClient


def main():
    # Ensure environment variables from .env are loaded before importing analyzer
    load_dotenv()
    from pr_analyzer import PRAnalyzer
    from github_client import GitHubClient
    
    webhook_url = "https://flask-hello-world-eight-lac.vercel.app/webhookCommits"

    print("🚀 Starting PR Analysis and Comment Pipeline")
    
    # Step 1: Fetch webhook data
    try:
        print("📡 Fetching webhook data...")
        resp = requests.get(webhook_url, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
        print(f"✅ Webhook data fetched: {len(payload) if isinstance(payload, list) else 'N/A'} entries")
    except Exception as exc:
        print(f"❌ Failed to fetch webhook data: {exc}")
        return

    if not isinstance(payload, list) or not payload:
        print("❌ Webhook returned empty or invalid payload")
        return

    # Step 2: Extract PR data
    latest = payload[-1]
    repo_owner = latest.get("repo_owner")
    repo_name = latest.get("repo_name")
    pr_number = latest.get("pr_number")
    
    print(f"📋 Processing PR: {repo_owner}/{repo_name}#{pr_number}")
    
    # Step 3: Extract code diff
    code_diff = None
    commits = latest.get("commits")
    if isinstance(commits, list) and commits:
        code_diff = commits[-1].get("code_changes")
    if not code_diff:
        code_diff = latest.get("code_changes")

    test_only = os.getenv("TEST_COMMENT") == "1"
    if not code_diff and not test_only:
        print("❌ No code_changes diff found in payload")
        return

    # Step 4: Analyze code (if not test mode)
    review = None
    if not test_only:
        analyzer = PRAnalyzer()

        review = analyzer.analyze(code_diff, "pr_review")
        #pr = (json.dumps(review, indent=2))
        #print(pr)
        

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
            print(f"❌ Comment posting failed: {exc}")
    else:
        missing = []
        if not github_token:
            missing.append("GITHUB_TOKEN")
        if not repo_owner:
            missing.append("repo_owner")
        if not repo_name:
            missing.append("repo_name")
        if not pr_number:
            missing.append("pr_number")
        
        print(f"⏭️  Skipping comments: missing {', '.join(missing)}")
    
    print("✅ Pipeline completed!")

    #Check code vulneribilityc
    vulneribility = analyzer.analyze(code_diff, "vulneribility_check")
    #vul = (json.dumps(vulneribility, indent=2))
    #print(vul)

    postPR = "https://flask-hello-world-eight-lac.vercel.app/fetchPrReview"
    postVul = "https://flask-hello-world-eight-lac.vercel.app/fetchVulnerability"

    response = requests.post(postPR, json = review)
    response2 = requests.post(postVul, json = vulneribility)

    SlackClient().send_pr_review(review, latest)
    SlackClient().send_pr_review(vulneribility, latest)

if __name__ == "__main__":
    main()


