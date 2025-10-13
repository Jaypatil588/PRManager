import requests
import json
import os
from dotenv import load_dotenv
from slack_client import SlackClient


def main():
    # Ensure environment variables from .env are loaded before importing analyzer
    load_dotenv()
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
        review = analyzer.analyze(code_diff,"pr_review")
        print(json.dumps(review, indent=2))
        
        try:
            slack = SlackClient()
            pr_info = {
                "repo_owner": latest.get("repo_owner"),
                "repo_name": latest.get("repo_name"),
                "pr_number": latest.get("pr_number")
            }
            slack.send_pr_review(review, pr_info)
        except ValueError as e:
            print(f"Skipping Slack notification: {e}")
        except Exception as e:
            print(f"Error with Slack notification: {e}")


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


    #Check code vulneribilityc
    vulneribility = analyzer.analyze(code_diff, "vulneribility_check")
    print(json.dumps(vulneribility, indent=2))

if __name__ == "__main__":
    main()


