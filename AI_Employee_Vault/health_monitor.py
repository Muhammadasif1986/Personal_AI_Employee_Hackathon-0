#!/usr/bin/env python3
"""
Health Monitor - Platinum Tier
Monitors the health and availability of Cloud and Local agents
"""
import time
import logging
import os
import subprocess
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Optional


class HealthMonitor:
    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # File handler for logging
        log_file_path = self.vault_path / 'health_monitor.log'
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Initialize directories if they don't exist
        dirs_to_create = [
            self.vault_path / 'Health_Monitor',
            self.vault_path / 'Notifications'
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.logger.info("Health Monitor initialized")

    def check_cloud_agent_health(self) -> Dict:
        """
        Check the health status of the cloud agent
        """
        try:
            health_file = self.vault_path / 'Health_Monitor' / 'cloud_agent_health.json'

            if health_file.exists():
                with open(health_file, 'r') as f:
                    health_data = json.load(f)

                # Check if the heartbeat is recent (within last 15 minutes)
                if 'timestamp' in health_data:
                    timestamp_str = health_data['timestamp']
                    # Convert ISO format timestamp to datetime
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    current_time = datetime.now()
                    time_diff = (current_time - timestamp).total_seconds()

                    if time_diff > 900:  # 15 minutes
                        health_data['status'] = 'offline'
                        health_data['last_seen'] = timestamp_str
                    else:
                        health_data['status'] = 'healthy'
                else:
                    health_data['status'] = 'unknown'

            else:
                # Check for heartbeat file as fallback
                heartbeat_file = self.vault_path / 'Cloud_Agent' / 'heartbeat.txt'
                if heartbeat_file.exists():
                    mod_time = heartbeat_file.stat().st_mtime
                    current_time = time.time()
                    if (current_time - mod_time) < 900:  # 15 minutes
                        health_data = {
                            'status': 'healthy',
                            'timestamp': datetime.fromtimestamp(mod_time).isoformat(),
                            'agent_type': 'cloud'
                        }
                    else:
                        health_data = {
                            'status': 'offline',
                            'timestamp': datetime.fromtimestamp(mod_time).isoformat(),
                            'agent_type': 'cloud'
                        }
                else:
                    health_data = {
                        'status': 'offline',
                        'timestamp': datetime.now().isoformat(),
                        'agent_type': 'cloud'
                    }

            return health_data

        except Exception as e:
            self.logger.error(f"Error checking cloud agent health: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'agent_type': 'cloud'
            }

    def check_local_agent_health(self) -> Dict:
        """
        Check the health status of the local agent
        """
        try:
            health_file = self.vault_path / 'Health_Monitor' / 'local_agent_health.json'

            if health_file.exists():
                with open(health_file, 'r') as f:
                    health_data = json.load(f)

                # Check if the heartbeat is recent (within last 15 minutes)
                if 'timestamp' in health_data:
                    timestamp_str = health_data['timestamp']
                    # Convert ISO format timestamp to datetime
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    current_time = datetime.now()
                    time_diff = (current_time - timestamp).total_seconds()

                    if time_diff > 900:  # 15 minutes
                        health_data['status'] = 'offline'
                        health_data['last_seen'] = timestamp_str
                    else:
                        health_data['status'] = 'healthy'
                else:
                    health_data['status'] = 'unknown'

            else:
                # Check for heartbeat file as fallback
                heartbeat_file = self.vault_path / 'Local_Agent' / 'heartbeat.txt'
                if heartbeat_file.exists():
                    mod_time = heartbeat_file.stat().st_mtime
                    current_time = time.time()
                    if (current_time - mod_time) < 900:  # 15 minutes
                        health_data = {
                            'status': 'healthy',
                            'timestamp': datetime.fromtimestamp(mod_time).isoformat(),
                            'agent_type': 'local'
                        }
                    else:
                        health_data = {
                            'status': 'offline',
                            'timestamp': datetime.fromtimestamp(mod_time).isoformat(),
                            'agent_type': 'local'
                        }
                else:
                    health_data = {
                        'status': 'offline',
                        'timestamp': datetime.now().isoformat(),
                        'agent_type': 'local'
                    }

            return health_data

        except Exception as e:
            self.logger.error(f"Error checking local agent health: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'agent_type': 'local'
            }

    def check_system_resources(self) -> Dict:
        """
        Check system resource usage
        """
        try:
            import psutil

            # Get system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent

            resources = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'status': 'ok'
            }

            # Check for resource issues
            if cpu_percent > 80:
                resources['status'] = 'warning'
                resources['cpu_warning'] = f'CPU usage high: {cpu_percent}%'
            if memory_percent > 85:
                resources['status'] = 'warning'
                resources['memory_warning'] = f'Memory usage high: {memory_percent}%'
            if disk_percent > 90:
                resources['status'] = 'warning'
                resources['disk_warning'] = f'Disk usage high: {disk_percent}%'

            return resources

        except ImportError:
            # psutil not available, return basic info
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'ok',
                'note': 'psutil not available, basic monitoring only'
            }
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def check_sync_status(self) -> Dict:
        """
        Check the synchronization status
        """
        try:
            sync_file = self.vault_path / 'Sync_Manager' / 'sync_status.json'
            vault_sync_file = self.vault_path / 'Sync_Manager' / 'vault_sync_status.json'

            sync_status = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'unknown',
                'last_sync': 'never',
                'conflicts': 0,
                'items_queued': 0
            }

            if sync_file.exists():
                with open(sync_file, 'r') as f:
                    file_data = json.load(f)
                    if 'last_sync' in file_data:
                        sync_status['last_sync'] = file_data['last_sync']
                    if 'status' in file_data:
                        sync_status['overall_status'] = file_data['status']

            if vault_sync_file.exists():
                with open(vault_sync_file, 'r') as f:
                    vault_data = json.load(f)
                    if 'conflicts' in vault_data:
                        sync_status['conflicts'] = len(vault_data['conflicts'])
                    if 'items_queued' in vault_data:
                        sync_status['items_queued'] += vault_data['items_queued']

            # Determine sync health based on age of last sync
            if sync_status['last_sync'] != 'never':
                try:
                    last_sync_time = datetime.fromisoformat(sync_status['last_sync'].replace('Z', '+00:00'))
                    time_diff = (datetime.now() - last_sync_time).total_seconds()
                    if time_diff > 1800:  # 30 minutes
                        sync_status['overall_status'] = 'degraded'
                except:
                    pass

            return sync_status

        except Exception as e:
            self.logger.error(f"Error checking sync status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def generate_health_report(self) -> Dict:
        """
        Generate a comprehensive health report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'report_type': 'health_report',
            'cloud_agent': self.check_cloud_agent_health(),
            'local_agent': self.check_local_agent_health(),
            'system_resources': self.check_system_resources(),
            'sync_status': self.check_sync_status(),
            'overall_status': 'unknown'
        }

        # Determine overall health based on individual components
        components = [
            report['cloud_agent']['status'],
            report['local_agent']['status'],
            report['system_resources']['status'],
            report['sync_status']['overall_status']
        ]

        if any(status == 'error' for status in components):
            report['overall_status'] = 'error'
        elif any(status in ['offline', 'warning', 'degraded'] for status in components):
            report['overall_status'] = 'degraded'
        else:
            report['overall_status'] = 'healthy'

        return report

    def send_alert(self, alert_type: str, message: str, severity: str = "medium"):
        """
        Send an alert for health issues
        """
        try:
            alert_content = f"""---
type: health_alert
severity: {severity}
timestamp: {datetime.now().isoformat()}
---

## Health Alert: {alert_type}

**Severity**: {severity.upper()}
**Time**: {datetime.now().isoformat()}

**Message**: {message}

---
**Alert generated by Health Monitor**
"""

            alert_filename = f"HEALTH_ALERT_{int(time.time())}_{alert_type.replace(' ', '_').lower()}.md"
            alert_path = self.vault_path / 'Notifications' / alert_filename
            alert_path.write_text(alert_content)

            self.logger.warning(f"Health alert generated: {alert_type} - {message}")

        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")

    def take_corrective_action(self, issue: Dict):
        """
        Take corrective actions for detected issues
        """
        try:
            if issue.get('status') == 'offline':
                # For now, just log the issue
                # In a real implementation, this might restart services
                agent_type = issue.get('agent_type', 'unknown')
                self.logger.info(f"Detected {agent_type} agent offline - potential restart needed")
                self.send_alert(
                    f"{agent_type.title()} Agent Offline",
                    f"The {agent_type} agent has gone offline. Please check the system.",
                    "high"
                )

            elif issue.get('status') == 'error':
                # Log and alert on errors
                error_msg = issue.get('error', 'Unknown error')
                agent_type = issue.get('agent_type', 'unknown')
                self.logger.error(f"Error in {agent_type} agent: {error_msg}")
                self.send_alert(
                    f"{agent_type.title()} Agent Error",
                    f"Error in {agent_type} agent: {error_msg}",
                    "high"
                )

        except Exception as e:
            self.logger.error(f"Error taking corrective action: {e}")

    def run(self):
        """Run the Health Monitor"""
        self.logger.info("Starting Health Monitor...")

        print("Starting Health Monitor...")
        print("Features Active:")
        print("- Cloud agent health monitoring")
        print("- Local agent health monitoring")
        print("- System resource monitoring")
        print("- Sync status monitoring")
        print("- Alert generation for issues")
        print("- Health report generation")
        print("\nHealth Monitor is now running!\n")

        # Main loop
        while True:
            try:
                report = self.generate_health_report()

                # Write the report to file
                report_filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                report_path = self.vault_path / 'Health_Monitor' / report_filename
                with open(report_path, 'w') as f:
                    json.dump(report, f, indent=2)

                # Write the latest report to a specific file for easy access
                latest_report_path = self.vault_path / 'Health_Monitor' / 'latest_health_report.json'
                with open(latest_report_path, 'w') as f:
                    json.dump(report, f, indent=2)

                # Check for issues and take corrective actions
                cloud_status = report['cloud_agent'].get('status', 'unknown')
                local_status = report['local_agent'].get('status', 'unknown')
                system_status = report['system_resources'].get('status', 'unknown')
                sync_status = report['sync_status'].get('overall_status', 'unknown')

                # Check for issues that require corrective action
                if cloud_status in ['offline', 'error']:
                    self.take_corrective_action(report['cloud_agent'])
                if local_status in ['offline', 'error']:
                    self.take_corrective_action(report['local_agent'])
                if system_status in ['error']:
                    self.send_alert(
                        "System Resource Error",
                        f"System resource monitoring error: {report['system_resources'].get('error', 'Unknown error')}",
                        "high"
                    )
                if sync_status in ['error']:
                    self.send_alert(
                        "Sync Error",
                        "Error in synchronization monitoring",
                        "medium"
                    )

                self.logger.info(f"Health check completed - Overall status: {report['overall_status']}")

                # Wait before checking again (5 minutes)
                time.sleep(300)

            except KeyboardInterrupt:
                self.logger.info("Shutting down Health Monitor...")
                break
            except Exception as e:
                self.logger.error(f"Error in Health Monitor: {e}")
                time.sleep(60)  # Wait longer on error


def main():
    # Set the vault path from environment or use default
    current_dir = Path.cwd()
    if current_dir.name == 'AI_Employee_Vault':
        vault_path = str(current_dir)  # Use current directory if we're already in the vault
    else:
        vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    # Create the health monitor and run it
    health_monitor = HealthMonitor(vault_path)

    print("=" * 50)
    print("PLATINUM TIER HEALTH MONITOR")
    print("24/7 Health & Status Monitoring System")
    print("=" * 50)
    print()
    print("Monitoring:")
    print("✅ Cloud Agent status and availability")
    print("✅ Local Agent status and availability")
    print("✅ System resources (CPU, Memory, Disk)")
    print("✅ Sync status between agents")
    print("✅ Health alert generation")
    print("✅ Corrective action triggers")
    print()
    print("Starting Health Monitor...")
    print()

    health_monitor.run()


if __name__ == "__main__":
    main()