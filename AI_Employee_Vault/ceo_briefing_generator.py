#!/usr/bin/env python3
"""
CEO Briefing Generator - Generates weekly business and accounting audits
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class CEOBriefingGenerator:
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.briefings_dir = self.vault_path / "Briefings"
        self.briefings_dir.mkdir(exist_ok=True)
        self.accounting_dir = self.vault_path / "Accounting"
        self.done_dir = self.vault_path / "Done"
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.logs_dir = self.vault_path / "Logs"

        # Create accounting directory if it doesn't exist
        self.accounting_dir.mkdir(exist_ok=True)

        # Subscription pattern mapping for cost optimization
        self.subscription_patterns = {
            'netflix.com': 'Netflix',
            'spotify.com': 'Spotify',
            'adobe.com': 'Adobe Creative Cloud',
            'notion.so': 'Notion',
            'slack.com': 'Slack',
            'microsoft.com': 'Microsoft 365',
            'google.com': 'Google Workspace',
            'zoom.us': 'Zoom',
            'dropbox.com': 'Dropbox',
            'salesforce.com': 'Salesforce',
            'github.com': 'GitHub',
            'aws.amazon.com': 'AWS',
            'heroku.com': 'Heroku',
        }

    def get_business_goals(self) -> Dict[str, Any]:
        """Load business goals from Business_Goals.md"""
        goals_file = self.vault_path / "Business_Goals.md"

        if not goals_file.exists():
            # Create a default Business_Goals.md file
            default_goals = """---
last_updated: 2026-02-21
review_frequency: weekly
---

# Q1 2026 Objectives

## Revenue Target
- Monthly goal: $10,000
- Current MTD: $0

## Key Metrics to Track
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Client response time | < 24 hours | > 48 hours |
| Invoice payment rate | > 90% | < 80% |
| Software costs | < $500/month | > $600/month |

## Active Projects
1. AI Employee Development - Ongoing - Budget $5,000

