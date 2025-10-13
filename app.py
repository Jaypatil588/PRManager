import requests
import json
import os
from dotenv import load_dotenv


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
    if not test_only and code_diff:
        print("🤖 Running AI analysis...")
        try:
            analyzer = PRAnalyzer()
            review = analyzer.analyze(code_diff)
            print("✅ Analysis completed")
            print(json.dumps(review, indent=2))
        except Exception as exc:
            print(f"❌ Analysis failed: {exc}")
            review = {"error": f"Analysis failed: {exc}"}

    # Step 5: Post comments using GitHubClient
    github_token = os.getenv("GITHUB_TOKEN")
    
    if github_token and repo_owner and repo_name and pr_number:
        print("💬 Posting comments to GitHub...")
        
        try:
            # Initialize GitHub client with Bearer token
            client = GitHubClient(github_token, repo_owner, repo_name, use_bearer=True)
            
            # Format comment based on analysis or test mode
            if test_only or not review:
                comment_body = "🧪 Test comment from PRManager - integration check ✅"
            elif "error" in review:
                comment_body = f"❌ PR Review failed: {review.get('error', 'Unknown error')}"
            else:
                # Format detailed review comment
                overall = review.get("overall_assessment", "No assessment produced.")
                approve = review.get("approve", False)
                concerns = review.get("concerns", [])
                
                lines = [
                    "## 🤖 Automated PR Review (NVIDIA RAG)",
                    "",
                    f"**Overall Assessment:** {overall}",
                    f"**Decision:** {'✅ Approve' if approve else '❌ Request changes'}",
                    f"**Concerns Found:** {len(concerns)}",
                    ""
                ]
                
                if concerns:
                    lines.append("### Issues Found:")
                    for idx, c in enumerate(concerns[:5], start=1):
                        fp = c.get("file_path", "unknown")
                        sev = c.get("severity", "-")
                        typ = c.get("type", "-")
                        desc = c.get("description", "")
                        sugg = c.get("suggestion", "")
                        lines.extend([
                            f"**{idx}. [{sev}/{typ}] {fp}**",
                            f"   - {desc}",
                            f"   - 💡 Suggestion: {sugg}",
                            ""
                        ])
                    
                    if len(concerns) > 5:
                        lines.append(f"...and {len(concerns) - 5} more concerns.")
                
                comment_body = "\n".join(lines)
            
            # Post regular comment
            print("📝 Posting regular comment...")
            comment_result = client.post_comment(int(pr_number), comment_body)
            print(f"✅ Regular comment posted: {comment_result.get('html_url', 'N/A')}")
            
            # Post inline review comment on first file if analysis found issues
            if not test_only and review and not review.get("error") and review.get("concerns"):
                print("🔍 Posting inline review comment...")
                try:
                    first_concern = review["concerns"][0]
                    file_path = first_concern.get("file_path", "app.py")
                    line_number = first_concern.get("line_number_start", 1)
                    
                    inline_body = f"🤖 **{first_concern.get('severity', 'MEDIUM')}** - {first_concern.get('description', 'Issue found')}"
                    
                    inline_result = client.post_review_comment_with_auto_commit(
                        int(pr_number), 
                        inline_body, 
                        file_path, 
                        line_number
                    )
                    print(f"✅ Inline comment posted: {inline_result.get('html_url', 'N/A')}")
                except Exception as exc:
                    print(f"⚠️  Inline comment failed: {exc}")
            
            print("🎉 Comment posting completed successfully!")
            
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


if __name__ == "__main__":
    main()


