#!/usr/bin/env python3
"""
Advanced Orchestrator - Implements Claude reasoning loop and Plan.md creation
"""
import time
import logging
from pathlib import Path
import os
import subprocess
import json
from datetime import datetime
from typing import List, Dict, Any


class AdvancedOrchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_dir = self.vault_path / 'Plans'
        self.done_dir = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.dashboard_path = self.vault_path / 'Dashboard.md'
        self.company_handbook_path = self.vault_path / 'Company_Handbook.md'

        # Create directories if they don't exist
        for dir_path in [self.needs_action, self.plans_dir, self.done_dir, self.pending_approval]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # File handler for logging
        handler = logging.FileHandler(self.vault_path / 'orchestrator.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def get_needs_action_files(self) -> List[Path]:
        """Get all files in Needs_Action directory"""
        return list(self.needs_action.glob("*.md"))

    def get_pending_approval_files(self) -> List[Path]:
        """Get all files in Pending_Approval directory"""
        return list(self.pending_approval.glob("*.md"))

    def create_plan_file(self, task_description: str, related_files: List[Path] = None) -> Path:
        """Create a Plan.md file based on task description"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_filename = f"PLAN_{timestamp}.md"
        plan_path = self.plans_dir / plan_filename

        related_files_str = ""
        if related_files:
            related_files_str = "\n".join([f"- {f.name}" for f in related_files])

        plan_content = f"""---
created: {datetime.now().isoformat()}
status: pending
related_files:
  - {related_files_str}
---

# Plan: {task_description}

## Objective
{task_description}

## Context
The following files triggered this plan:
{related_files_str}

## Steps
- [ ] Analyze requirements
- [ ] Research possible approaches
- [ ] Execute action
- [ ] Verify completion
- [ ] Update dashboard

## Approval Required
- [ ] Human approval if action involves payments or sensitive data

## Expected Outcome
{task_description} successfully completed.

## Notes
Additional implementation details as needed.
"""
        plan_path.write_text(plan_content)
        self.logger.info(f"Created plan file: {plan_path.name}")
        return plan_path

    def trigger_claude_reasoning(self, plan_path: Path) -> bool:
        """Trigger Claude reasoning on a plan file"""
        try:
            # This would be where you call Claude Code to work on the plan
            # For now, we'll simulate the process

            plan_content = plan_path.read_text()

            # In a real implementation, you would call Claude like:
            # result = subprocess.run([
            #     'claude', 'reason', '--file', str(plan_path)
            # ], capture_output=True, text=True, cwd=self.vault_path)

            # For simulation, we'll mark the plan as processed
            self.logger.info(f"Simulated Claude reasoning on: {plan_path.name}")

            # Move the plan to Done after "processing"
            new_path = self.done_dir / plan_path.name
            plan_path.rename(new_path)

            return True
        except Exception as e:
            self.logger.error(f"Error triggering Claude reasoning: {e}")
            return False

    def check_and_process_needs_action(self):
        """Check for new action items and create plans"""
        needs_action_files = self.get_needs_action_files()

        for file_path in needs_action_files:
            self.logger.info(f"Processing needs action file: {file_path.name}")

            # Read the file to understand what needs to be done
            content = file_path.read_text()

            # Create a plan based on the content
            # This is a simplified approach - in reality, Claude would analyze the content
            task_description = f"Process {file_path.stem}"

            # Create plan file
            plan_path = self.create_plan_file(task_description, [file_path])

            # Optionally trigger Claude reasoning on the plan immediately
            # self.trigger_claude_reasoning(plan_path)

            # Move the original file to Done
            done_path = self.done_dir / file_path.name
            file_path.rename(done_path)

    def check_pending_approval(self):
        """Check for pending approvals and process them"""
        approval_files = self.get_pending_approval_files()

        for file_path in approval_files:
            self.logger.info(f"Checking approval file: {file_path.name}")

            # In a real system, this would check if the file has been approved
            # by looking for approval markers or checking if it was moved to an approved directory
            # For now, we'll just log it exists

    def update_dashboard(self):
        """Update the dashboard with recent activity"""
        dashboard_content = f"""# Dashboard

## Last Updated
{datetime.now().isoformat()}

## Activity Summary
- Total Needs Action Files Processed: {len(list(self.done_dir.glob("*.md")))}
- Active Plans: {len(list(self.plans_dir.glob("*.md")))}
- Pending Approvals: {len(list(self.pending_approval.glob("*.md")))}

## Recent Activity
"""
        # Add recent activities
        recent_done = sorted(self.done_dir.glob("*.md"), key=os.path.getmtime, reverse=True)[:5]
        for file_path in recent_done:
            dashboard_content += f"- {file_path.name} ({datetime.fromtimestamp(file_path.stat().st_mtime)})\n"

        self.dashboard_path.write_text(dashboard_content)

    def run(self):
        """Main orchestrator loop"""
        self.logger.info("Starting Advanced Orchestrator...")

        while True:
            try:
                self.logger.info("Checking for new action items...")

                # Process needs action files
                self.check_and_process_needs_action()

                # Check pending approvals
                self.check_pending_approval()

                # Update dashboard
                self.update_dashboard()

                # Wait for a while before next check
                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Error in orchestrator: {e}")
                time.sleep(60)  # Wait longer if there's an error


if __name__ == "__main__":
    # Initialize with vault path
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    orchestrator = AdvancedOrchestrator(vault_path)

    print("Starting Advanced Orchestrator...")
    orchestrator.run()