# orchestrator.py
# Main orchestrator for the AI Employee system
import time
import logging
from pathlib import Path
import subprocess
import threading

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AI_Employee_Orchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'

        # Create directories if they don't exist
        for dir_path in [self.needs_action, self.done, self.plans, self.pending_approval]:
            dir_path.mkdir(exist_ok=True)

    def check_for_tasks(self):
        """Check for new tasks that need processing"""
        needs_action_files = list(self.needs_action.glob('*.md'))
        pending_approval_files = list(self.pending_approval.glob('*.md'))

        logger.info(f"Found {len(needs_action_files)} tasks needing action")
        logger.info(f"Found {len(pending_approval_files)} tasks pending approval")

        return needs_action_files, pending_approval_files

    def process_tasks(self):
        """Process tasks in the needs_action directory"""
        needs_action_files, pending_approval_files = self.check_for_tasks()

        for task_file in needs_action_files:
            logger.info(f"Processing task: {task_file.name}")
            self.handle_task(task_file)

    def handle_task(self, task_file):
        """Handle a specific task file"""
        # This would normally call Claude Code to process the task
        # For now, we'll just log the action
        logger.info(f"Task {task_file.name} would be processed by Claude Code")

        # Update dashboard to reflect activity
        self.update_dashboard(f"Started processing {task_file.name}")

    def update_dashboard(self, message):
        """Update the dashboard with current status"""
        dashboard_path = self.vault_path / 'Dashboard.md'
        current_content = dashboard_path.read_text()

        # Find the recent activity section and add the new message
        lines = current_content.split('\n')
        new_lines = []
        activity_section_found = False

        for line in lines:
            if line.startswith('## Recent Activity'):
                activity_section_found = True
                new_lines.append(line)
                new_lines.append(f'- {time.strftime("%H:%M")} - {message}')
            elif activity_section_found and line.startswith('## ') and not line.startswith('## Recent Activity'):
                # End of activity section, add back the current line
                activity_section_found = False
                new_lines.append(line)
            elif activity_section_found and line.startswith('- No recent activity'):
                # Replace "No recent activity" with the new message
                new_lines.append(f'- {time.strftime("%H:%M")} - {message}')
                activity_section_found = False
            else:
                new_lines.append(line)

        # Write the updated content back
        dashboard_path.write_text('\n'.join(new_lines))

    def run(self):
        """Run the orchestrator continuously"""
        logger.info("AI Employee Orchestrator started")

        while True:
            try:
                self.process_tasks()
                time.sleep(30)  # Check every 30 seconds
            except KeyboardInterrupt:
                logger.info("Orchestrator stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in orchestrator: {e}")
                time.sleep(60)  # Wait a minute before retrying

def main():
    vault_path = Path(__file__).parent
    orchestrator = AI_Employee_Orchestrator(str(vault_path))

    logger.info("Starting AI Employee Orchestrator")
    logger.info(f"Monitoring vault at: {vault_path}")

    orchestrator.run()

if __name__ == "__main__":
    main()