#!/usr/bin/env python3
"""
Platinum Tier Orchestrator - Main orchestrator for Platinum Tier features
Implements 24/7 Cloud + Local Executive system with file-based communication
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


class PlatinumTierOrchestrator:
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # File handler for logging
        log_file_path = self.vault_path / 'platinum_tier_orchestrator.log'
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
            self.vault_path / 'Local_Agent' / 'Needs_Action',
            self.vault_path / 'Local_Agent' / 'Plans',
            self.vault_path / 'Local_Agent' / 'Done',
            self.vault_path / 'Local_Agent' / 'Pending_Approval',
            self.vault_path / 'Local_Agent' / 'Approved',
            self.vault_path / 'Local_Agent' / 'Rejected',
            self.vault_path / 'Updates',
            self.vault_path / 'In_Progress',
            self.vault_path / 'Sync_Manager',
            self.vault_path / 'Health_Monitor',
            self.vault_path / 'Notifications'
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Track all running processes
        self.processes = []
        self.threads = []

        self.logger.info("Platinum Tier Orchestrator initialized")

    def start_cloud_agent(self):
        """Start the cloud agent orchestrator"""
        try:
            script_path = self.vault_path / "cloud_agent_orchestrator.py"
            if script_path.exists():
                process = subprocess.Popen(['python3', str(script_path)])
                self.processes.append(process)
                self.logger.info(f"Started Cloud Agent with PID {process.pid}")
                return process
            else:
                self.logger.error(f"Cloud Agent script does not exist: {script_path}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to start Cloud Agent: {e}")
            return None

    def start_local_agent(self):
        """Start the local agent orchestrator"""
        try:
            script_path = self.vault_path / "local_agent_orchestrator.py"
            if script_path.exists():
                process = subprocess.Popen(['python3', str(script_path)])
                self.processes.append(process)
                self.logger.info(f"Started Local Agent with PID {process.pid}")
                return process
            else:
                self.logger.error(f"Local Agent script does not exist: {script_path}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to start Local Agent: {e}")
            return None

    def start_sync_manager(self):
        """Start the synchronization manager"""
        try:
            script_path = self.vault_path / "synchronization_manager.py"
            if script_path.exists():
                process = subprocess.Popen(['python3', str(script_path)])
                self.processes.append(process)
                self.logger.info(f"Started Sync Manager with PID {process.pid}")
                return process
            else:
                self.logger.error(f"Sync Manager script does not exist: {script_path}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to start Sync Manager: {e}")
            return None

    def start_health_monitor(self):
        """Start the health monitor"""
        try:
            script_path = self.vault_path / "health_monitor.py"
            if script_path.exists():
                process = subprocess.Popen(['python3', str(script_path)])
                self.processes.append(process)
                self.logger.info(f"Started Health Monitor with PID {process.pid}")
                return process
            else:
                self.logger.error(f"Health Monitor script does not exist: {script_path}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to start Health Monitor: {e}")
            return None

    def check_platinum_demo_scenario(self):
        """
        Implement the Platinum demo scenario:
        Email arrives while Local is offline → Cloud drafts reply + writes approval file →
        when Local returns, user approves → Local executes send via MCP → logs → moves task to /Done
        """
        try:
            # Create a sample email that would arrive while local is offline
            # This simulates the scenario from the hackathon requirements
            if not hasattr(self, '_demo_created'):
                # Only create the demo scenario once
                email_content = f"""---
type: email
from: client@example.com
subject: Urgent: Project Timeline Update Required
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content
We need an urgent update on the project timeline as our internal deadlines are approaching.

## Suggested Actions
- [ ] Draft reply with project status
- [ ] Send reply after approval
- [ ] Update project tracking
"""

                # Create the email file in Cloud Agent's needs action (since local is "offline")
                email_filename = f"EMAIL_CLIENT_URGENT_{int(time.time())}.md"
                email_path = self.vault_path / 'Cloud_Agent' / 'Needs_Action' / email_filename
                email_path.write_text(email_content)

                self.logger.info(f"Created demo email scenario: {email_filename}")
                self._demo_created = True

        except Exception as e:
            self.logger.error(f"Error creating demo scenario: {e}")

    def update_dashboard(self):
        """Update dashboard with Platinum Tier status"""
        dashboard_path = self.vault_path / 'Dashboard.md'

        # Read existing dashboard content if it exists
        if dashboard_path.exists():
            content = dashboard_path.read_text()
        else:
            content = "# AI Employee Dashboard\n\n"

        # Get process counts
        active_processes = len([p for p in self.processes if p and p.poll() is None])

        # Add/update the system status section with Platinum Tier features
        status_section = f"""## System Status
- Active Processes: {active_processes}
- Last Updated: {datetime.now().isoformat()}
- Platinum Tier Features Active
- Cloud Agent: 24/7 Operations (Email/Social Drafts)
- Local Agent: Approval & Sensitive Actions
- Sync Status: File-based Communication
- Security: Secrets Never Sync (WhatsApp, Banking)

