#!/usr/bin/env python3
"""
Scheduler - Basic task scheduler for the AI Employee
"""
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
import json
import os
import subprocess
import sys
from typing import Dict, Any, List
from threading import Thread


class TaskScheduler:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.tasks_dir = self.vault_path / 'Tasks'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_dir = self.vault_path / 'Plans'
        self.scheduled = self.vault_path / 'Scheduled'
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create directories if they don't exist
        for dir_path in [self.tasks_dir, self.needs_action, self.plans_dir, self.scheduled]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Task storage
        self.scheduled_tasks_file = self.vault_path / 'scheduled_tasks.json'
        self.scheduled_tasks = self._load_scheduled_tasks()

        # Set up logging
        handler = logging.FileHandler(self.vault_path / 'scheduler.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _load_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Load scheduled tasks from file"""
        if self.scheduled_tasks_file.exists():
            try:
                content = self.scheduled_tasks_file.read_text()
                return json.loads(content)
            except:
                return []
        return []

    def _save_scheduled_tasks(self):
        """Save scheduled tasks to file"""
        self.scheduled_tasks_file.write_text(json.dumps(self.scheduled_tasks, indent=2))

    def _is_time_to_run(self, task: Dict[str, Any]) -> bool:
        """Simple time-based scheduler - check if current time matches schedule"""
        if not task['enabled']:
            return False

        now = datetime.now()
        task_schedule = task.get('schedule', '*/5 * * * *')  # Default: every 5 minutes

        # For a simple implementation, we'll just check if it's been enough time
        # In a real implementation, we would parse cron expressions using croniter
        last_run = None
        if task.get('last_run'):
            last_run = datetime.fromisoformat(task['last_run'])

        # Simple check: if schedule is like "*/30" meaning every 30 minutes, etc.
        if task_schedule.startswith('*/'):
            interval = int(task_schedule.split('/')[1].split()[0])
            if not last_run or (now - last_run).total_seconds() >= interval * 60:
                return True
        else:
            # If not a simple interval schedule, just run once every 5 minutes for demo
            if not last_run or (now - last_run).total_seconds() >= 300:  # 5 minutes
                return True

        return False

    def run_task(self, task: Dict[str, Any]):
        """Execute a scheduled task"""
        try:
            task_type = task['type']
            details = task['details']

            self.logger.info(f"Running scheduled task: {task['name']}")

            if task_type == 'create_file':
                # Create a file in Needs_Action directory
                filename = f"SCHEDULED_{task['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                filepath = self.needs_action / filename

                content = f"""---
type: scheduled_task
task_id: {task['id']}
created: {datetime.now().isoformat()}
---

# Scheduled Task: {task['name']}

## Description
{details.get('description', 'No description provided')}

## Action Required
{details.get('action_required', 'Process this scheduled task')}

## Notes
This task was automatically created by the scheduler.
"""
                filepath.write_text(content)

            elif task_type == 'run_script':
                # Run an external script
                script_path = details.get('script_path')
                if script_path and Path(script_path).exists():
                    result = subprocess.run(['python', script_path], capture_output=True, text=True)
                    if result.returncode != 0:
                        self.logger.error(f"Script {script_path} failed: {result.stderr}")
                    else:
                        self.logger.info(f"Script {script_path} completed successfully")

            elif task_type == 'post_to_linkedin':
                # Create a LinkedIn post plan
                from linkedin_poster import LinkedInPoster

                filename = f"LINKEDIN_POST_{task['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                filepath = self.plans_dir / filename

                content = f"""---
type: scheduled_linkedin_post
task_id: {task['id']}
created: {datetime.now().isoformat()}
---

# LinkedIn Post Plan: {task['name']}

## Post Content
{details.get('content', 'Scheduled LinkedIn post')}

## Target Audience
{details.get('audience', 'General')}

## Hashtags
{details.get('hashtags', '')}
"""
                filepath.write_text(content)

            elif task_type == 'send_email':
                # Create an email approval request
                from approval_handler import ApprovalHandler
                approval_handler = ApprovalHandler(str(self.vault_path))

                details_for_approval = {
                    'to': details.get('to'),
                    'subject': details.get('subject'),
                    'body': details.get('body'),
                    'type': 'email'
                }

                approval_handler.create_approval_request(
                    action_type='email',
                    details=details_for_approval,
                    reason='Scheduled email task'
                )

            # Update task's last run time
            task['last_run'] = datetime.now().isoformat()
            self._save_scheduled_tasks()

            self.logger.info(f"Completed scheduled task: {task['name']}")

        except Exception as e:
            self.logger.error(f"Error running task {task['name']}: {e}")

    def run_scheduler(self):
        """Main scheduler loop"""
        self.logger.info("Starting Task Scheduler...")

        # Add some default tasks if none exist
        if not self.scheduled_tasks:
            self._add_default_tasks()

        while True:
            try:
                current_time = datetime.now()
                self.logger.debug(f"Checking scheduled tasks at {current_time}")

                for task in self.scheduled_tasks:
                    if self._is_time_to_run(task):
                        # Run task in separate thread to avoid blocking scheduler
                        thread = Thread(target=self.run_task, args=(task,))
                        thread.daemon = True
                        thread.start()

                # Sleep for 30 seconds before checking again
                time.sleep(30)

            except Exception as e:
                self.logger.error(f"Error in scheduler: {e}")
                time.sleep(60)  # Wait longer if there's an error

    def _add_default_tasks(self):
        """Add some default scheduled tasks"""
        # Daily business briefing
        self.scheduled_tasks.append({
            'id': f"task_{int(time.time())}_daily",
            'name': 'Daily Business Briefing',
            'schedule': '0 8 * * *',  # Every day at 8 AM - for demo we'll use simple interval
            'type': 'create_file',
            'details': {
                "description": "Generate daily business briefing",
                "action_required": "Create daily business summary and metrics report"
            },
            'enabled': True,
            'created': datetime.now().isoformat(),
            'last_run': None
        })

        # Weekly social media post
        self.scheduled_tasks.append({
            'id': f"task_{int(time.time())}_weekly",
            'name': 'Weekly LinkedIn Post',
            'schedule': '0 10 * * 1',  # Every Monday at 10 AM - for demo we'll use simple interval
            'type': 'post_to_linkedin',
            'details': {
                "content": "Weekly business update and insights from our team.",
                "audience": "Business professionals",
                "hashtags": "#business #insights #weeklyupdate"
            },
            'enabled': True,
            'created': datetime.now().isoformat(),
            'last_run': None
        })

        # Monthly financial review
        self.scheduled_tasks.append({
            'id': f"task_{int(time.time())}_monthly",
            'name': 'Monthly Financial Review',
            'schedule': '0 9 1 * *',  # First day of every month at 9 AM - for demo we'll use simple interval
            'type': 'create_file',
            'details': {
                "description": "Review monthly financials",
                "action_required": "Analyze financial performance and create summary report"
            },
            'enabled': True,
            'created': datetime.now().isoformat(),
            'last_run': None
        })

        self._save_scheduled_tasks()
        self.logger.info("Added default scheduled tasks")


if __name__ == "__main__":
    # Initialize with vault path
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    scheduler = TaskScheduler(vault_path)

    print("Starting Task Scheduler...")
    scheduler.run_scheduler()