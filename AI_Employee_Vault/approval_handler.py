#!/usr/bin/env python3
"""
Approval Handler - Manages human-in-the-loop approval workflow
"""
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
import json
import os
from typing import Dict, Any, List


class ApprovalHandler:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.dashboard_path = self.vault_path / 'Dashboard.md'

        # Create directories if they don't exist
        for dir_path in [self.pending_approval, self.approved, self.rejected, self.done]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # File handler for logging
        handler = logging.FileHandler(self.vault_path / 'approval_handler.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def create_approval_request(self, action_type: str, details: Dict[str, Any], reason: str = "") -> Path:
        """Create an approval request file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        approval_id = f"APPROVAL_{action_type.upper()}_{timestamp}"
        approval_path = self.pending_approval / f"{approval_id}.md"

        approval_content = f"""---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=7)).isoformat()}
status: pending
---

## Action Details
{json.dumps(details, indent=2)}

## Reason for Approval
{reason}

## To Approve
Move this file to /Approved folder or add [APPROVED] tag.

## To Reject
Move this file to /Rejected folder or add [REJECTED] tag.

## Next Steps
After approval, the action will be executed automatically.
"""

        approval_path.write_text(approval_content)
        self.logger.info(f"Created approval request: {approval_path.name}")
        return approval_path

    def check_approvals(self) -> List[Dict[str, Any]]:
        """Check for approvals that have been processed manually"""
        processed_approvals = []

        # Check Approved directory
        for approved_file in self.approved.glob("*.md"):
            approval_data = {
                'file_path': approved_file,
                'action': 'approved',
                'timestamp': datetime.fromtimestamp(approved_file.stat().st_mtime)
            }
            processed_approvals.append(approval_data)

        # Check Rejected directory
        for rejected_file in self.rejected.glob("*.md"):
            approval_data = {
                'file_path': rejected_file,
                'action': 'rejected',
                'timestamp': datetime.fromtimestamp(rejected_file.stat().st_mtime)
            }
            processed_approvals.append(approval_data)

        return processed_approvals

    def process_approvals(self):
        """Process approvals and take appropriate actions"""
        processed_approvals = self.check_approvals()

        for approval in processed_approvals:
            file_path = approval['file_path']
            action = approval['action']

            self.logger.info(f"Processing {action} approval: {file_path.name}")

            if action == 'approved':
                # Execute the approved action
                self.execute_approved_action(file_path)
                # Move to Done
                new_path = self.done / file_path.name
                file_path.rename(new_path)

            elif action == 'rejected':
                # Log the rejection and move to Done
                self.logger.info(f"Approval rejected: {file_path.name}")
                new_path = self.done / file_path.name
                file_path.rename(new_path)

    def execute_approved_action(self, approval_file: Path):
        """Execute an action that has been approved"""
        # Read the approval file to get action details
        content = approval_file.read_text()

        # In a real implementation, this would parse the content and execute the appropriate action
        # For now, we'll just log that an action was approved
        self.logger.info(f"Executing approved action from: {approval_file.name}")

        # Example: if it's an email action, execute it
        if 'email' in approval_file.name.lower():
            self.logger.info("Email action approved - would send email")

        # Example: if it's a payment action, execute it
        if 'payment' in approval_file.name.lower():
            self.logger.info("Payment action approved - would process payment")

        # Example: if it's a social media post, execute it
        if 'linkedin' in approval_file.name.lower() or 'social' in approval_file.name.lower():
            self.logger.info("Social media post approved - would publish")

    def check_pending_approvals(self) -> int:
        """Check number of pending approvals and update dashboard"""
        pending_files = list(self.pending_approval.glob("*.md"))
        num_pending = len(pending_files)

        # Update dashboard with pending approvals
        self.update_dashboard(num_pending)

        self.logger.info(f"Currently {num_pending} pending approvals")
        return num_pending

    def update_dashboard(self, num_pending: int):
        """Update dashboard with approval information"""
        if self.dashboard_path.exists():
            dashboard_content = self.dashboard_path.read_text()
        else:
            dashboard_content = "# Dashboard\n\n"

        # Append approval information
        approval_info = f"\n## Approval Queue\n"
        approval_info += f"- Pending approvals: {num_pending}\n"
        approval_info += f"- Last updated: {datetime.now().isoformat()}\n"

        # Find the approval queue section and replace it, or add it if it doesn't exist
        lines = dashboard_content.split('\n')
        new_lines = []
        approval_section_found = False

        for line in lines:
            if line.startswith('## Approval Queue'):
                approval_section_found = True
                continue
            if approval_section_found and line.startswith('## ') and not line.startswith('## Approval Queue'):
                # End of approval section, add the new info here
                new_lines.append(approval_info)
                new_lines.append(line)
                approval_section_found = False
            else:
                if not approval_section_found:
                    new_lines.append(line)

        # If approval section wasn't found, just append the info
        if num_pending > 0 or not approval_section_found:
            if approval_section_found:
                # If we were in the approval section, add the new content
                new_dashboard = '\n'.join(new_lines)
            else:
                new_dashboard = '\n'.join(new_lines) + approval_info
        else:
            new_dashboard = '\n'.join(new_lines)

        self.dashboard_path.write_text(new_dashboard)

    def run(self):
        """Main approval handler loop"""
        self.logger.info("Starting Approval Handler...")

        while True:
            try:
                self.logger.info("Checking for pending approvals...")

                # Check number of pending approvals
                num_pending = self.check_pending_approvals()

                # Process any processed approvals
                self.process_approvals()

                # Wait for a while before next check
                time.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in approval handler: {e}")
                time.sleep(300)  # Wait 5 minutes if there's an error


if __name__ == "__main__":
    # Initialize with vault path
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    handler = ApprovalHandler(vault_path)

    print("Starting Approval Handler...")
    handler.run()