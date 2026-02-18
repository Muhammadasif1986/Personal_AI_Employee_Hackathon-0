# filesystem_watcher.py
import time
import logging
from pathlib import Path
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'
        self.inbox = Path(vault_path) / 'Inbox'
        self.done = Path(vault_path) / 'Done'

    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        logger.info(f"New file detected: {source.name}")

        # Create metadata file in Needs_Action
        dest = self.needs_action / f'FILE_{source.name}.md'

        # Create metadata for the file
        meta_content = f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}
---

New file dropped for processing: {source.name}
'''
        dest.write_text(meta_content)
        logger.info(f"Created action file: {dest}")

        # Copy the original file to Inbox for processing
        inbox_dest = self.inbox / source.name
        shutil.copy2(source, inbox_dest)
        logger.info(f"File copied to inbox: {inbox_dest}")

def main():
    vault_path = Path(__file__).parent / "AI_Employee_Vault"
    event_handler = DropFolderHandler(str(vault_path))
    observer = Observer()
    observer.schedule(event_handler, str(vault_path / "Inbox"), recursive=False)

    logger.info(f"Starting file system watcher for {vault_path}/Inbox")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("File system watcher stopped")

    observer.join()

if __name__ == "__main__":
    main()