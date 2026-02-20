#!/usr/bin/env python3
"""
Email MCP Server - Model Context Protocol server for sending emails
"""
import asyncio
import json
import smtplib
import logging
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Dict, Any


class EmailMCP:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Get email configuration from environment
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')

        if not self.email_address or not self.email_password:
            self.logger.warning("Email credentials not set. Server will operate in dry-run mode.")
            self.dry_run = True
        else:
            self.dry_run = False

    def send_email(self, to: str, subject: str, body: str, cc: str = None, bcc: str = None) -> Dict[str, Any]:
        """Send an email"""
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would send email to: {to}")
                self.logger.info(f"[DRY RUN] Subject: {subject}")
                self.logger.info(f"[DRY RUN] Body preview: {body[:100]}...")
                return {
                    "success": True,
                    "message": f"Would send email to {to}",
                    "dry_run": True
                }

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = cc

            # Add body to email
            msg.attach(MIMEText(body, 'plain'))

            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.email_address, self.email_password)

            # Get all recipients
            recipients = [to]
            if cc:
                recipients.extend(cc.split(','))
            if bcc:
                recipients.extend(bcc.split(','))

            # Send email
            text = msg.as_string()
            server.sendmail(self.email_address, recipients, text)
            server.quit()

            self.logger.info(f"Email sent successfully to {to}")
            return {
                "success": True,
                "message": f"Email sent to {to}",
                "dry_run": False
            }

        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return {
                "success": False,
                "message": f"Error sending email: {str(e)}",
                "dry_run": self.dry_run
            }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        try:
            if request.get("method") == "send_email":
                params = request.get("params", {})
                result = self.send_email(
                    to=params.get("to", ""),
                    subject=params.get("subject", ""),
                    body=params.get("body", ""),
                    cc=params.get("cc"),
                    bcc=params.get("bcc")
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }

            elif request.get("method") == "mcp/initialize":
                # Initialize the MCP server
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "serverInfo": {
                            "name": "email-mcp-server",
                            "version": "1.0.0"
                        },
                        "capabilities": {
                            "prompts": {},
                            "resources": {
                                "read": False,
                                "write": False
                            },
                            "tools": {
                                "definitions": [
                                    {
                                        "name": "send_email",
                                        "description": "Send an email to recipients",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "to": {"type": "string", "description": "Recipient email address"},
                                                "subject": {"type": "string", "description": "Email subject"},
                                                "body": {"type": "string", "description": "Email body content"},
                                                "cc": {"type": "string", "description": "CC recipients (optional)"},
                                                "bcc": {"type": "string", "description": "BCC recipients (optional)"}
                                            },
                                            "required": ["to", "subject", "body"]
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }

            elif request.get("method") == "textDocument/capabilities":
                # Return capabilities
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {}
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,  # Method not found
                        "message": f"Method {request.get('method')} not supported"
                    }
                }

        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,  # Internal error
                    "message": str(e)
                }
            }

    async def run_server(self):
        """Run the MCP server"""
        self.logger.info("Email MCP Server starting...")

        # Read from stdin and write to stdout in MCP protocol
        while True:
            try:
                # Read content length
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                if line.startswith('Content-Length:'):
                    length = int(line.split(':')[1].strip())

                    # Read empty line
                    await asyncio.get_event_loop().run_in_executor(None, input)

                    # Read JSON-RPC request
                    request_str = await asyncio.get_event_loop().run_in_executor(None, input)
                    request = json.loads(request_str)

                    # Handle the request
                    response = await self.handle_request(request)

                    # Send response
                    response_str = json.dumps(response)
                    response_bytes = response_str.encode('utf-8')

                    print(f'Content-Length: {len(response_bytes)}')
                    print('')
                    print(response_str, flush=True)

            except EOFError:
                # End of input, exit gracefully
                break
            except Exception as e:
                self.logger.error(f"Server error: {e}")
                # Continue running despite errors


if __name__ == "__main__":
    import sys

    # Check if running in MCP mode (through Claude Code)
    if '--mcp' in sys.argv:
        # Run as MCP server
        server = EmailMCP()
        try:
            asyncio.run(server.run_server())
        except KeyboardInterrupt:
            print("Email MCP Server stopped.")
    else:
        # Run in standalone mode for testing
        print("Email MCP Server - Standalone mode for testing")
        print("To run as MCP server, use: python email_mcp_server.py --mcp")

        # Example usage in standalone mode
        mcp = EmailMCP()
        result = mcp.send_email(
            to="test@example.com",
            subject="Test Email",
            body="This is a test email from the MCP server."
        )
        print(f"Test result: {result}")