# Approval Handler Skill

## Description
This Agent Skill manages the human-in-the-loop approval workflow. It creates approval request files for sensitive actions and monitors for approved/rejected actions, implementing the critical safety mechanism for the AI Employee.

## Functionality
- Creates approval request files with proper metadata
- Monitors approval directories for user decisions
- Executes approved actions
- Logs rejected actions
- Implements proper security checks before executing

## Parameters
- `action_type`: Type of action requiring approval (payment, email, etc.)
- `action_details`: Specific details about the action to approve
- `approval_threshold`: Action value limit before requiring approval
- `request_file_path`: Where to create the approval request

## Example Usage
When a payment over $100 is detected, create an approval request:
```
action_type: "payment"
action_details: {amount: 500.00, recipient: "Client A", reason: "Invoice #123"}
request_file_path: "/Pending_Approval/PAYMENT_ClientA_20260217.md"
```

## Implementation Details
The skill should:
1. Check if action exceeds approval thresholds from Company_Handbook.md
2. Create standardized approval request file with all necessary details
3. Monitor Pending_Approval directory for user movements
4. Execute approved actions via appropriate MCP servers
5. Log all approval activities for audit trail
6. Never auto-approve sensitive actions

This skill implements the critical safety mechanism that prevents unauthorized actions while maintaining efficiency for safe operations.