#!/usr/bin/env python3
"""
Ralph Wiggum Loop - Implements persistent reasoning loops for autonomous task completion
Based on the "ralph-wiggum" pattern described in the hackathon document
"""
import time
import logging
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import json
import asyncio


class RalphWiggumLoop:
    def __init__(self, vault_path: str = "./AI_Employee_Vault", max_iterations: int = 10):
        self.vault_path = Path(vault_path)
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.done_dir = self.vault_path / "Done"
        self.pending_approval_dir = self.vault_path / "Pending_Approval"
        self.max_iterations = max_iterations

        # Set up logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info("Ralph Wiggum Loop initialized")

    def check_completion_condition(self, task_file_path: Path) -> bool:
        """
        Check if a task is complete by seeing if it has been moved to Done directory
        """
        task_name = task_file_path.stem
        done_task = self.done_dir / f"{task_name}.md"

        # Check if the task file has been moved to Done
        if done_task.exists():
            return True

        # Check if the task file has been moved to Pending_Approval (partial completion)
        pending_task = self.pending_approval_dir / f"{task_name}.md"
        if pending_task.exists():
            return True

        return False

    def run_task_loop(self, task_file_path: Path, process_function: Callable[[Path], bool]):
        """
        Run the Ralph Wiggum loop for a specific task
        """
        self.logger.info(f"Starting Ralph Wiggum loop for task: {task_file_path.name}")

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            self.logger.info(f"Iteration {iteration} for task: {task_file_path.name}")

            try:
                # Process the task
                result = process_function(task_file_path)

                # Check if the task is complete
                if self.check_completion_condition(task_file_path):
                    self.logger.info(f"Task {task_file_path.name} is complete at iteration {iteration}")
                    return True

                # If process function returned True, the task might be complete
                if result:
                    if self.check_completion_condition(task_file_path):
                        self.logger.info(f"Task {task_file_path.name} is complete at iteration {iteration}")
                        return True

                # Wait a bit before the next iteration
                time.sleep(2)

            except Exception as e:
                self.logger.error(f"Error in iteration {iteration} for task {task_file_path.name}: {e}")
                if iteration >= self.max_iterations:
                    self.logger.error(f"Max iterations reached for task {task_file_path.name}")
                    return False

        self.logger.warning(f"Max iterations ({self.max_iterations}) reached for task {task_file_path.name}")
        return False

    async def run_async_task_loop(self, task_file_path: Path, process_function: Callable[[Path], Any]):
        """
        Async version of the Ralph Wiggum loop
        """
        self.logger.info(f"Starting async Ralph Wiggum loop for task: {task_file_path.name}")

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            self.logger.info(f"Async iteration {iteration} for task: {task_file_path.name}")

            try:
                # Process the task (async)
                result = await process_function(task_file_path)

                # Check if the task is complete
                if self.check_completion_condition(task_file_path):
                    self.logger.info(f"Task {task_file_path.name} is complete at iteration {iteration}")
                    return True

                # If process function returned True, the task might be complete
                if result:
                    if self.check_completion_condition(task_file_path):
                        self.logger.info(f"Task {task_file_path.name} is complete at iteration {iteration}")
                        return True

                # Wait a bit before the next iteration
                await asyncio.sleep(2)

            except Exception as e:
                self.logger.error(f"Error in async iteration {iteration} for task {task_file_path.name}: {e}")
                if iteration >= self.max_iterations:
                    self.logger.error(f"Max iterations reached for task {task_file_path.name}")
                    return False

        self.logger.warning(f"Max iterations ({self.max_iterations}) reached for task {task_file_path.name}")
        return False

    def process_needs_action_items(self, max_tasks: int = 5):
        """
        Process all items in Needs_Action using Ralph Wiggum loops
        """
        task_files = list(self.needs_action_dir.glob("*.md"))[:max_tasks]

        if not task_files:
            self.logger.info("No tasks in Needs_Action directory")
            return

        self.logger.info(f"Processing {len(task_files)} tasks from Needs_Action")

        for task_file in task_files:
            # For this implementation, we'll create a simple processing function
            def simple_task_processor(task_path: Path) -> bool:
                content = task_path.read_text()
                # Check if the task contains any completion indicators
                if "[x]" in content or "COMPLETED" in content.upper():
                    # Move the task to Done directory
                    done_path = self.done_dir / task_path.name
                    task_path.rename(done_path)
                    return True
                return False

            # Run the Ralph Wiggum loop for this task
            result = self.run_task_loop(task_file, simple_task_processor)
            self.logger.info(f"Task {task_file.name} processed: {'Success' if result else 'Incomplete'}")

    def create_persistent_task(self, task_description: str, goal: str) -> Path:
        """
        Create a persistent task that requires continuous effort until goal is reached
        """
        task_id = f"PERSISTENT_TASK_{int(time.time())}"
        content = f"""---
type: persistent_task
task_id: {task_id}
created: {time.strftime('%Y-%m-%d %H:%M:%S')}
status: active
ralph_wiggum_loop: True
max_iterations: {self.max_iterations}
---

# Persistent Task: {task_description}

## Goal
{goal}

## Current Status
- [ ] Task initialization
- [ ] First attempt
- [ ] Validation
- [ ] Completion check

## Instructions for Claude
Process this task using a Ralph Wiggum loop. Continue working until the goal is achieved.
When complete, move this file to the Done folder or create an approval request in Pending_Approval if needed.

## Completion Criteria
- [ ] Goal has been met: {goal}
- [ ] Appropriate follow-up actions taken
- [ ] Task file moved to correct location
"""

        task_path = self.needs_action_dir / f"{task_id}.md"
        task_path.write_text(content)

        self.logger.info(f"Created persistent task: {task_path.name}")
        return task_path


