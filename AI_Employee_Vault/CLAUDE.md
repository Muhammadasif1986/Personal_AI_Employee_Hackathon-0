# Claude Code Configuration for AI Employee Project
# This file helps Claude understand the project structure and purpose

## Project Overview
The AI Employee project is a Personal AI Employee Hackathon project (Hackathon 0)
that implements an autonomous Full-Time Equivalent (FTE) agent using Claude Code
and Obsidian as the knowledge base.

## Key Directories
- AI_Employee_Vault/: Main Obsidian vault
  - Dashboard.md: Real-time summary of business metrics
  - Company_Handbook.md: Rules of engagement and preferences
  - Inbox/: Files dropped for processing
  - Needs_Action/: Action items for the AI to process
  - Plans/: Generated plans for complex tasks
  - Done/: Completed tasks
  - Pending_Approval/: Items requiring human approval

- Skills/: Agent Skills implementations

## Main Scripts
- simple_file_monitor.py: Monitors Inbox for new files
- orchestrator.py: Main orchestrator that coordinates AI actions
- filesystem_watcher.py: Alternative file watching implementation

## Working with the AI Employee
1. Place files in the Inbox directory to trigger processing
2. The file monitor creates action items in Needs_Action
3. The orchestrator coordinates Claude Code to process tasks
4. Results are placed in appropriate directories and Dashboard is updated

## Human-in-the-Loop
For sensitive actions, approval files are created in Pending_Approval
Move these to the appropriate directory to approve or reject actions.

## Agent Skills
All AI functionality should be implemented as Agent Skills as specified
in the hackathon requirements.