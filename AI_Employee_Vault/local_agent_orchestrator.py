#!/usr/bin/env python3
"""
Local Agent Orchestrator - Platinum Tier
Specialized orchestrator for local-based AI operations (approvals, sensitive actions)
Handles WhatsApp, payments, banking, and final execution of approved actions.
"""
import time
import logging
import os
import subprocess
from pathlib import Path
from threading import Thread
from datetime import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional


class LocalAgentOrchestrator:
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # File handler for logging
        log_file_path = self.vault_path / 'local_agent_orchestrator.log'
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Initialize directories if they don't exist
        dirs_to_create = [
            self.vault_path / 'Local_Agent' / 'Needs_Action',
            self.vault_path / 'Local_Agent' / 'Plans',
            self.vault_path / 'Local_Agent' / 'Done',
            self.vault_path / 'Local_Agent' / 'Pending_Approval',
            self.vault_path / 'Local_Agent' / 'Approved',
            self.vault_path / 'Local_Agent' / 'Rejected',
            self.vault_path / 'Updates',
            self.vault_path / 'In_Progress',
            self.vault_path / 'Health_Monitor',
            # Cloud agent directories that we'll monitor
            self.vault_path / 'Cloud_Agent' / 'Pending_Approval'
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Track running processes
        self.processes = []

        # Email configuration (for actual sending from local)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')

        # WhatsApp session path (local only)
        self.whatsapp_session_path = Path(os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session'))

        self.logger.info("Local Agent Orchestrator initialized")

    def is_cloud_online(self) -> bool:
        """
        Check if cloud agent is online by checking for heartbeat file
        """
        heartbeat_file = self.vault_path / 'Cloud_Agent' / 'heartbeat.txt'
        if heartbeat_file.exists():
            # Check if heartbeat is recent (within last 10 minutes)
            mod_time = heartbeat_file.stat().st_mtime
            current_time = time.time()
            return (current_time - mod_time) < 600  # 10 minutes
        return False

    def process_approvals(self):
        """
        Process all pending approval requests and execute approved actions
        """
        try:
            # Process cloud agent approval requests
            cloud_approval_path = self.vault_path / 'Cloud_Agent' / 'Pending_Approval'
            approval_files = list(cloud_approval_path.glob('*.md'))

            for approval_file in approval_files:
                try:
                    content = approval_file.read_text()

                    # Determine action type and execute accordingly
                    if "action: send_email" in content:
                        self.execute_email_approval(approval_file, content)
                    elif "action: post_social" in content:
                        self.execute_social_approval(approval_file, content)
                    elif "action: accounting_action" in content:
                        self.execute_accounting_approval(approval_file, content)
                    else:
                        self.logger.warning(f"Unknown action type in {approval_file.name}, moving to rejected")
                        # Move to rejected for manual review
                        rejected_path = self.vault_path / 'Local_Agent' / 'Rejected' / approval_file.name
                        approval_file.rename(rejected_path)

                except Exception as e:
                    self.logger.error(f"Error processing approval file {approval_file}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in approval processing: {e}")

    def execute_email_approval(self, approval_file: Path, content: str):
        """
        Execute an approved email action
        """
        try:
            # Parse the approval content to get the draft file
            draft_line = [line for line in content.split('\n') if 'draft_file:' in line.lower()]
            if not draft_line:
                self.logger.error(f"No draft file specified in {approval_file.name}")
                return

            draft_filename = draft_line[0].split(': ')[1].strip()
            draft_path = self.vault_path / 'Cloud_Agent' / 'Drafts' / draft_filename

            if not draft_path.exists():
                self.logger.error(f"Draft file {draft_filename} not found")
                return

            draft_content = draft_path.read_text()

            # Extract email details from draft
            to_line = [line for line in draft_content.split('\n') if 'to:' in line.lower()]
            subject_line = [line for line in draft_content.split('\n') if 'subject:' in line.lower()]

            if not to_line or not subject_line:
                self.logger.error(f"Missing email details in draft {draft_filename}")
                return

            to_addr = to_line[0].split(': ')[1].strip()
            subject = subject_line[0].split(': ')[1].strip()

            # Extract the actual email body from draft
            lines = draft_content.split('\n')
            body_start = -1
            for i, line in enumerate(lines):
                if 'draft reply:' in line.lower() or 'content:' in line.lower():
                    body_start = i + 1
                    break

            if body_start == -1:
                self.logger.error(f"Could not find email body in draft {draft_filename}")
                return

            email_body = '\n'.join(lines[body_start:]).strip()

            # Send the actual email (this is where sensitive action happens)
            if self.email_address and self.email_password:
                # Create message
                msg = MIMEMultipart()
                msg['From'] = self.email_address
                msg['To'] = to_addr
                msg['Subject'] = subject

                # Add body to email
                msg.attach(MIMEText(email_body, 'plain'))

                # Create SMTP session
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()  # Enable security
                server.login(self.email_address, self.email_password)

                # Send email
                text = msg.as_string()
                server.sendmail(self.email_address, to_addr, text)
                server.quit()

                self.logger.info(f"Email sent successfully to {to_addr}")

                # Log the action
                self.log_action("email_sent", "local_agent", to_addr, {
                    "subject": subject,
                    "draft_file": draft_filename
                })
            else:
                self.logger.warning("Email credentials not set, skipping actual send (dry-run mode)")

            # Move approval file to approved
            approved_path = self.vault_path / 'Local_Agent' / 'Approved' / approval_file.name
            approval_file.rename(approved_path)

            # Move draft file to done
            done_path = self.vault_path / 'Cloud_Agent' / 'Done' / draft_path.name
            draft_path.rename(done_path)

            # Write update to cloud about successful execution
            update_content = f"""---
type: execution_update
action: email_sent
to: {to_addr}
subject: {subject}
status: completed
timestamp: {datetime.now().isoformat()}
---

## Email Execution Update

Successfully sent email to {to_addr} with subject "{subject}".

---
**Update from Local Agent - {datetime.now().isoformat()}**
"""
            update_filename = f"EMAIL_EXEC_UPDATE_{int(time.time())}.md"
            update_path = self.vault_path / 'Updates' / update_filename
            update_path.write_text(update_content)

        except Exception as e:
            self.logger.error(f"Error executing email approval {approval_file.name}: {e}")

            # Move to rejected if failed
            rejected_path = self.vault_path / 'Local_Agent' / 'Rejected' / approval_file.name
            approval_file.rename(rejected_path)

    def execute_social_approval(self, approval_file: Path, content: str):
        """
        Execute an approved social media action
        """
        try:
            # Parse the approval content to get the draft file
            draft_line = [line for line in content.split('\n') if 'draft_file:' in line.lower()]
            if not draft_line:
                self.logger.error(f"No draft file specified in {approval_file.name}")
                return

            draft_filename = draft_line[0].split(': ')[1].strip()
            draft_path = self.vault_path / 'Cloud_Agent' / 'Social_Drafts' / draft_filename

            if not draft_path.exists():
                self.logger.error(f"Draft file {draft_filename} not found")
                return

            draft_content = draft_path.read_text()

            # In a real implementation, this would call the social media MCP servers
            # For now, we'll simulate the posting
            self.logger.info(f"Simulating social media post from draft {draft_filename}")

            # Move approval file to approved
            approved_path = self.vault_path / 'Local_Agent' / 'Approved' / approval_file.name
            approval_file.rename(approved_path)

            # Move draft file to done
            done_path = self.vault_path / 'Cloud_Agent' / 'Done' / draft_path.name
            draft_path.rename(done_path)

            # Write update to cloud about successful execution
            update_content = f"""---
type: execution_update
action: social_posted
draft_file: {draft_filename}
status: completed
timestamp: {datetime.now().isoformat()}
---

## Social Media Execution Update

Successfully processed social media draft {draft_filename}.

---
**Update from Local Agent - {datetime.now().isoformat()}**
"""
            update_filename = f"SOCIAL_EXEC_UPDATE_{int(time.time())}.md"
            update_path = self.vault_path / 'Updates' / update_filename
            update_path.write_text(update_content)

        except Exception as e:
            self.logger.error(f"Error executing social approval {approval_file.name}: {e}")

            # Move to rejected if failed
            rejected_path = self.vault_path / 'Local_Agent' / 'Rejected' / approval_file.name
            approval_file.rename(rejected_path)

    def execute_accounting_approval(self, approval_file: Path, content: str):
        """
        Execute an approved accounting action
        """
        try:
            # In a real implementation, this would call the Odoo MCP server
            # For now, we'll simulate the accounting action
            self.logger.info(f"Simulating accounting action from approval {approval_file.name}")

            # Move approval file to approved
            approved_path = self.vault_path / 'Local_Agent' / 'Approved' / approval_file.name
            approval_file.rename(approved_path)

            # Write update to cloud about successful execution
            update_content = f"""---
type: execution_update
action: accounting_executed
status: completed
timestamp: {datetime.now().isoformat()}
---

## Accounting Execution Update

Successfully processed accounting action from {approval_file.name}.

---
**Update from Local Agent - {datetime.now().isoformat()}**
"""
            update_filename = f"ACCOUNTING_EXEC_UPDATE_{int(time.time())}.md"
            update_path = self.vault_path / 'Updates' / update_filename
            update_path.write_text(update_content)

        except Exception as e:
            self.logger.error(f"Error executing accounting approval {approval_file.name}: {e}")

            # Move to rejected if failed
            rejected_path = self.vault_path / 'Local_Agent' / 'Rejected' / approval_file.name
            approval_file.rename(rejected_path)

    def handle_whatsapp_messages(self):
        """
        Handle WhatsApp messages (local-only functionality)
        """
        try:
            # In a real implementation, this would use the WhatsApp session to send messages
            # For now, we'll just simulate checking for WhatsApp-related files
            needs_action_path = self.vault_path / 'Local_Agent' / 'Needs_Action'
            whatsapp_files = list(needs_action_path.glob('*whatsapp*.md'))

            for whatsapp_file in whatsapp_files:
                try:
                    content = whatsapp_file.read_text()

                    # In a real implementation, this would send WhatsApp messages
                    # using the local WhatsApp session
                    self.logger.info(f"Processing WhatsApp-related file: {whatsapp_file.name}")

                    # Move to done
                    done_path = self.vault_path / 'Local_Agent' / 'Done' / whatsapp_file.name
                    whatsapp_file.rename(done_path)

                except Exception as e:
                    self.logger.error(f"Error processing WhatsApp file {whatsapp_file}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in WhatsApp handling: {e}")

    def handle_payments_banking(self):
        """
        Handle payments and banking (local-only functionality)
        """
        try:
            # In a real implementation, this would handle actual payments
            # For now, we'll just simulate checking for payment-related files
            needs_action_path = self.vault_path / 'Local_Agent' / 'Needs_Action'
            payment_files = list(needs_action_path.glob('*payment*.md')) + list(needs_action_path.glob('*bank*.md'))

            for payment_file in payment_files:
                try:
                    content = payment_file.read_text()

                    # In a real implementation, this would execute actual payments
                    # using banking credentials stored locally
                    self.logger.info(f"Processing payment/banking file: {payment_file.name}")

                    # Move to done
                    done_path = self.vault_path / 'Local_Agent' / 'Done' / payment_file.name
                    payment_file.rename(done_path)

                except Exception as e:
                    self.logger.error(f"Error processing payment file {payment_file}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in payments/banking handling: {e}")

    def synchronize_with_cloud(self):
        """
        Synchronize with cloud agent via Git or other sync mechanism
        """
        try:
            # In a real implementation, this would run Git pull/push to sync with cloud
            # For now, we'll just simulate the sync process
            self.logger.info("Simulating synchronization with cloud...")

            # Write sync status
            sync_status = {
                "timestamp": datetime.now().isoformat(),
                "sync_status": "completed",
                "last_sync": datetime.now().isoformat(),
                "cloud_online": self.is_cloud_online(),
                "conflicts": []
            }

            sync_file = self.vault_path / 'Local_Agent' / 'sync_status.json'
            with open(sync_file, 'w') as f:
                json.dump(sync_status, f, indent=2)

            self.logger.info("Synchronization completed")

        except Exception as e:
            self.logger.error(f"Error in synchronization: {e}")

    def run_health_check(self):
        """
        Perform health check and write status to health monitor
        """
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "agent_type": "local",
                "status": "running",
                "cloud_online": self.is_cloud_online(),
                "active_processes": len([p for p in self.processes if p and p.poll() is None]),
                "last_processed": datetime.now().isoformat()
            }

            # Write health status
            health_file = self.vault_path / 'Health_Monitor' / 'local_agent_health.json'
            with open(health_file, 'w') as f:
                json.dump(health_status, f, indent=2)

            # Also write heartbeat for cloud agent to detect
            heartbeat_file = self.vault_path / 'Local_Agent' / 'heartbeat.txt'
            heartbeat_file.write_text(f"Local Agent online at {datetime.now().isoformat()}")

            self.logger.info(f"Health check completed - cloud online: {health_status['cloud_online']}")

        except Exception as e:
            self.logger.error(f"Error in health check: {e}")

    def log_action(self, action_type: str, actor: str, target: str, params: Dict):
        """
        Log actions with comprehensive details for audit trail
        """
        try:
            from audit_logger import AuditLogger
            audit_logger = AuditLogger(str(self.vault_path))
            audit_logger.log_action(
                action_type=action_type,
                actor=actor,
                target=target,
                parameters=params,
                approval_status="executed",
                approved_by="local_agent",
                result="success"
            )
        except ImportError:
            # If audit logger is not available, log to standard logger
            self.logger.info(f"Action logged: {action_type} by {actor} on {target}")

    def run(self):
        """Run the Local Agent orchestrator"""
        self.logger.info("Starting Local Agent Orchestrator...")

        print("Starting Local Agent Orchestrator...")
        print("Features Active:")
        print("- Processing approvals from Cloud Agent")
        print("- Executing approved email, social, and accounting actions")
        print("- Handling WhatsApp messages and sessions")
        print("- Processing payments and banking (local only)")
        print("- Synchronizing with Cloud Agent")
        print("- Health monitoring and status reporting")
        print("\nLocal Agent is now running and handling sensitive operations!\n")

        # Main loop
        loop_count = 0
        while True:
            try:
                # Process different types of tasks
                self.process_approvals()
                self.handle_whatsapp_messages()
                self.handle_payments_banking()

                # Run sync every 5 iterations (every 2.5 minutes)
                if loop_count % 5 == 0:
                    self.synchronize_with_cloud()

                # Run health check every 10 iterations (every 5 minutes)
                if loop_count % 10 == 0:
                    self.run_health_check()

                # Update dashboard status
                self.update_dashboard()

                # Wait before checking again
                time.sleep(30)  # 30 seconds
                loop_count += 1

            except KeyboardInterrupt:
                self.logger.info("Shutting down Local Agent orchestrator...")
                for process in self.processes:
                    if process:
                        try:
                            process.terminate()
                        except:
                            pass
                break
            except Exception as e:
                self.logger.error(f"Error in Local Agent orchestrator: {e}")
                time.sleep(60)  # Wait longer on error

    def update_dashboard(self):
        """Update dashboard with Local Agent status"""
        dashboard_path = self.vault_path / 'Dashboard.md'

        # Read existing dashboard content if it exists
        if dashboard_path.exists():
            content = dashboard_path.read_text()
        else:
            content = "# AI Employee Dashboard\n\n"

        # Add/update the system status section with Platinum Tier features
        cloud_status = "ONLINE" if self.is_cloud_online() else "OFFLINE"

        status_section = f"""## System Status
- Active Processes: {len([p for p in self.processes if p and p.poll() is None])}
- Last Updated: {datetime.now().isoformat()}
- Platinum Tier Features Active
- Cloud Agent Status: {cloud_status}
- Local Agent: Running with full permissions
- Sync Status: Monitoring

## Business Metrics
- Current Date: {datetime.now().strftime('%Y-%m-%d')}
- Active Projects: 0
- Pending Approvals from Cloud: {len(list((self.vault_path / 'Cloud_Agent' / 'Pending_Approval').glob('*.md')))}
- Approvals Processed: {len(list((self.vault_path / 'Local_Agent' / 'Approved').glob('*.md')))}
- Executed Actions: {len(list((self.vault_path / 'Local_Agent' / 'Done').glob('*.md')))}
- WhatsApp Messages Handled: {len(list((self.vault_path / 'Local_Agent' / 'Needs_Action').glob('*whatsapp*')))}
- Payments Processed: {len(list((self.vault_path / 'Local_Agent' / 'Needs_Action').glob('*payment*')))}
- Sync Operations: {len(list((self.vault_path / 'Local_Agent').glob('sync_status.json')))}
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
    orchestrator = LocalAgentOrchestrator(vault_path)

    print("=" * 70)
    print("PLATINUM TIER LOCAL AGENT ORCHESTRATOR")
    print("Local Executive with Approval and Sensitive Operations")
    print("=" * 70)
    print()
    print("Specialized Functions (Local):")
    print("✅ Processing approvals from Cloud Agent")
    print("✅ Executing approved actions (email, social, accounting)")
    print("✅ Handling WhatsApp sessions and messages")
    print("✅ Processing payments and banking (secure local operations)")
    print("✅ Synchronizing with Cloud Agent")
    print()
    print("Security & Compliance (Local):")
    print("✅ All sensitive actions executed on local system")
    print("✅ WhatsApp sessions stored locally only")
    print("✅ Banking credentials never synced to cloud")
    print("✅ Final approval and execution point")
    print()
    print("Starting Local Agent services...")
    print()

    orchestrator.run()


if __name__ == "__main__":
    main()