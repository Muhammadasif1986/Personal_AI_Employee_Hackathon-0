#!/usr/bin/env python3
"""
LinkedIn Poster - Automatically posts business updates to LinkedIn
"""
import time
import logging
from pathlib import Path
from datetime import datetime
import os
import requests
import json


class LinkedInPoster:
    def __init__(self, vault_path: str, access_token: str = None):
        self.vault_path = Path(vault_path)
        self.plans_dir = self.vault_path / 'Plans'
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.api_url = "https://api.linkedin.com/v2/ugcPosts"
        self.logger = logging.getLogger(self.__class__.__name__)

        # Ensure Plans directory exists
        self.plans_dir.mkdir(parents=True, exist_ok=True)

        # Check if we have valid access token
        if not self.access_token:
            self.logger.warning("No LinkedIn access token provided. Will operate in dry-run mode.")
            self.dry_run = True
        else:
            self.dry_run = False

        self.logger.info("LinkedIn Poster initialized")

    def check_for_posts(self):
        """Check for planned LinkedIn posts in Plans directory"""
        # Look for post plan files
        post_plans = list(self.plans_dir.glob("LINKEDIN_POST_*.md"))
        return post_plans

    def post_to_linkedin(self, content: str, visibility: str = "PUBLIC") -> bool:
        """Post content to LinkedIn"""
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post to LinkedIn: {content[:100]}...")
            return True

        # LinkedIn UGC Post API request format
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        # Create the post payload
        post_data = {
            "author": f"urn:li:person:{os.getenv('LINKEDIN_PERSON_URN')}",  # This should be your LinkedIn person URN
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=post_data)
            if response.status_code == 201:
                self.logger.info("Successfully posted to LinkedIn")
                return True
            else:
                self.logger.error(f"Failed to post to LinkedIn: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error posting to LinkedIn: {e}")
            return False

    def process_post_plan(self, plan_file: Path):
        """Process a LinkedIn post plan file"""
        content = plan_file.read_text()

        # Extract content to post (this is a simple approach)
        lines = content.split('\n')
        post_content = ""
        capture_content = False

        for line in lines:
            if '## Post Content' in line:
                capture_content = True
                continue
            if capture_content and line.startswith('#'):
                break  # End of content section
            if capture_content:
                post_content += line + '\n'

        if post_content.strip():
            success = self.post_to_linkedin(post_content.strip())
            if success:
                # Move to done
                done_dir = self.vault_path / 'Done'
                done_dir.mkdir(exist_ok=True)
                new_path = done_dir / plan_file.name
                plan_file.rename(new_path)
                self.logger.info(f"Posted LinkedIn update and moved plan to Done: {plan_file.name}")
                return True

        return False

    def run(self):
        """Run the LinkedIn posting loop"""
        self.logger.info("Starting LinkedIn Poster...")
        while True:
            try:
                post_plans = self.check_for_posts()
                for plan_file in post_plans:
                    self.process_post_plan(plan_file)
            except Exception as e:
                self.logger.error(f'Error in LinkedIn Poster: {e}')

            # Check every 10 minutes for new post plans
            time.sleep(600)


if __name__ == "__main__":
    # Initialize with vault path
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    poster = LinkedInPoster(vault_path)

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    print("Starting LinkedIn Poster...")
    poster.run()