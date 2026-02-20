#!/usr/bin/env python3
"""
Advanced Orchestrator - Integrates all Silver Tier components
"""
import time
import logging
from pathlib import Path
import os
import subprocess
from threading import Thread
from datetime import datetime


class IntegratedOrchestrator:
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # File handler for logging - make sure we're using the correct path
        log_file_path = self.vault_path / 'integrated_orchestrator.log'
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

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
            self.vault_path / 'Approved',
            self.vault_path / 'Rejected'
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

    def start_watcher(self, script_name: str):
        """Start a watcher script as a subprocess"""
        script_path = self.vault_path / script_name
        if script_path.exists():
            try:
                # Start the watcher as a background process
                # Use python3 instead of python for compatibility
                process = subprocess.Popen(['python3', str(script_path)])
                self.logger.info(f"Started {script_name} with PID {process.pid}")
                return process
            except Exception as e:
                self.logger.error(f"Failed to start {script_name}: {e}")
                return None
        else:
            self.logger.warning(f"Script {script_name} does not exist")
            return None

    def start_component(self, component_name: str):
        """Start a specific component"""
        script_name = f"{component_name}.py"
        script_path = self.vault_path / script_name

        if script_path.exists():
            try:
                # For MCP servers, we need to handle them specially
                if "mcp" in component_name.lower():
                    # MCP servers need to be integrated with Claude Code differently
                    self.logger.info(f"Prepared {script_name} for MCP integration")
                    return True
                else:
                    # Use python3 instead of python for compatibility
                    process = subprocess.Popen(['python3', str(script_path)])
                    self.logger.info(f"Started {component_name} with PID {process.pid}")
                    return process
            except Exception as e:
                self.logger.error(f"Failed to start {component_name}: {e}")
                return None
        else:
            self.logger.warning(f"Component {component_name} does not exist as a script")
            return None

    def run(self):
        """Run the integrated orchestrator"""
        self.logger.info("Starting Integrated Orchestrator for Silver Tier...")

        # Start all Silver Tier components
        processes = []

        # Start watchers
        watcher_processes = [
            self.start_watcher("email_watcher.py"),
            self.start_watcher("whatsapp_watcher.py"),
        ]
        processes.extend([p for p in watcher_processes if p])

        # Start other components
        other_processes = [
            self.start_component("linkedin_poster"),
            self.start_component("advanced_orchestrator"),
            self.start_component("approval_handler"),
            self.start_component("scheduler")
        ]
        processes.extend([p for p in other_processes if p])

        self.logger.info(f"Started {len(processes)} processes")

        # Main loop
        while True:
            try:
                # Keep track of active processes
                active_processes = [p for p in processes if p and p.poll() is None]

                # Restart any processes that have died
                for i, process in enumerate(processes):
                    if process and process.poll() is None:  # Process has died
                        self.logger.warning(f"Process {process.pid} has died, restarting...")

                        # Restart based on the original script
                        if i < 2:  # These are the watchers
                            script_names = ["email_watcher.py", "whatsapp_watcher.py"]
                            if i < len(script_names):
                                new_process = self.start_watcher(script_names[i])
                                if new_process:
                                    processes[i] = new_process
                        else:  # These are other components
                            component_names = ["linkedin_poster", "advanced_orchestrator",
                                             "approval_handler", "scheduler"]
                            orig_idx = i - 2
                            if orig_idx < len(component_names):
                                new_process = self.start_component(component_names[orig_idx])
                                if new_process:
                                    processes[i] = new_process

                # Update dashboard with status
                self.update_dashboard(len(active_processes))

                # Wait before checking again
                time.sleep(30)

            except KeyboardInterrupt:
                self.logger.info("Shutting down orchestrator...")
                for process in processes:
                    if process:
                        try:
                            process.terminate()
                        except:
                            pass
                break
            except Exception as e:
                self.logger.error(f"Error in orchestrator: {e}")
                time.sleep(60)  # Wait longer on error

    def update_dashboard(self, active_processes: int):
        """Update dashboard with system status"""
        dashboard_path = self.vault_path / 'Dashboard.md'

        # Read existing dashboard content if it exists
        if dashboard_path.exists():
            content = dashboard_path.read_text()
        else:
            content = "# Dashboard\n\n"

        # Add/update the system status section
        status_section = f"""## System Status
- Active Processes: {active_processes}
- Last Updated: {datetime.now().isoformat()}
- Silver Tier Features Active

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

        # Update the Active Processes count specifically in the dashboard
        lines = content.split('\n')
        updated_lines = []
        for line in lines:
            if line.startswith('- Active Processes:'):
                updated_lines.append(f'- Active Processes: {active_processes}')
            elif line.startswith('- Last Updated:'):
                updated_lines.append(f'- Last Updated: {datetime.now().isoformat()}')
            else:
                updated_lines.append(line)

        content = '\n'.join(updated_lines)
        dashboard_path.write_text(content)


def main():
    # Set the vault path from environment or use default
    # If running from within AI_Employee_Vault, use current directory
    import sys
    current_dir = Path.cwd()
    if current_dir.name == 'AI_Employee_Vault':
        vault_path = str(current_dir)  # Use current directory if we're already in the vault
    else:
        vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    # Create the orchestrator and run it
    orchestrator = IntegratedOrchestrator(vault_path)

    print("Starting Integrated Orchestrator for Silver Tier...")
    print("Components included:")
    print("- Email Watcher")
    print("- WhatsApp Watcher")
    print("- LinkedIn Poster")
    print("- Advanced Orchestrator with Claude reasoning loop")
    print("- Human-in-the-Loop Approval Handler")
    print("- Task Scheduler")
    print("\nAll Silver Tier features are now active!\n")

    orchestrator.run()


if __name__ == "__main__":
    main()