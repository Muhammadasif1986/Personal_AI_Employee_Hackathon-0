#!/usr/bin/env python3
"""
OpenRouter Orchestrator - Main orchestrator configured to use OpenRouter API
Replaces Claude Code reasoning with OpenRouter AI models
"""
import time
import logging
from pathlib import Path
import os
import subprocess
from threading import Thread
from datetime import datetime
from .openrouter_reasoning import OpenRouterReasoning


class OpenRouterOrchestrator:
    def __init__(self, vault_path: str = "./AI_Employee_Vault", model: str = "anthropic/claude-3.5-sonnet"):
        self.vault_path = Path(vault_path)
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # File handler for logging
        log_file_path = self.vault_path / 'openrouter_orchestrator.log'
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Initialize OpenRouter reasoning
        try:
            self.reasoning = OpenRouterReasoning(vault_path=vault_path, model=model)
            self.logger.info(f"OpenRouter Orchestrator initialized with model: {model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenRouter reasoning: {e}")
            raise

        # Create directories if they don't exist
        dirs_to_create = [
            self.vault_path / 'Needs_Action',
            self.vault_path / 'Plans',
            self.vault_path / 'Done',
            self.vault_path / 'Pending_Approval',
            self.vault_path / 'Approved',
            self.vault_path / 'Rejected',
            self.vault_path / 'Scheduled',
            self.vault_path / 'Tasks',
            self.vault_path / 'Inbox',
            self.vault_path / 'Social_Drafts',
            self.vault_path / 'Email_Drafts'
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_needs_action_files(self):
        """Get all files in Needs_Action directory"""
        return list((self.vault_path / 'Needs_Action').glob("*.md"))

    def get_inbox_files(self):
        """Get all files in Inbox directory"""
        return list((self.vault_path / 'Inbox').glob("*.md"))

    def process_needs_action_files(self):
        """Process all files in Needs_Action directory using OpenRouter AI"""
        needs_action_files = self.get_needs_action_files()

        for file_path in needs_action_files:
            try:
                self.logger.info(f"Processing needs action file with OpenRouter AI: {file_path.name}")

                # Process the file using OpenRouter reasoning
                result = self.reasoning.process_file_with_ai(
                    file_path=file_path,
                    company_handbook=self.get_company_handbook()
                )

                if "error" not in result:
                    # Move to Done after successful processing
                    done_path = self.vault_path / 'Done' / file_path.name
                    file_path.rename(done_path)
                    self.logger.info(f"Successfully processed: {file_path.name}")
                else:
                    # Move to Rejected if there was an error
                    rejected_path = self.vault_path / 'Rejected' / file_path.name
                    file_path.rename(rejected_path)
                    self.logger.error(f"Failed to process: {file_path.name}, moved to Rejected")

            except Exception as e:
                self.logger.error(f"Error processing needs action file {file_path}: {e}")
                try:
                    # Move to Rejected on error
                    rejected_path = self.vault_path / 'Rejected' / file_path.name
                    file_path.rename(rejected_path)
                except:
                    pass

    def process_inbox_files(self):
        """Process all files in Inbox directory using OpenRouter AI"""
        inbox_files = self.get_inbox_files()

        for file_path in inbox_files:
            try:
                self.logger.info(f"Processing inbox file with OpenRouter AI: {file_path.name}")

                # Move file to Needs_Action for processing
                needs_action_path = self.vault_path / 'Needs_Action' / file_path.name
                file_path.rename(needs_action_path)

                # The file will be picked up by process_needs_action_files in the next cycle
                self.logger.info(f"Moved to Needs_Action: {file_path.name}")

            except Exception as e:
                self.logger.error(f"Error processing inbox file {file_path}: {e}")
                try:
                    # Move to Rejected on error
                    rejected_path = self.vault_path / 'Rejected' / file_path.name
                    file_path.rename(rejected_path)
                except:
                    pass

    def get_company_handbook(self) -> str:
        """Read the company handbook from the vault"""
        handbook_path = self.vault_path / 'Company_Handbook.md'
        if handbook_path.exists():
            return handbook_path.read_text()
        return "No company handbook found. Follow standard business practices."

    def update_dashboard(self):
        """Update dashboard with current status"""
        dashboard_path = self.vault_path / 'Dashboard.md'

        # Read existing dashboard content if it exists
        if dashboard_path.exists():
            content = dashboard_path.read_text()
        else:
            content = "# AI Employee Dashboard\n\n"

        # Get counts
        needs_action_count = len(self.get_needs_action_files())
        inbox_count = len(self.get_inbox_files())
        done_count = len(list((self.vault_path / 'Done').glob("*.md")))
        rejected_count = len(list((self.vault_path / 'Rejected').glob("*.md")))
        pending_approval_count = len(list((self.vault_path / 'Pending_Approval').glob("*.md")))

        # Add/update the system status section
        status_section = f"""## System Status
- Last Updated: {datetime.now().isoformat()}
- AI Model: {self.model}
- OpenRouter Integration: Active
- Active Processes: 1 (OpenRouter Orchestrator)

## Business Metrics
- Current Date: {datetime.now().strftime('%Y-%m-%d')}
- Inbox Items: {inbox_count}
- Needs Action: {needs_action_count}
- Pending Approval: {pending_approval_count}
- Completed Tasks: {done_count}
- Rejected Tasks: {rejected_count}

## OpenRouter Features Active
- ✅ AI Reasoning with {self.model}
- ✅ Automated Task Processing
- ✅ File-based Workflow Management
- ✅ Company Handbook Integration
- ✅ Error Handling and Logging
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
        """Main orchestrator loop"""
        self.logger.info("Starting OpenRouter Orchestrator...")
        print("Starting OpenRouter Orchestrator...")
        print(f"Using AI Model: {self.model}")
        print("OpenRouter API integration is active")
        print("Processing files with AI reasoning...")
        print()

        while True:
            try:
                # Process inbox files first (move to Needs_Action)
                self.process_inbox_files()

                # Process needs action files using OpenRouter AI
                self.process_needs_action_files()

                # Update dashboard
                self.update_dashboard()

                # Wait before next cycle
                time.sleep(30)  # Check every 30 seconds

            except KeyboardInterrupt:
                self.logger.info("Shutting down OpenRouter orchestrator...")
                print("OpenRouter Orchestrator stopped.")
                break
            except Exception as e:
                self.logger.error(f"Error in OpenRouter orchestrator: {e}")
                time.sleep(60)  # Wait longer on error


def main():
    # Set the vault path from environment or use default
    import sys
    current_dir = Path.cwd()
    if current_dir.name == 'AI_Employee_Vault':
        vault_path = str(current_dir)  # Use current directory if we're already in the vault
    else:
        vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    # Get model from environment or use default
    model = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')

    # Create the orchestrator and run it
    orchestrator = OpenRouterOrchestrator(vault_path, model)

    print("=" * 70)
    print("OPENROUTER AI EMPLOYEE ORCHESTRATOR")
    print("=" * 70)
    print()
    print(f"Configuration:")
    print(f"  • Vault Path: {vault_path}")
    print(f"  • AI Model: {model}")
    print(f"  • API Provider: OpenRouter")
    print()
    print("Features:")
    print("  ✅ OpenRouter API Integration")
    print("  ✅ AI-Powered Task Processing")
    print("  ✅ File-Based Workflow Management")
    print("  ✅ Company Handbook Integration")
    print("  ✅ Automatic Dashboard Updates")
    print("  ✅ Comprehensive Logging")
    print()
    print("Starting OpenRouter AI Employee...")
    print()

    orchestrator.run()


if __name__ == "__main__":
    main()