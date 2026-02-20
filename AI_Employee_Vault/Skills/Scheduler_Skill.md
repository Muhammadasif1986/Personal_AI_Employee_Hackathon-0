# Scheduler Skill

## Description
This skill enables the AI Employee to schedule and execute recurring tasks using a cron-like scheduling system.

## Purpose
- Schedule regular business activities
- Execute automated tasks at specified intervals
- Manage recurring business processes
- Create scheduled action items

## Input
- Schedule definition (cron format)
- Task type and parameters
- Execution context and environment

## Process
1. Parse schedule definition in cron format
2. Determine next execution time
3. Execute scheduled task when due
4. Create action files for complex tasks
5. Log scheduling activity
6. Update dashboard with scheduled activity

## Requirements
- croniter library for cron parsing
- Proper task execution environment
- Error handling and logging

## Output
- Executed scheduled tasks
- Action files created in Needs_Action directory when appropriate
- Scheduling logs
- Updated dashboard with scheduled activity status