# Handbook Reader Skill

## Description
This Agent Skill reads and interprets the Company_Handbook.md file to understand business rules, preferences, and guidelines that should guide the AI Employee's behavior. This ensures consistent and rule-adherent operation.

## Functionality
- Reads the Company_Handbook.md file
- Parses business rules and guidelines
- Applies rules to current decision-making
- Updates behavior based on handbook changes
- Identifies when to request approval vs. act autonomously

## Parameters
- `handbook_path`: Path to the company handbook file (default: Company_Handbook.md)
- `section_filter`: Specific section to read (optional)
- `update_rules`: Whether to apply updated rules to current processing (default: true)

## Example Usage
Before processing an email from a new contact, check the handbook:
```
handbook_path: "Company_Handbook.md"
section_filter: "Communication Guidelines"
```

## Implementation Details
The skill should:
1. Parse the Company_Handbook.md file
2. Extract relevant rules for the current context
3. Apply rules to decision-making process
4. Maintain consistency with established preferences
5. Flag situations where handbook doesn't provide clear guidance
6. Suggest handbook updates when encountering edge cases

This skill ensures the AI Employee follows consistent business practices and maintains the user's preferred operational style.