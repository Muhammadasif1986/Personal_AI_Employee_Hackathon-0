# Task Processor Skill

## Description
This Agent Skill processes task files found in the `/Needs_Action/` directory. It reads the task file, analyzes the content, determines the appropriate action, and creates a plan or takes direct action as appropriate.

## Functionality
- Reads task files from the Needs_Action directory
- Parses task metadata and content
- Determines appropriate response based on task type and Company Handbook rules
- Creates plan files or takes direct action
- Updates status and moves files appropriately

## Parameters
- `task_file_path`: Path to the task file to process
- `auto_approve`: Whether to auto-approve certain safe actions (default: false)

## Example Usage
When a task file like `EMAIL_urgent_client_request.md` is found in `/Needs_Action/`, this skill processes it according to the following logic:
1. Reads the file content and metadata
2. Checks Company_Handbook.md for handling rules
3. Determines if action can be taken autonomously or needs approval
4. Creates appropriate output (response, plan, or approval request)

## Implementation Details
This skill would typically be invoked by Claude Code when processing items in the Needs_Action directory. It should follow the pattern of reading the file, analyzing the content, and either:
- Taking direct action for low-risk items
- Creating a plan file in the Plans directory
- Creating an approval request in Pending_Approval for sensitive items