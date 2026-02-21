#!/usr/bin/env python3
"""
Audit Logger - Comprehensive audit logging for Gold Tier
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class AuditLogger:
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / "Logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # Create file handler for audit logs
        log_file_path = self.logs_dir / f"audit_{datetime.now().strftime('%Y-%m-%d')}.json"
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info("Audit Logger initialized")

    def log_action(self,
                   action_type: str,
                   actor: str,
                   target: str,
                   parameters: Dict[str, Any],
                   approval_status: str = "auto",
                   approved_by: str = "system",
                   result: str = "success"):
        """
        Log an action with comprehensive details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "parameters": parameters,
            "approval_status": approval_status,
            "approved_by": approved_by,
            "result": result,
            "session_id": os.getenv("AUDIT_SESSION_ID", "unknown")
        }

        # Write to daily log file
        log_file_path = self.logs_dir / f"audit_{datetime.now().strftime('%Y-%m-%d')}.json"

        # Read existing logs if file exists
        existing_logs = []
        if log_file_path.exists():
            try:
                with open(log_file_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        existing_logs = json.loads(content)
                        if not isinstance(existing_logs, list):
                            existing_logs = [existing_logs]
            except (json.JSONDecodeError, FileNotFoundError):
                existing_logs = []

        # Append new log entry
        existing_logs.append(log_entry)

        # Write back to file
        with open(log_file_path, 'w') as f:
            json.dump(existing_logs, f, indent=2)

        # Also log to standard logger
        self.logger.info(f"ACTION: {action_type} by {actor} on {target} - {result}")

        return log_entry

    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log an error with context"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {},
            "severity": "error"
        }

        # Write to error log file
        error_log_path = self.logs_dir / f"errors_{datetime.now().strftime('%Y-%m-%d')}.json"

        # Read existing error logs if file exists
        existing_errors = []
        if error_log_path.exists():
            try:
                with open(error_log_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        existing_errors = json.loads(content)
                        if not isinstance(existing_errors, list):
                            existing_errors = [existing_errors]
            except (json.JSONDecodeError, FileNotFoundError):
                existing_errors = []

        # Append new error entry
        existing_errors.append(log_entry)

        # Write back to file
        with open(error_log_path, 'w') as f:
            json.dump(existing_errors, f, indent=2)

        # Also log to standard logger
        self.logger.error(f"ERROR: {error_type} - {error_message}")

        return log_entry

    def get_audit_trail(self, start_date: str = None, end_date: str = None,
                       action_type: str = None, limit: int = 100) -> list:
        """Retrieve audit trail with optional filters"""
        logs = []

        # Get list of log files
        log_pattern = "audit_*.json"
        for log_file in self.logs_dir.glob(log_pattern):
            try:
                with open(log_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        file_logs = json.loads(content)
                        if not isinstance(file_logs, list):
                            file_logs = [file_logs]
                        logs.extend(file_logs)
            except (json.JSONDecodeError, FileNotFoundError):
                continue

        # Apply filters
        if start_date:
            logs = [log for log in logs if log['timestamp'] >= start_date]

        if end_date:
            logs = [log for log in logs if log['timestamp'] <= end_date]

        if action_type:
            logs = [log for log in logs if log['action_type'] == action_type]

        # Sort by timestamp (newest first) and limit
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return logs[:limit]

    def generate_audit_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate a comprehensive audit report"""
        logs = self.get_audit_trail(start_date=start_date, end_date=end_date)

        # Summary statistics
        total_actions = len(logs)
        action_types = {}
        actors = {}
        results = {}

        for log in logs:
            action_type = log['action_type']
            actor = log['actor']
            result = log['result']

            action_types[action_type] = action_types.get(action_type, 0) + 1
            actors[actor] = actors.get(actor, 0) + 1
            results[result] = results.get(result, 0) + 1

        report = {
            "report_date": datetime.now().isoformat(),
            "period": {"start": start_date, "end": end_date},
            "summary": {
                "total_actions": total_actions,
                "action_types": action_types,
                "actors": actors,
                "results": results
            },
            "recent_logs": logs[:10]  # Show last 10 logs
        }

        return report


# Example usage
if __name__ == "__main__":
    audit_logger = AuditLogger()

    # Example audit logs
    audit_logger.log_action(
        action_type="email_send",
        actor="claude_code",
        target="client@example.com",
        parameters={"subject": "Invoice #123", "body_length": 200},
        approval_status="approved",
        approved_by="human"
    )

    audit_logger.log_action(
        action_type="file_create",
        actor="filesystem_watcher",
        target="/Needs_Action/new_task.md",
        parameters={"file_size": 1500, "original_name": "urgent_request.txt"},
        result="success"
    )

    print("Audit logs created successfully")