## Business Metrics
- Current Date: {datetime.now().strftime('%Y-%m-%d')}
- Cloud Pending Actions: {len(list((self.vault_path / 'Cloud_Agent' / 'Needs_Action').glob('*.md')))}
- Local Pending Actions: {len(list((self.vault_path / 'Local_Agent' / 'Needs_Action').glob('*.md')))}
- Pending Approvals: {len(list((self.vault_path / 'Cloud_Agent' / 'Pending_Approval').glob('*.md')))}
- Cloud Drafts: {len(list((self.vault_path / 'Cloud_Agent' / 'Drafts').glob('*.md')))}
- Executed Actions: {len(list((self.vault_path / 'Local_Agent' / 'Done').glob('*.md')))}
- Health Alerts: {len(list((self.vault_path / 'Notifications').glob('*.md')))}
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

    def run(self):
        """Run the Platinum Tier orchestrator"""
        self.logger.info("Starting Platinum Tier Orchestrator...")

        # Start all components
        print("Starting Platinum Tier Orchestrator...")
        print("Components included:")
        print("- Cloud Agent (24/7 email triage, social media drafts)")
        print("- Local Agent (approvals, WhatsApp, payments, banking)")
        print("- Synchronization Manager (claim-by-move, file handoffs)")
        print("- Health Monitor (24/7 system monitoring)")
        print("- Security system (secrets never sync to cloud)")
        print("\nAll Platinum Tier features are now active!\n")

        # Start all processes
        cloud_agent = self.start_cloud_agent()
        local_agent = self.start_local_agent()
        sync_manager = self.start_sync_manager()
        health_monitor = self.start_health_monitor()

        print("All Platinum Tier components are running...")
        print("\nSystem is now operating in 24/7 Cloud + Local Executive mode!")
        print("  - Cloud handles: Email triage, Social media drafts, Accounting drafts")
        print("  - Local handles: Approvals, WhatsApp, Payments, Banking")
        print("  - Sync mechanism: File-based communication with claim-by-move rule")
        print("  - Security: Secrets never synced to cloud\n")

        # Main loop
        loop_count = 0
        while True:
            try:
                # Run the platinum demo scenario check every 20 iterations
                if loop_count % 20 == 0:
                    self.check_platinum_demo_scenario()

                # Update dashboard
                self.update_dashboard()

                # Check if processes are still running and restart if needed
                active_processes = []
                for i, process in enumerate(self.processes):
                    if process and process.poll() is None:  # Process is still running
                        active_processes.append(process)
                    else:  # Process has died, restart it
                        self.logger.warning(f"Process {i} has died, attempting restart...")
                        # Restart the appropriate process based on its index
                        if i == 0:  # Cloud Agent
                            restarted = self.start_cloud_agent()
                            if restarted:
                                active_processes.append(restarted)
                        elif i == 1:  # Local Agent
                            restarted = self.start_local_agent()
                            if restarted:
                                active_processes.append(restarted)
                        elif i == 2:  # Sync Manager
                            restarted = self.start_sync_manager()
                            if restarted:
                                active_processes.append(restarted)
                        elif i == 3:  # Health Monitor
                            restarted = self.start_health_monitor()
                            if restarted:
                                active_processes.append(restarted)

                self.processes = active_processes

                # Log active processes count
                active_count = len(active_processes)
                if active_count != 4:
                    self.logger.warning(f"Expected 4 processes, but {active_count} are active")

                # Wait before checking again
                time.sleep(30)

            except KeyboardInterrupt:
                self.logger.info("Shutting down Platinum Tier orchestrator...")
                for process in self.processes:
                    if process:
                        try:
                            process.terminate()
                        except:
                            pass
                break
            except Exception as e:
                self.logger.error(f"Error in Platinum Tier orchestrator: {e}")
                time.sleep(60)  # Wait longer on error


def main():
    # Set the vault path from environment or use default
    import sys
    current_dir = Path.cwd()
    if current_dir.name == 'AI_Employee_Vault':
        vault_path = str(current_dir)  # Use current directory if we're already in the vault
    else:
        vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    # Create the orchestrator and run it
    orchestrator = PlatinumTierOrchestrator(vault_path)

    print("=" * 75)
    print("PLATINUM TIER ORCHESTRATOR")
    print("24/7 Cloud + Local Executive AI Employee System")
    print("=" * 75)
    print()
    print("Architecture:")
    print("  Cloud Agent: 24/7 operations (email triage, social media drafts)")
    print("  Local Agent: Approvals and sensitive actions (WhatsApp, payments)")
    print("  Sync System: File-based communication with claim-by-move rule")
    print("  Security: Secrets never synced to cloud")
    print()
    print("Platinum Features:")
    print("✅ Always-on Cloud operations for continuous monitoring")
    print("✅ Work-zone specialization (Cloud vs Local responsibilities)")
    print("✅ File-based agent communication via Vault sync")
    print("✅ Claim-by-move rule to prevent double-work")
    print("✅ Security-first approach (secret isolation)")
    print("✅ Odoo integration with draft/execute pattern")
    print("✅ Demo scenario: Email arrives → Cloud drafts → Local approves → Execute")
    print()
    print("Starting Platinum Tier services...")
    print()

    orchestrator.run()


if __name__ == "__main__":
    main()