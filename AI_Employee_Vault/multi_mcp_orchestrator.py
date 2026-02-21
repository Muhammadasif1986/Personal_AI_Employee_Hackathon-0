#!/usr/bin/env python3
"""
Multi-MCP Orchestrator - Orchestrates multiple Model Context Protocol servers
for Gold Tier requirements (Social media, accounting, etc.)
"""
import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os


@dataclass
class MCPService:
    name: str
    command: List[str]
    port: Optional[int] = None
    env_vars: Optional[Dict[str, str]] = None
    status: str = "stopped"
    process: Optional[Any] = None


class MultiMCPManager:
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.services_dir = self.vault_path / "MCP_Services"
        self.services_dir.mkdir(exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Define MCP services
        self.mcp_services: Dict[str, MCPService] = {}
        self._initialize_services()

        self.logger.info("Multi-MCP Manager initialized")

    def _initialize_services(self):
        """Initialize all MCP services for Gold Tier"""
        # Email MCP service (existing)
        self.mcp_services["email"] = MCPService(
            name="email",
            command=["python3", "email_mcp_server.py", "--mcp"],
            env_vars={
                "SMTP_SERVER": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
                "EMAIL_ADDRESS": os.getenv("EMAIL_ADDRESS"),
                "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD")
            }
        )

        # Placeholder for social media MCP services
        self.mcp_services["twitter"] = MCPService(
            name="twitter",
            command=["python3", "twitter_mcp_server.py", "--mcp"],
            env_vars={
                "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
                "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
                "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
                "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            }
        )

        self.mcp_services["facebook"] = MCPService(
            name="facebook",
            command=["python3", "facebook_mcp_server.py", "--mcp"],
            env_vars={
                "FACEBOOK_PAGE_ID": os.getenv("FACEBOOK_PAGE_ID"),
                "FACEBOOK_ACCESS_TOKEN": os.getenv("FACEBOOK_ACCESS_TOKEN")
            }
        )

        self.mcp_services["instagram"] = MCPService(
            name="instagram",
            command=["python3", "instagram_mcp_server.py", "--mcp"],
            env_vars={
                "INSTAGRAM_ACCOUNT_ID": os.getenv("INSTAGRAM_ACCOUNT_ID"),
                "INSTAGRAM_ACCESS_TOKEN": os.getenv("INSTAGRAM_ACCESS_TOKEN")
            }
        )

        # Placeholder for accounting/odoo MCP service
        self.mcp_services["odoo"] = MCPService(
            name="odoo",
            command=["python3", "odoo_mcp_server.py", "--mcp"],
            env_vars={
                "ODOO_URL": os.getenv("ODOO_URL", "http://localhost:8069"),
                "ODOO_DB": os.getenv("ODOO_DB", "odoo_db"),
                "ODOO_USERNAME": os.getenv("ODOO_USERNAME"),
                "ODOO_PASSWORD": os.getenv("ODOO_PASSWORD")
            }
        )

    def start_service(self, service_name: str) -> bool:
        """Start a specific MCP service"""
        if service_name not in self.mcp_services:
            self.logger.error(f"Service {service_name} not found")
            return False

        service = self.mcp_services[service_name]

        try:
            # Set up environment
            env = os.environ.copy()
            if service.env_vars:
                env.update(service.env_vars)

            # Change to the vault directory to find the MCP server files
            original_cwd = os.getcwd()
            os.chdir(self.vault_path)

            # Start the process
            service.process = subprocess.Popen(
                service.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )

            os.chdir(original_cwd)

            service.status = "running"
            self.logger.info(f"Started MCP service: {service_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start {service_name}: {e}")
            service.status = "error"
            return False

    def stop_service(self, service_name: str) -> bool:
        """Stop a specific MCP service"""
        if service_name not in self.mcp_services:
            self.logger.error(f"Service {service_name} not found")
            return False

        service = self.mcp_services[service_name]

        try:
            if service.process:
                service.process.terminate()
                service.process.wait(timeout=5)  # Wait up to 5 seconds
                service.process = None

            service.status = "stopped"
            self.logger.info(f"Stopped MCP service: {service_name}")
            return True

        except subprocess.TimeoutExpired:
            if service.process:
                service.process.kill()
                service.process = None
            service.status = "stopped"
            self.logger.warning(f"Force killed MCP service: {service_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping {service_name}: {e}")
            return False

    def start_all_services(self) -> Dict[str, bool]:
        """Start all MCP services"""
        results = {}
        for service_name in self.mcp_services:
            results[service_name] = self.start_service(service_name)
        return results

    def stop_all_services(self) -> Dict[str, bool]:
        """Stop all MCP services"""
        results = {}
        for service_name in self.mcp_services:
            results[service_name] = self.stop_service(service_name)
        return results

    def get_service_status(self) -> Dict[str, str]:
        """Get status of all services"""
        status = {}
        for name, service in self.mcp_services.items():
            if service.process:
                # Check if process is still alive
                if service.process.poll() is not None:
                    service.status = "stopped"
                else:
                    service.status = "running"
            status[name] = service.status
        return status

    def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check of all services"""
        status_report = {
            "timestamp": time.time(),
            "services": self.get_service_status(),
            "overall_status": "healthy",
            "issues": []
        }

        for name, status in status_report["services"].items():
            if status != "running":
                status_report["overall_status"] = "degraded"
                status_report["issues"].append(f"Service {name} is {status}")

        return status_report

    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""
        self.stop_service(service_name)
        time.sleep(1)  # Brief pause
        return self.start_service(service_name)

    def restart_all_services(self) -> Dict[str, bool]:
        """Restart all services"""
        results = {}
        for service_name in self.mcp_services:
            results[service_name] = self.restart_service(service_name)
        return results

    def send_mcp_request(self, service_name: str, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a request to a specific MCP service (simplified implementation)"""
        if service_name not in self.mcp_services:
            self.logger.error(f"Service {service_name} not found")
            return None

        # In a real implementation, this would communicate with the running MCP process
        # For now, we'll simulate the request
        self.logger.info(f"Simulating MCP request to {service_name}: {method} with params {params}")

        # Return a simulated response
        return {
            "success": True,
            "result": f"Simulated response from {service_name} for {method}",
            "request_id": time.time()
        }


class GoldTierOrchestrator:
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.mcp_manager = MultiMCPManager(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Initialize other Gold Tier components
        self.ralph_loop = None
        self.audit_logger = None

    def initialize_gold_tier_components(self):
        """Initialize all Gold Tier components"""
        self.logger.info("Initializing Gold Tier components...")

        # Start MCP services
        service_results = self.mcp_manager.start_all_services()
        self.logger.info(f"MCP Services started: {service_results}")

        # Initialize Ralph Wiggum loop
        try:
            from ralph_wiggum_loop import RalphWiggumLoop
            self.ralph_loop = RalphWiggumLoop(self.vault_path)
        except ImportError:
            self.logger.warning("Ralph Wiggum loop module not found")

        # Initialize audit logger
        try:
            from audit_logger import AuditLogger
            self.audit_logger = AuditLogger(self.vault_path)
        except ImportError:
            self.logger.warning("Audit logger module not found")

        self.logger.info("Gold Tier components initialized")

    def run_health_monitor(self, interval: int = 60):
        """Run continuous health monitoring"""
        self.logger.info(f"Starting health monitor (checking every {interval}s)")

        while True:
            try:
                health_status = self.mcp_manager.health_check()
                self.logger.info(f"Health check: {health_status['overall_status']}")

                if health_status['overall_status'] == 'degraded':
                    for issue in health_status['issues']:
                        self.logger.warning(f"Health issue: {issue}")

                        # Auto-restart failed services (simplified)
                        if 'Service' in issue and 'stopped' in issue:
                            service_name = issue.split()[1]
                            self.logger.info(f"Attempting to restart {service_name}")
                            self.mcp_manager.restart_service(service_name)

                time.sleep(interval)

            except KeyboardInterrupt:
                self.logger.info("Health monitor stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in health monitor: {e}")
                time.sleep(interval)

    def shutdown(self):
        """Gracefully shutdown all Gold Tier components"""
        self.logger.info("Shutting down Gold Tier components...")

        # Stop all MCP services
        results = self.mcp_manager.stop_all_services()
        self.logger.info(f"MCP Services stopped: {results}")

        self.logger.info("Gold Tier shutdown complete")


# Example usage
if __name__ == "__main__":
    print("Multi-MCP Orchestrator for Gold Tier")
    print("This orchestrates multiple Model Context Protocol servers")

    orchestrator = GoldTierOrchestrator()
    orchestrator.initialize_gold_tier_components()

    print("\nGold Tier components initialized successfully!")
    print("Services status:", orchestrator.mcp_manager.get_service_status())

    # Example: Send a request to a simulated service
    result = orchestrator.mcp_manager.send_mcp_request(
        "email",
        "send_email",
        {"to": "test@example.com", "subject": "Test", "body": "Test message"}
    )
    print("Simulated request result:", result)

    print("\nTo run the health monitor continuously, call orchestrator.run_health_monitor()")
    print("To shut down gracefully, call orchestrator.shutdown()")