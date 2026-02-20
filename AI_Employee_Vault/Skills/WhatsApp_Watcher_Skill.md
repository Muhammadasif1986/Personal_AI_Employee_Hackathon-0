# WhatsApp Watcher Skill

## Description
This skill enables the AI Employee to monitor WhatsApp for business-related messages using Playwright for web automation.

## Purpose
- Monitor WhatsApp for business communications
- Identify urgent messages based on keywords
- Create action items for processing
- Respond to common business inquiries

## Input
- WhatsApp Web session
- Keyword list for identifying important messages
- Business hours configuration

## Process
1. Maintain WhatsApp Web session
2. Monitor for unread messages
3. Check messages for business-related keywords
4. Create action files in Needs_Action directory
5. Log monitoring activity
6. Flag urgent messages for immediate attention

## Requirements
- WhatsApp Web session
- Playwright for browser automation
- Compliance with WhatsApp's terms of service
- Proper session management

## Output
- Action files created in Needs_Action directory
- Monitoring logs
- Updated dashboard with message activity