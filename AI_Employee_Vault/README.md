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

## Setup
1. Make sure Claude Code is installed and available in your PATH
2. Ensure Node.js is installed (v24+ LTS recommended)
3. Python 3.10+ is required
4. Run the orchestrator: `python orchestrator.py`

## Running the AI Employee
1. Start the file monitor: `python simple_file_monitor.py`
2. Start the orchestrator: `python orchestrator.py`
3. Place files in the Inbox directory to trigger processing
4. Monitor the Dashboard.md for updates

## Tier Progression
- ✅ Bronze: Foundation (completed)
- 🔜 Silver: Functional Assistant
- 🔜 Gold: Autonomous Employee
- 🔜 Platinum: Always-On Cloud + Local Executive