# File Movement Skill

## Description
This Agent Skill handles the movement of files between different directories in the vault system (Inbox, Needs_Action, Plans, Done, Pending_Approval). It implements the file-based workflow that enables the human-in-the-loop approval process.

## Functionality
- Moves files between designated directories
- Logs file movements for audit purposes
- Ensures proper file handling during status changes
- Prevents duplicate processing by moving files atomically

## Parameters
- `source_file`: Path to the file to move
- `destination_directory`: Target directory for the file
- `create_backup`: Whether to create a backup before moving (default: false)
- `log_movement`: Whether to log the movement action (default: true)

## Example Usage
When a task is completed, move it from Needs_Action to Done:
```
source_file: /Needs_Action/EMAIL_client_invoice_request.md
destination_directory: /Done/
```

## Implementation Details
The skill should:
1. Verify the source file exists
2. Verify the destination directory exists
3. Move the file atomically
4. Log the movement in appropriate logs
5. Update dashboard if needed
6. Handle errors gracefully (e.g., if destination is locked)

This skill is critical for the workflow management system that ensures each task moves through the proper stages from discovery to completion.