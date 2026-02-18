# Example Agent Skill - File Processor

This is an example of how Agent Skills can be implemented for the AI Employee. This particular skill processes files dropped in the inbox.

## Functionality
- Reads files from the Inbox directory
- Creates action items in Needs_Action
- Processes file content based on type
- Updates Dashboard with progress

## Implementation
The skill would typically be implemented as an MCP server that Claude can call to process files.

Example usage:
1. File dropped in `/Inbox/`
2. File monitor detects new file
3. Creates action item in `/Needs_Action/`
4. Claude processes the action item
5. Updates dashboard and moves to appropriate status

## Parameters
- file_path: Path to the file to process
- action_type: Type of action to perform (read, analyze, categorize, etc.)
- output_path: Where to place the processed result