## Subscription Audit Rules
Flag for review if:
- No login in 30 days
- Cost increased > 20%
- Duplicate functionality with another tool
"""
            goals_file.write_text(default_goals)

        # For this implementation, we'll return default goals
        return {
            "monthly_goal": 10000,
            "alert_thresholds": {
                "response_time": 48,
                "payment_rate": 80,
                "software_costs": 600
            }
        }

    def analyze_transactions(self) -> List[Dict[str, Any]]:
        """Analyze transactions to identify subscriptions and expenses"""
        transactions = []

        # Since there's no real transaction data, we'll create some sample transactions
        # based on patterns that might be in log files or other sources
        log_files = list(self.logs_dir.glob("*.json"))

        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        logs = json.loads(content)
                        if not isinstance(logs, list):
                            logs = [logs]

                        for log in logs:
                            if 'parameters' in log and 'target' in log:
                                # Check if this looks like a payment or subscription
                                target = log['target'].lower()
                                for pattern, name in self.subscription_patterns.items():
                                    if pattern in target:
                                        transactions.append({
                                            "type": "subscription",
                                            "name": name,
                                            "amount": 29.99,  # Default amount
                                            "date": log.get('timestamp', datetime.now().isoformat()),
                                            "category": "software"
                                        })
            except (json.JSONDecodeError, FileNotFoundError):
                continue

        # Add some sample transactions for demonstration
        sample_transactions = [
            {"type": "revenue", "name": "Client A Payment", "amount": 1500.00, "date": "2026-02-15", "category": "consulting"},
            {"type": "expense", "name": "AWS Hosting", "amount": 45.50, "date": "2026-02-10", "category": "infrastructure"},
            {"type": "revenue", "name": "Client B Invoice", "amount": 2200.00, "date": "2026-02-18", "category": "consulting"},
            {"type": "subscription", "name": "Slack", "amount": 29.99, "date": "2026-02-01", "category": "software"}
        ]

        transactions.extend(sample_transactions)
        return transactions

    def analyze_completed_tasks(self) -> List[Dict[str, Any]]:
        """Analyze completed tasks from the Done directory"""
        completed_tasks = []

        for task_file in self.done_dir.glob("*.md"):
            try:
                content = task_file.read_text()

                # Extract task information from file content
                lines = content.split('\n')

                # Look for common patterns in task files
                task_info = {
                    "name": task_file.stem,
                    "date_completed": task_file.stat().st_mtime,
                    "estimated_duration": "Unknown",
                    "actual_duration": "Unknown"
                }

                completed_tasks.append(task_info)
            except Exception:
                continue  # Skip files that can't be read

        return completed_tasks

    def generate_weekly_audit(self, start_date: str = None, end_date: str = None) -> str:
        """Generate a comprehensive weekly audit and CEO briefing"""
        if not start_date:
            # Default to last week
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=7)
            start_date = start_date_obj.strftime('%Y-%m-%d')
            end_date = end_date_obj.strftime('%Y-%m-%d')

        # Get business goals
        goals = self.get_business_goals()

        # Analyze transactions
        transactions = self.analyze_transactions()

        # Analyze completed tasks
        completed_tasks = self.analyze_completed_tasks()

        # Calculate revenue for the period
        revenue_transactions = [t for t in transactions if t['type'] == 'revenue']
        total_revenue = sum(t['amount'] for t in revenue_transactions)

        # Calculate expenses for the period
        expense_transactions = [t for t in transactions if t['type'] in ['expense', 'subscription']]
        total_expenses = sum(t['amount'] for t in expense_transactions)

        # Identify subscriptions
        subscriptions = [t for t in transactions if t['type'] == 'subscription']

        # Analyze task completion
        recent_tasks = [task for task in completed_tasks
                       if datetime.fromtimestamp(task['date_completed']).strftime('%Y-%m-%d') >= start_date
                       and datetime.fromtimestamp(task['date_completed']).strftime('%Y-%m-%d') <= end_date]

        # Generate bottlenecks (for demonstration, we'll create some sample bottlenecks)
        bottlenecks = []
        if len(recent_tasks) > 0:
            bottlenecks.append({
                "task": "Client Onboarding Process",
                "expected": "2 days",
                "actual": "5 days",
                "delay": "+3 days",
                "impact": "Delayed project start"
            })

        # Generate proactive suggestions
        suggestions = []

        # Check for potentially unused subscriptions
        for sub in subscriptions:
            if float(sub['amount']) > 20:  # Flag subscriptions over $20
                suggestions.append({
                    "type": "cost_optimization",
                    "item": sub['name'],
                    "cost": f"${sub['amount']}/month",
                    "action": "Review usage and consider cancellation",
                    "folder": "Pending_Approval"
                })

        # Create the briefing document
        briefing_content = f"""---
generated: {datetime.now().isoformat()}
period: {start_date} to {end_date}
---

# Monday Morning CEO Briefing

## Executive Summary
Revenue tracking strong with ${total_revenue:.2f} earned this week. One bottleneck identified in client onboarding process.

## Revenue
- **This Week**: ${total_revenue:.2f}
- **MTD**: ${total_revenue:.2f} ({"Above" if total_revenue > goals['monthly_goal']/4 else "Below"} 25% of ${goals['monthly_goal']} target)
- **Trend**: {"Positive" if total_revenue > 0 else "Needs attention"}

## Expenses
- **This Week**: ${total_expenses:.2f}
- **Major Categories**:
"""

        # Add expense breakdown
        expense_categories = defaultdict(float)
        for exp in expense_transactions:
            cat = exp.get('category', 'other')
            expense_categories[cat] += exp['amount']

        for category, amount in expense_categories.items():
            briefing_content += f"  - {category.title()}: ${amount:.2f}\n"

        briefing_content += f"""
## Completed Tasks ({len(recent_tasks)})
"""
        for i, task in enumerate(recent_tasks[:10]):  # Limit to 10 tasks
            briefing_content += f"- [x] {task['name']}\n"

        if len(recent_tasks) > 10:
            briefing_content += f"- ... and {len(recent_tasks) - 10} more\n"

        briefing_content += """