# Example processing functions for different types of tasks
def process_email_task(task_path: Path) -> bool:
    """Example processor for email-related tasks"""
    content = task_path.read_text()

    # Simulate email processing
    if "send" in content.lower() and "email" in content.lower():
        # In a real implementation, this would call the email MCP server
        print(f"Processing email task: {task_path.name}")

        # Simulate email being processed
        if "APPROVED" in content.upper():
            # Move to Done if approved
            done_path = Path(str(task_path).replace("Needs_Action", "Done"))
            task_path.rename(done_path)
            return True

    return False


def process_approval_task(task_path: Path) -> bool:
    """Example processor for approval-related tasks"""
    content = task_path.read_text()

    # Check if the task has been approved (moved to Pending_Approval directory)
    pending_approval_dir = task_path.parent.parent / "Pending_Approval"
    if pending_approval_dir.exists():
        import shutil
        approval_check = pending_approval_dir / task_path.name
        if approval_check.exists():
            # If approval file exists in Pending_Approval, task is considered in progress
            # and may need further action
            approved_file = approval_check
            if approved_file.exists():
                # In a real system, this would check if it's been moved to Approved
                approved_dir = task_path.parent.parent / "Approved"
                if approved_dir.exists():
                    approved_check = approved_dir / task_path.name
                    if approved_check.exists():
                        # Move original task to Done
                        done_path = task_path.parent.parent / "Done" / task_path.name
                        if task_path.exists():
                            task_path.rename(done_path)
                        return True

    return False


# Example usage
if __name__ == "__main__":
    print("Ralph Wiggum Loop - Testing autonomous task completion")
    print("This demonstrates the persistent reasoning loop for multi-step task completion")

    # Example 1: Create a Ralph Wiggum loop instance
    ralph_loop = RalphWiggumLoop()

    # Example 2: Process items in Needs_Action
    print("\nProcessing tasks in Needs_Action directory...")
    ralph_loop.process_needs_action_items()

    # Example 3: Create a persistent task
    print("\nCreating a persistent task example...")
    persistent_task = ralph_loop.create_persistent_task(
        "Weekly Business Report Generation",
        "Generate and send weekly business report to stakeholders"
    )

    print(f"Created persistent task: {persistent_task}")
    print("\nRalph Wiggum loop is ready to handle persistent tasks!")
    print("The loop will continue until tasks are moved to Done or max iterations reached.")