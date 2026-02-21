# OpenRouter Integration for AI Employee

This document explains how to set up and test the AI Employee application using OpenRouter API instead of Claude/Anthropic APIs.

## Setup Instructions

### 1. Environment Configuration
Make sure your `.env` file contains the following:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct
```

### 2. Free Model Options
The following models are recommended for free usage:
- `meta-llama/llama-3.1-8b-instruct` - Free Llama model
- `mistralai/mistral-7b-instruct` - Free Mistral model
- `google/gemini-2.0-flash` - Low-cost Gemini model

## Testing the Application

### 1. Run the Basic Test
```bash
python3 test_openrouter.py
```

Expected output:
```
🎉 All tests passed! OpenRouter integration is working correctly.
```

### 2. Start the OpenRouter Orchestrator
```bash
python -m AI_Employee_Vault.openrouter_orchestrator
```

This will:
- Start the main orchestrator with OpenRouter AI reasoning
- Process files placed in the Inbox directory
- Generate plans and execute tasks using OpenRouter AI

### 3. Test the Platinum Tier with OpenRouter
```bash
git checkout platinum_tier
python -m AI_Employee_Vault.platinum_tier_orchestrator
```

This will start the complete Platinum Tier system with:
- Cloud Agent (24/7 operations)
- Local Agent (sensitive actions)
- Sync Manager (file-based communication)
- Health Monitor (system monitoring)

## File-Based Testing Workflow

### 1. Place Test Files in Inbox
Create files in `AI_Employee_Vault/Inbox/` with instructions:

**Example: `AI_Employee_Vault/Inbox/test_task.md`**
```markdown
---
priority: high
type: email
---

Please draft a professional response to the client's inquiry about our project timeline.

The client is concerned about the delivery date and needs a status update.
```

### 2. Monitor Processing
The system will:
- Move files from `Inbox/` to `Needs_Action/`
- Process files with OpenRouter AI reasoning
- Create plans in `Plans/` directory
- Execute tasks and move completed files to `Done/`

### 3. Check Dashboard
Monitor `AI_Employee_Vault/Dashboard.md` for real-time status updates.

### 4. Human Approval Workflow
For sensitive tasks:
- Files will appear in `Pending_Approval/` directory
- Move to `Approved/` to execute
- Move to `Rejected/` to discard

## Platinum Tier Demo Scenario

To test the Platinum Tier email scenario:

1. Place an email file in the Cloud Agent's needs action:
   `AI_Employee_Vault/Cloud_Agent/Needs_Action/EMAIL_CLIENT_URGENT_12345.md`

2. The Cloud Agent will:
   - Process the email while Local Agent is offline
   - Create draft reply in `Cloud_Agent/Drafts/`
   - Create approval request in `Cloud_Agent/Pending_Approval/`

3. When Local Agent returns:
   - Move approval file to `Approved/` to execute
   - System will send email via MCP server
   - Log and move to `Done/`

## Troubleshooting

### Common Issues:

1. **API Error 402 (Insufficient Credits)**:
   - Switch to a free model like `meta-llama/llama-3.1-8b-instruct`
   - Reduce max_tokens in API calls
   - Consider upgrading your OpenRouter account

2. **Model Not Found**:
   - Verify the model name is valid
   - Check OpenRouter documentation for current model list
   - Use `python -c "from AI_Employee_Vault.openrouter_config import OpenRouterAPI; print(OpenRouterAPI('your_key').list_models())"` to see available models

3. **File Permissions**:
   - Ensure the application has read/write access to the AI_Employee_Vault directory
   - Check that all subdirectories exist and are writable

### Testing Individual Components:

1. **Test OpenRouter connection only**:
   ```bash
   python3 test_openrouter.py
   ```

2. **Test simple orchestrator**:
   ```bash
   python -m AI_Employee_Vault.openrouter_orchestrator
   ```

3. **Check available models**:
   ```python
   from AI_Employee_Vault.openrouter_config import OpenRouterAPI
   import os
   api_key = os.getenv('OPENROUTER_API_KEY')
   client = OpenRouterAPI(api_key)
   models = client.list_models()
   for model in models['data'][:10]:  # Show first 10 models
       print(f"ID: {model['id']}, Name: {model.get('name', 'N/A')}")
   ```

## Security Note

- The OpenRouter API key is stored in `.env` and should never be committed to version control
- Sensitive operations still go through the Local Agent for security
- Vault sync excludes secret files to maintain security

## Next Steps

1. Place various test files in the Inbox to see how the AI processes them
2. Monitor the Dashboard for system status and metrics
3. Test the approval workflow for sensitive operations
4. Try the Platinum Tier architecture with both Cloud and Local agents