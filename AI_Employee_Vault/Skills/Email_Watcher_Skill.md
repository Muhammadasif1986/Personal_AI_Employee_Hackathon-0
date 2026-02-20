# Email Watcher Skill

## Description
This skill enables the AI Employee to monitor Gmail for new emails and create appropriate action files.

## Purpose
- Monitor Gmail for new messages
- Identify urgent or important emails
- Create action items for processing
- Flag important communications

## Input
- Gmail credentials
- Filter criteria (important, urgent, specific senders)

## Process
1. Connect to Gmail using API credentials
2. Check for unread messages matching criteria
3. Create action files in Needs_Action directory
4. Track processed message IDs to avoid duplicates
5. Log monitoring activity

## Requirements
- Valid Gmail API credentials
- OAuth 2.0 setup
- Appropriate permissions

## Output
- Action files created in Needs_Action directory
- Monitoring logs
- Updated dashboard with email activity