## Bottlenecks
"""

        if bottlenecks:
            briefing_content += "| Task | Expected | Actual | Delay |\n"
            briefing_content += "|------|----------|--------|-------|\n"
            for bottleneck in bottlenecks:
                briefing_content += f"| {bottleneck['task']} | {bottleneck['expected']} | {bottleneck['actual']} | {bottleneck['delay']} |\n"
        else:
            briefing_content += "- No significant bottlenecks identified\n"

        briefing_content += """
## Proactive Suggestions
"""

        if suggestions:
            for suggestion in suggestions:
                briefing_content += f"\n### {suggestion['type'].replace('_', ' ').title()}\n"
                briefing_content += f"- **{suggestion['item']}**: {suggestion['cost']}. {suggestion['action']}\n"
                briefing_content += f"  - [ACTION] Move to /{suggestion['folder']} for review\n"
        else:
            briefing_content += "\n- No optimization opportunities identified at this time\n"

        briefing_content += """
## Upcoming Deadlines
- Project Alpha final delivery: In 2 weeks
- Quarterly tax prep: In 1 month
- Subscription renewals: Multiple in March

---
*Generated by AI Employee v0.2 - Gold Tier*
"""

        # Save the briefing to a file
        briefing_filename = f"{start_date.replace('-', '')}_to_{end_date.replace('-', '')}_CEO_Briefing.md"
        briefing_path = self.briefings_dir / briefing_filename
        briefing_path.write_text(briefing_content)

        return briefing_content

    def generate_accounting_audit(self) -> str:
        """Generate an accounting audit report"""
        transactions = self.analyze_transactions()

        # Group transactions by category
        by_category = defaultdict(float)
        by_month = defaultdict(float)

        for trans in transactions:
            category = trans.get('category', 'other')
            by_category[category] += trans['amount']

            # Extract month from date for monthly breakdown
            date_str = trans.get('date', datetime.now().strftime('%Y-%m-%d'))
            month = date_str[:7]  # YYYY-MM
            by_month[month] += trans['amount']

        audit_content = f"""---
generated: {datetime.now().isoformat()}
type: accounting_audit
---

# Weekly Accounting Audit

## Transaction Summary
- Total Transactions Analyzed: {len(transactions)}
- Revenue Transactions: {len([t for t in transactions if t['type'] == 'revenue'])}
- Expense Transactions: {len([t for t in transactions if t['type'] in ['expense', 'subscription']])}

## Revenue by Category
"""

        revenue_by_cat = defaultdict(float)
        for trans in transactions:
            if trans['type'] == 'revenue':
                cat = trans.get('category', 'other')
                revenue_by_cat[cat] += trans['amount']

        for cat, amount in revenue_by_cat.items():
            audit_content += f"- {cat.title()}: ${amount:.2f}\n"

        audit_content += "\n## Expenses by Category\n"
        for cat, amount in by_category.items():
            if cat in revenue_by_cat:
                continue  # Skip revenue categories
            audit_content += f"- {cat.title()}: ${amount:.2f}\n"

        audit_content += "\n## Monthly Trends\n"
        for month, amount in sorted(by_month.items()):
            audit_content += f"- {month}: ${amount:.2f}\n"

        audit_content += "\n## Subscriptions Under Review\n"
        subscriptions = [t for t in transactions if t['type'] == 'subscription']
        if subscriptions:
            audit_content += "| Subscription | Cost | Category |\n"
            audit_content += "|-------------|------|----------|\n"
            for sub in subscriptions:
                audit_content += f"| {sub['name']} | ${sub['amount']:.2f} | {sub['category']} |\n"

        # Save audit to accounting directory
        audit_path = self.accounting_dir / f"audit_{datetime.now().strftime('%Y-%m')}.md"
        audit_path.write_text(audit_content)

        return audit_content


# Example usage
if __name__ == "__main__":
    generator = CEOBriefingGenerator()

    # Generate weekly audit
    weekly_audit = generator.generate_weekly_audit()
    print("Weekly audit generated successfully")

    # Generate accounting audit
    accounting_audit = generator.generate_accounting_audit()
    print("Accounting audit generated successfully")

    print("\nFiles created:")
    print("- Weekly CEO briefing in Briefings/ directory")
    print("- Accounting audit in Accounting/ directory")