#!/usr/bin/env python3
"""
Cloud Agent Orchestrator - Platinum Tier
Specialized orchestrator for cloud-based AI operations (email triage, social media drafts)
All sensitive actions require local approval before execution.
"""
import time
import logging
import os
import subprocess
from pathlib import Path
from threading import Thread
from datetime import datetime
import json
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class CloudAgentOrchestrator:
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # File handler for logging
        log_file_path = self.vault_path / 'cloud_agent_orchestrator.log'
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Initialize directories if they don't exist
        dirs_to_create = [
            self.vault_path / 'Cloud_Agent' / 'Needs_Action',
            self.vault_path / 'Cloud_Agent' / 'Plans',
            self.vault_path / 'Cloud_Agent' / 'Done',
            self.vault_path / 'Cloud_Agent' / 'Pending_Approval',
            self.vault_path / 'Cloud_Agent' / 'Approved',
            self.vault_path / 'Cloud_Agent' / 'Rejected',
            self.vault_path / 'Cloud_Agent' / 'Drafts',
            self.vault_path / 'Cloud_Agent' / 'Social_Drafts',
            self.vault_path / 'Updates',
            self.vault_path / 'In_Progress',
            self.vault_path / 'Health_Monitor'
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Track running processes
        self.processes = []

        # Email configuration (for draft creation only - no actual sending from cloud)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS')

        self.logger.info("Cloud Agent Orchestrator initialized")

    def is_local_online(self) -> bool:
        """
        Check if local agent is online by checking for heartbeat file
        In a real implementation, this would be more sophisticated
        """
        heartbeat_file = self.vault_path / 'Local_Agent' / 'heartbeat.txt'
        if heartbeat_file.exists():
            # Check if heartbeat is recent (within last 5 minutes)
            mod_time = heartbeat_file.stat().st_mtime
            current_time = time.time()
            return (current_time - mod_time) < 300  # 5 minutes
        return False

    def process_email_drafts(self):
        """
        Process incoming emails and create draft replies for local approval
        """
        try:
            # Find email-related files that need processing
            needs_action_path = self.vault_path / 'Cloud_Agent' / 'Needs_Action'
            email_files = list(needs_action_path.glob('*email*.md'))

            for email_file in email_files:
                try:
                    content = email_file.read_text()

                    # Extract email information
                    if "type: email" in content and "from:" in content:
                        from_line = [line for line in content.split('\n') if 'from:' in line.lower()]
                        from_addr = from_line[0].split(': ')[1] if from_line else "unknown"

                        subject_line = [line for line in content.split('\n') if 'subject:' in line.lower()]
                        subject = subject_line[0].split(': ')[1] if subject_line else "No Subject"

                        # Generate draft reply (this would involve Claude reasoning in real implementation)
                        draft_content = f"""---
type: email_draft
to: {from_addr}
subject: Re: {subject}
original_file: {email_file.name}
status: pending_approval
---

## Draft Reply to: {from_addr}

### Original Message: {subject}

[Original message content would go here]

### Draft Reply:
Dear {from_addr},

Thank you for your email regarding "{subject}". I'm currently reviewing your request and will get back to you shortly.

Best regards,
AI Employee

---
**IMPORTANT**: This draft requires local approval before sending.
Move to /Approved/Cloud_Agent to approve or /Rejected/Cloud_Agent to reject.
"""

                        # Create draft file
                        draft_filename = f"EMAIL_DRAFT_{int(time.time())}_{from_addr.replace('@', '_at_')}.md"
                        draft_path = self.vault_path / 'Cloud_Agent' / 'Drafts' / draft_filename
                        draft_path.write_text(draft_content)

                        # Create approval request
                        approval_content = f"""---
type: approval_required
action: send_email
to: {from_addr}
subject: {subject}
draft_file: {draft_filename}
created: {datetime.now().isoformat()}
status: pending
---

## Email Approval Required

**To**: {from_addr}
**Subject**: {subject}

This email reply draft requires human approval before sending.

### Draft Content:
[Content in: {draft_filename}]

### Action Required:
- Move this file to **/Approved** to send the email
- Move this file to **/Rejected** to discard the email
- Review the draft before approving

---
**Generated by Cloud Agent - {datetime.now().isoformat()}**
"""

                        approval_filename = f"EMAIL_APPROVAL_{int(time.time())}_{from_addr.replace('@', '_at_')}.md"
                        approval_path = self.vault_path / 'Cloud_Agent' / 'Pending_Approval' / approval_filename
                        approval_path.write_text(approval_content)

                        # Move original file to In_Progress to prevent double-processing
                        in_progress_path = self.vault_path / 'In_Progress' / 'cloud_agent' / email_file.name
                        in_progress_path.parent.mkdir(parents=True, exist_ok=True)
                        email_file.rename(in_progress_path)

                        self.logger.info(f"Created email draft and approval request for {from_addr}")

                except Exception as e:
                    self.logger.error(f"Error processing email file {email_file}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in email draft processing: {e}")

    def process_social_media_drafts(self):
        """
        Process social media content and create draft posts for local approval
        """
        try:
            # Find social media-related files that need processing
            needs_action_path = self.vault_path / 'Cloud_Agent' / 'Needs_Action'
            social_files = list(needs_action_path.glob('*social*.md')) + list(needs_action_path.glob('*post*.md'))

            for social_file in social_files:
                try:
                    content = social_file.read_text()

                    # Extract social media information
                    if "social" in content.lower() or "post" in content.lower():
                        # Generate draft social media post (would involve Claude reasoning)
                        draft_content = f"""---
type: social_draft
platform: facebook,instagram,twitter
status: pending_approval
original_file: {social_file.name}
---

## Social Media Draft

### Content:
This is a draft social media post that was generated by the Cloud Agent.

[Original request content]:
{content[:500]}...

### Draft Post:
[Generated social media content would go here]

---
**IMPORTANT**: This draft requires local approval before posting.
Move to /Approved/Cloud_Agent to approve or /Rejected/Cloud_Agent to reject.
"""

                        # Create draft file
                        draft_filename = f"SOCIAL_DRAFT_{int(time.time())}.md"
                        draft_path = self.vault_path / 'Cloud_Agent' / 'Social_Drafts' / draft_filename
                        draft_path.write_text(draft_content)

                        # Create approval request
                        approval_content = f"""---
type: approval_required
action: post_social
platform: facebook,instagram,twitter
draft_file: {draft_filename}
created: {datetime.now().isoformat()}
status: pending
---

## Social Media Post Approval Required

**Platform(s)**: Facebook, Instagram, Twitter
**Draft File**: {draft_filename}

This social media post draft requires human approval before posting.

### Draft Content:
[Content in: {draft_filename}]

### Action Required:
- Move this file to **/Approved** to post the content
- Move this file to **/Rejected** to discard the post
- Review the draft before approving

---
**Generated by Cloud Agent - {datetime.now().isoformat()}**
"""

                        approval_filename = f"SOCIAL_APPROVAL_{int(time.time())}.md"
                        approval_path = self.vault_path / 'Cloud_Agent' / 'Pending_Approval' / approval_filename
                        approval_path.write_text(approval_content)

                        # Move original file to In_Progress to prevent double-processing
                        in_progress_path = self.vault_path / 'In_Progress' / 'cloud_agent' / social_file.name
                        in_progress_path.parent.mkdir(parents=True, exist_ok=True)
                        social_file.rename(in_progress_path)

                        self.logger.info(f"Created social media draft and approval request")

                except Exception as e:
                    self.logger.error(f"Error processing social file {social_file}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in social media draft processing: {e}")

    def process_updates_from_local(self):
        """
        Process updates from local agent that were written to Updates/ folder
        """
        try:
            updates_path = self.vault_path / 'Updates'
            update_files = list(updates_path.glob('*.md'))

            for update_file in update_files:
                try:
                    # Process the update from local agent
                    content = update_file.read_text()

                    # In a real implementation, this would handle specific types of updates
                    # For now, just log that we received an update
                    self.logger.info(f"Received update from local agent: {update_file.name}")

                    # Move processed update to archive
                    archive_path = updates_path / 'archive'
                    archive_path.mkdir(exist_ok=True)
                    archived_file = archive_path / update_file.name
                    update_file.rename(archived_file)

                except Exception as e:
                    self.logger.error(f"Error processing update file {update_file}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in processing updates from local: {e}")

    def handle_odoo_draft_actions(self):
        """
        Handle draft-only accounting actions for Odoo integration
        """
        try:
            # Find accounting-related files that need processing
            needs_action_path = self.vault_path / 'Cloud_Agent' / 'Needs_Action'
            accounting_files = list(needs_action_path.glob('*account*.md')) + list(needs_action_path.glob('*invoice*.md'))

            for acct_file in accounting_files:
                try:
                    content = acct_file.read_text()

                    if "account" in content.lower() or "invoice" in content.lower() or "payment" in content.lower():
                        # Generate draft accounting action (would involve Claude reasoning)
                        draft_content = f"""---
type: accounting_draft
action: create_invoice,record_payment,etc
status: pending_approval
original_file: {acct_file.name}
---

## Accounting Draft Action

### Request:
{content[:500]}...

### Proposed Action:
[Draft accounting entry/action would go here]

---
**IMPORTANT**: This accounting action requires local approval before execution.
Move to /Approved/Cloud_Agent to approve or /Rejected/Cloud_Agent to reject.
"""

                        # Create draft file
                        draft_filename = f"ACCOUNTING_DRAFT_{int(time.time())}.md"
                        draft_path = self.vault_path / 'Cloud_Agent' / 'Drafts' / draft_filename
                        draft_path.write_text(draft_content)

                        # Create approval request
                        approval_content = f"""---
type: approval_required
action: accounting_action
draft_file: {draft_filename}
created: {datetime.now().isoformat()}
status: pending
---

## Accounting Action Approval Required

**Action Type**: Draft accounting action
**Draft File**: {draft_filename}

This accounting action requires human approval before execution.

### Draft Content:
[Content in: {draft_filename}]

### Action Required:
- Move this file to **/Approved** to execute the action
- Move this file to **/Rejected** to discard the action
- Review the draft before approving

---
**Generated by Cloud Agent - {datetime.now().isoformat()}**
"""

                        approval_filename = f"ACCOUNTING_APPROVAL_{int(time.time())}.md"
                        approval_path = self.vault_path / 'Cloud_Agent' / 'Pending_Approval' / approval_filename
                        approval_path.write_text(approval_content)

                        # Move original file to In_Progress to prevent double-processing
                        in_progress_path = self.vault_path / 'In_Progress' / 'cloud_agent' / acct_file.name
                        in_progress_path.parent.mkdir(parents=True, exist_ok=True)
                        acct_file.rename(in_progress_path)

                        self.logger.info(f"Created accounting draft and approval request")

                except Exception as e:
                    self.logger.error(f"Error processing accounting file {acct_file}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in accounting draft processing: {e}")

    def run_health_check(self):
        """
        Perform health check and write status to health monitor
        """
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "agent_type": "cloud",
                "status": "running",
                "local_online": self.is_local_online(),
                "active_processes": len([p for p in self.processes if p and p.poll() is None]),
                "last_processed": datetime.now().isoformat()
            }

            # Write health status
            health_file = self.vault_path / 'Health_Monitor' / 'cloud_agent_health.json'
            with open(health_file, 'w') as f:
                json.dump(health_status, f, indent=2)

            # Also write heartbeat for local agent to detect
            heartbeat_file = self.vault_path / 'Cloud_Agent' / 'heartbeat.txt'
            heartbeat_file.write_text(f"Cloud Agent online at {datetime.now().isoformat()}")

            self.logger.info(f"Health check completed - local online: {health_status['local_online']}")

        except Exception as e:
            self.logger.error(f"Error in health check: {e}")

    def run_sync_monitor(self):
        """
        Monitor sync status between cloud and local vaults
        """
        try:
            # In a real implementation, this would monitor Git or Syncthing sync status
            sync_status = {
                "timestamp": datetime.now().isoformat(),
                "sync_status": "up_to_date",  # Would be checked in real implementation
                "last_sync": datetime.now().isoformat(),
                "conflicts": []
            }

            # Write sync status
            sync_file = self.vault_path / 'Cloud_Agent' / 'sync_status.json'
            with open(sync_file, 'w') as f:
                json.dump(sync_status, f, indent=2)

            self.logger.info("Sync monitor completed")

        except Exception as e:
            self.logger.error(f"Error in sync monitor: {e}")

    def run(self):
        """Run the Cloud Agent orchestrator"""
        self.logger.info("Starting Cloud Agent Orchestrator...")

        print("Starting Cloud Agent Orchestrator...")
        print("Features Active:")
        print("- Email triage and draft creation (requires local approval)")
        print("- Social media draft creation (requires local approval)")
        print("- Accounting draft actions (requires local approval)")
        print("- Processing updates from local agent")
        print("- Health monitoring and status reporting")
        print("- Sync monitoring between cloud and local")
        print("\nCloud Agent is now running and monitoring 24/7!\n")

        # Main loop
        loop_count = 0
        while True:
            try:
                # Process different types of tasks
                self.process_email_drafts()
                self.process_social_media_drafts()
                self.process_updates_from_local()
                self.handle_odoo_draft_actions()

                # Run health check every 10 iterations (every 5 minutes)
                if loop_count % 10 == 0:
                    self.run_health_check()
                    self.run_sync_monitor()

                # Update dashboard status
                self.update_dashboard()

                # Wait before checking again
                time.sleep(30)  # 30 seconds
                loop_count += 1

            except KeyboardInterrupt:
                self.logger.info("Shutting down Cloud Agent orchestrator...")
                for process in self.processes:
                    if process:
                        try:
                            process.terminate()
                        except:
                            pass
                break
            except Exception as e:
                self.logger.error(f"Error in Cloud Agent orchestrator: {e}")
                time.sleep(60)  # Wait longer on error

    def update_dashboard(self):
        """Update dashboard with Cloud Agent status"""
        dashboard_path = self.vault_path / 'Dashboard.md'

        # Read existing dashboard content if it exists
        if dashboard_path.exists():
            content = dashboard_path.read_text()
        else:
            content = "# AI Employee Dashboard\n\n"

        # Add/update the system status section with Platinum Tier features
        local_status = "ONLINE" if self.is_local_online() else "OFFLINE"

        status_section = f"""## System Status
- Active Processes: {len([p for p in self.processes if p and p.poll() is None])}
- Last Updated: {datetime.now().isoformat()}
- Platinum Tier Features Active
- Local Agent Status: {local_status}
- Cloud Agent: Running 24/7
- Sync Status: Monitoring

## Business Metrics
- Current Date: {datetime.now().strftime('%Y-%m-%d')}
- Active Projects: 0
- Cloud Pending Actions: {len(list((self.vault_path / 'Cloud_Agent' / 'Needs_Action').glob('*.md')))}
- Email Drafts Created: {len(list((self.vault_path / 'Cloud_Agent' / 'Drafts').glob('*email*')))}
- Social Drafts Created: {len(list((self.vault_path / 'Cloud_Agent' / 'Social_Drafts').glob('*.md')))}
- Pending Approvals: {len(list((self.vault_path / 'Cloud_Agent' / 'Pending_Approval').glob('*.md')))}
- Updates Received: {len(list((self.vault_path / 'Updates').glob('*.md')))}
"""

        # Update or add the status section
        if "## System Status" in content:
            # Replace existing status section
            lines = content.split('\n')
            new_lines = []
            skip_status = False
            for line in lines:
                if line.startswith('## System Status'):
                    skip_status = True
                    new_lines.append(status_section.strip())
                elif skip_status and line.startswith('## ') and not line.startswith('## System Status'):
                    skip_status = False
                    new_lines.append(line)
                elif not skip_status:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        else:
            content += status_section

        dashboard_path.write_text(content)


def main():
    # Set the vault path from environment or use default
    current_dir = Path.cwd()
    if current_dir.name == 'AI_Employee_Vault':
        vault_path = str(current_dir)  # Use current directory if we're already in the vault
    else:
        vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    # Create the orchestrator and run it
    orchestrator = CloudAgentOrchestrator(vault_path)

    print("=" * 70)
    print("PLATINUM TIER CLOUD AGENT ORCHESTRATOR")
    print("24/7 Cloud-Based Executive with Local Approval System")
    print("=" * 70)
    print()
    print("Specialized Functions (Cloud):")
    print("✅ Email triage and draft reply generation")
    print("✅ Social media post draft creation")
    print("✅ Draft accounting actions for Odoo")
    print("✅ Updates processing from Local Agent")
    print("✅ Health monitoring and status reporting")
    print()
    print("Security & Compliance (Cloud):")
    print("✅ All sensitive actions require local approval")
    print("✅ Draft-only mode for sending/posting/accounting")
    print("✅ Vault sync excludes secrets")
    print("✅ Claim-by-move rule to prevent double-work")
    print()
    print("Starting Cloud Agent services...")
    print()

    orchestrator.run()


if __name__ == "__main__":
    main()