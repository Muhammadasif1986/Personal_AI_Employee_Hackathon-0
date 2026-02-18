# simple_file_monitor.py
# Simple file monitoring script that checks for new files periodically
import time
import logging
from pathlib import Path
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleFileMonitor:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.processed_files = set()

        # Create directories if they don't exist
        self.inbox.mkdir(exist_ok=True)
        self.needs_action.mkdir(exist_ok=True)

    def check_for_new_files(self):
        """Check for new files in the inbox folder"""
        current_files = set(self.inbox.glob('*'))
        new_files = current_files - self.processed_files

        for file_path in new_files:
            if file_path.is_file():
                self.process_new_file(file_path)
                self.processed_files.add(file_path)

    def process_new_file(self, file_path):
        """Process a new file by creating an action item"""
        logger.info(f"Processing new file: {file_path.name}")

        # Create metadata file in Needs_Action
        action_file = self.needs_action / f'FILE_{file_path.stem}_{int(time.time())}.md'

        # Create metadata for the file
        meta_content = f'''---
type: file_drop
original_name: {file_path.name}
size: {file_path.stat().st_size}
timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}
status: pending
---

# New file for processing

File: {file_path.name}
Size: {file_path.stat().st_size} bytes
Detected: {time.strftime("%Y-%m-%d %H:%M:%S")}

## Action Required
- [ ] Review file content
- [ ] Determine appropriate response
- [ ] Process file as needed
- [ ] Move original to Done when complete
'''
        action_file.write_text(meta_content)
        logger.info(f"Created action file: {action_file}")

def main():
    vault_path = Path(__file__).parent
    monitor = SimpleFileMonitor(str(vault_path))

    logger.info(f"Starting simple file monitor for {vault_path}/Inbox")
    logger.info("Monitoring for new files every 10 seconds. Press Ctrl+C to stop.")

    try:
        while True:
            monitor.check_for_new_files()
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("File monitor stopped by user")

if __name__ == "__main__":
    main()