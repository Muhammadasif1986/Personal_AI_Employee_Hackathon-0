# AI Employee - Digital FTE

This project implements a Personal AI Employee as part of the Hackathon 0: Building Autonomous FTEs in 2026.

## Overview
An autonomous AI employee that manages personal and business affairs 24/7 using Claude Code as the reasoning engine and Obsidian as the management dashboard.

## Architecture
- **The Brain**: Claude Code for reasoning and decision making
- **The Memory/GUI**: Obsidian (local Markdown) for knowledge management
- **The Senses**: Python watcher scripts monitoring various inputs
- **The Hands**: Model Context Protocol (MCP) servers for external actions

## Bronze Tier Features (Completed)
- Obsidian vault with Dashboard.md and Company_Handbook.md
- File system monitoring script (simple_file_monitor.py)
- Basic folder structure: /Inbox, /Needs_Action, /Done
- Claude Code integration via file system
- Agent Skills implementation started in Skills/ directory

## Silver Tier Features (Completed)
- **Multi-channel Watchers**: Gmail, WhatsApp and file system monitoring
- **LinkedIn Business Posting**: Automatic business updates and marketing content
- **Claude Reasoning Loop**: Creates Plan.md files for complex multi-step tasks
- **MCP Server Integration**: Email MCP server for external email actions
- **Human-in-the-Loop Approval**: Workflow for sensitive actions requiring approval
- **Task Scheduler**: Cron-like scheduling for recurring tasks
- **Integrated Orchestrator**: Manages all Silver Tier components

### Silver Tier Components:
- `email_watcher.py`: Monitors Gmail for new emails and creates action files
- `whatsapp_watcher.py`: Monitors WhatsApp for business-related messages
- `linkedin_poster.py`: Automatically posts business updates to LinkedIn
- `email_mcp_server.py`: MCP server for sending emails
- `advanced_orchestrator.py`: Implements Claude reasoning loops
- `approval_handler.py`: Manages approval workflows
- `scheduler.py`: Schedules recurring tasks
- Enhanced `orchestrator.py`: Integrates all Silver Tier components

## Setup
1. Make sure Claude Code is installed and available in your PATH
2. Ensure Node.js is installed (v24+ LTS recommended)
3. Python 3.10+ is required with additional packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables for external services (see Configuration section)
5. Run the integrated orchestrator: `python orchestrator.py`

## Configuration
Set up environment variables for external services:
- `EMAIL_ADDRESS`: Your email address for Gmail integration
- `EMAIL_PASSWORD`: App password for email (not regular password)
- `SMTP_SERVER`: SMTP server (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP port (default: 587)
- `LINKEDIN_ACCESS_TOKEN`: LinkedIn API access token
- `LINKEDIN_PERSON_URN`: Your LinkedIn person URN
- `WHATSAPP_SESSION_PATH`: Path for WhatsApp session storage
- `GMAIL_CREDENTIALS_PATH`: Path for Gmail API credentials

## Running the AI Employee
1. Start the integrated orchestrator: `python orchestrator.py`
2. The orchestrator automatically starts all Silver Tier components
3. Place files in the Inbox directory to trigger processing
4. Monitor the Dashboard.md for updates
5. Review pending approvals in Pending_Approval directory

## Tier Progression
- ✅ Bronze: Foundation (completed)
- ✅ Silver: Functional Assistant (completed)
- 🔜 Gold: Autonomous Employee
- 🔜 Platinum: Always-On Cloud + Local Executive

## Key Features in Practice

### Multi-Channel Monitoring
- Gmail Watcher checks for new emails and creates action items
- WhatsApp Watcher monitors business messages (requires WhatsApp Web session)
- File system watcher continues to monitor for dropped files

### LinkedIn Business Automation
- Scheduled weekly business updates
- Approval required for all posts
- Plan files created in /Plans before posting

### Human-in-the-Loop
- All payments require approval in Pending_Approval
- All LinkedIn posts require approval
- Email responses to new contacts require approval

### Scheduling
- Daily business briefings at 8 AM
- Weekly LinkedIn posts on Monday mornings
- Monthly financial reviews on first of month