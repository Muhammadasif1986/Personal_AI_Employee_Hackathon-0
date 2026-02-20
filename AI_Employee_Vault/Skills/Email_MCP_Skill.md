# Email MCP Skill

## Description
This skill enables the AI Employee to send emails through an MCP (Model Context Protocol) server, providing a secure interface between Claude Code and email services.

## Purpose
- Send emails through MCP interface
- Maintain security by isolating credentials
- Provide dry-run capabilities for testing
- Enable Claude to send emails without direct access to credentials

## Input
- Recipient email address
- Email subject
- Email body content
- Optional CC and BCC recipients

## Process
1. Receive email request from Claude through MCP
2. Validate email parameters
3. Format email with proper headers
4. Connect to SMTP server using credentials
5. Send email to specified recipients
6. Return success or error status
7. Log email activity

## Requirements
- Valid SMTP credentials
- MCP server configuration
- Proper error handling
- Dry-run capability for testing

## Output
- Sent email to specified recipients
- Success or error status returned to Claude
- Email activity logs
- Updated dashboard with email activity