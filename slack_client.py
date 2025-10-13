import os
import requests
from typing import Optional

class SlackClient:
    
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("SLACK_WEBHOOK_URL not found in environment variables")
    
    def send_pr_review(self, review_data: dict, pr_info: Optional[dict] = None) -> bool:
        try:
            message = self._format_message(review_data, pr_info)
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Slack notification sent successfully")
                return True
            else:
                print(f"❌ Slack notification failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Slack notification: {e}")
            return False
    
    def _format_message(self, review_data: dict, pr_info: Optional[dict] = None) -> dict:
        
        if "error" in review_data:
            return {
                "text": "PR Review Failed",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ PR Review Failed"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Error:* {review_data.get('error', 'Unknown error')}"
                        }
                    }
                ]
            }
        
        overall = review_data.get("overall_assessment", "No assessment provided")
        approve = review_data.get("approve", False)
        concerns = review_data.get("concerns", [])
        
        pr_title = "New Pull Request Analyzed"
        if pr_info:
            repo_owner = pr_info.get("repo_owner")
            repo_name = pr_info.get("repo_name")
            pr_number = pr_info.get("pr_number")
            if repo_owner and repo_name and pr_number:
                pr_title = f"PR #{pr_number} - {repo_owner}/{repo_name}"
        
        status_emoji = "✅" if approve else "⚠️"
        decision = "Approved" if approve else "Changes Requested"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{status_emoji} {pr_title}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Decision:*\n{decision}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Concerns Found:*\n{len(concerns)}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Overall Assessment:*\n{overall}"
                }
            },
            {"type": "divider"}
        ]
        
        if concerns:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔍 Detailed Concerns:*"
                }
            })
            
            for idx, concern in enumerate(concerns, 1):
                severity = concern.get("severity", "UNKNOWN")
                concern_type = concern.get("type", "Unknown")
                file_path = concern.get("file_path", "Unknown file")
                line_start = concern.get("line_number_start", "?")
                line_end = concern.get("line_number_end", "?")
                description = concern.get("description", "No description")
                suggestion = concern.get("suggestion", "No suggestion provided")
                
                severity_emoji = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🟢"
                }.get(severity, "⚪")
                
                concern_text = (
                    f"*{idx}. {severity_emoji} {severity} - {concern_type}*\n"
                    f"📁 `{file_path}` (Lines {line_start}-{line_end})\n"
                    f"*Issue:* {description}\n"
                    f"*Suggestion:* {suggestion}"
                )
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": concern_text
                    }
                })
                
                if idx < len(concerns):
                    blocks.append({"type": "divider"})
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "✨ *No concerns found - code looks good!*"
                }
            })
        
        return {
            "text": f"PR Review: {decision}",
            "blocks": blocks
        }

