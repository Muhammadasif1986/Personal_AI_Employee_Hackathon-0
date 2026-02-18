# Dashboard Updater Skill

## Description
This Agent Skill updates the Dashboard.md file with current status information, recent activities, and business metrics. It reads the current dashboard, updates relevant sections, and writes the updated content back.

## Functionality
- Reads the current Dashboard.md file
- Updates business metrics based on recent activity
- Adds new activities to the Recent Activity section
- Updates task counts and completion status
- Maintains proper formatting and structure

## Parameters
- `activity_message`: A message to add to the Recent Activity section
- `update_metrics`: Whether to recalculate business metrics (default: true)
- `dashboard_path`: Path to the dashboard file (default: Dashboard.md)

## Example Usage
When a task is completed, this skill is called to update the dashboard:
```
Activity: "Invoice sent to Client A ($1,250)"
Updates the dashboard with the new activity and recalculates metrics.
```

## Implementation Details
The skill should:
1. Read the current Dashboard.md content
2. Parse the content to identify sections that need updates
3. Update the Recent Activity section with new entries
4. Recalculate metrics based on directory contents (e.g., count files in Done vs Needs_Action)
5. Preserve other sections of the dashboard
6. Write the updated content back to the file

This helps maintain real-time visibility into AI employee activities and business status.