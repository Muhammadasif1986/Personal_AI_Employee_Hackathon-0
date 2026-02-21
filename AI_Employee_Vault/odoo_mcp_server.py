#!/usr/bin/env python3
"""
Odoo MCP Server - Model Context Protocol server for Odoo accounting integration
"""
import asyncio
import json
import logging
import os
import xmlrpc.client
from pathlib import Path
from typing import Dict, Any, List
import re


class OdooMCP:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Get Odoo configuration from environment
        self.url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.db = os.getenv('ODOO_DB', 'odoo_db')
        self.username = os.getenv('ODOO_USERNAME')
        self.password = os.getenv('ODOO_PASSWORD')

        if not all([self.username, self.password]):
            self.logger.warning("Odoo credentials not set. Server will operate in dry-run mode.")
            self.dry_run = True
        else:
            self.dry_run = False

        # Initialize Odoo connection
        self.common = None
        self.models = None
        self.uid = None

    def connect_to_odoo(self):
        """Connect to Odoo if credentials are provided"""
        if self.dry_run:
            return True

        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            return True
        except Exception as e:
            self.logger.error(f"Error connecting to Odoo: {e}")
            self.dry_run = True
            return False

    def create_invoice(self, customer: str, amount: float, description: str,
                      invoice_date: str = None, reference: str = None) -> Dict[str, Any]:
        """Create an invoice in Odoo"""
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would create invoice for {customer}: ${amount} - {description}")
                return {
                    "success": True,
                    "message": "Would create invoice in dry-run mode",
                    "invoice_id": "DRY001",
                    "invoice_number": "INV-DRY-001",
                    "dry_run": True
                }

            # Connect to Odoo if not already connected
            if not self.uid:
                if not self.connect_to_odoo():
                    return {
                        "success": False,
                        "message": "Failed to connect to Odoo",
                        "dry_run": True
                    }

            # Find or create customer partner
            partner_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'search',
                [[['name', '=', customer]]]
            )

            if not partner_ids:
                # Create customer if not found
                partner_id = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'res.partner', 'create',
                    [{'name': customer, 'customer_rank': 1}]
                )
            else:
                partner_id = partner_ids[0]

            # Create invoice
            invoice_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'create',
                [{
                    'partner_id': partner_id,
                    'move_type': 'out_invoice',
                    'invoice_date': invoice_date or str(self.common.strftime('%Y-%m-%d')),
                    'ref': reference,
                    'invoice_line_ids': [
                        (0, 0, {
                            'name': description,
                            'quantity': 1,
                            'price_unit': amount,
                        }),
                    ],
                }]
            )

            return {
                "success": True,
                "message": "Invoice created successfully",
                "invoice_id": invoice_id,
                "invoice_number": f"INV-{invoice_id:05d}",
                "dry_run": False
            }

        except Exception as e:
            self.logger.error(f"Error creating invoice: {e}")
            return {
                "success": False,
                "message": f"Error creating invoice: {str(e)}",
                "dry_run": self.dry_run
            }

    def get_invoices(self, limit: int = 10, customer: str = None) -> Dict[str, Any]:
        """Get invoices from Odoo"""
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would get {limit} invoices")
                if customer:
                    self.logger.info(f"[DRY RUN] Filter by customer: {customer}")

                sample_invoices = [
                    {
                        "id": f"DRY_INV_{i}",
                        "number": f"INV-DRY-{i:03d}",
                        "customer": "Sample Customer" if not customer else customer,
                        "amount": 1500.00 + (i * 100),
                        "date": f"2026-02-{15+i:02d}",
                        "status": "posted" if i % 3 != 0 else "draft"
                    }
                    for i in range(limit)
                ]
                return {
                    "success": True,
                    "invoices": sample_invoices,
                    "dry_run": True
                }

            # Connect to Odoo if not already connected
            if not self.uid:
                if not self.connect_to_odoo():
                    return {
                        "success": False,
                        "message": "Failed to connect to Odoo",
                        "dry_run": True
                    }

            # Build domain for search
            domain = [['move_type', '=', 'out_invoice']]
            if customer:
                domain.append(['partner_id.name', 'ilike', customer])

            # Search invoices
            invoice_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'search',
                [domain],
                {'limit': limit}
            )

            if not invoice_ids:
                return {
                    "success": True,
                    "invoices": [],
                    "message": "No invoices found",
                    "dry_run": False
                }

            # Read invoice details
            invoices = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'read',
                [invoice_ids, ['name', 'partner_id', 'amount_total', 'invoice_date', 'state']]
            )

            formatted_invoices = []
            for inv in invoices:
                formatted_invoices.append({
                    "id": inv['id'],
                    "number": inv['name'],
                    "customer": inv['partner_id'][1] if inv['partner_id'] else "Unknown",
                    "amount": inv['amount_total'],
                    "date": inv['invoice_date'],
                    "status": inv['state']
                })

            return {
                "success": True,
                "invoices": formatted_invoices,
                "dry_run": False
            }

        except Exception as e:
            self.logger.error(f"Error getting invoices: {e}")
            return {
                "success": False,
                "message": f"Error getting invoices: {str(e)}",
                "dry_run": self.dry_run
            }

    def create_contact(self, name: str, email: str = None, phone: str = None,
                      company: str = None) -> Dict[str, Any]:
        """Create a contact in Odoo"""
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would create contact: {name}")
                if email:
                    self.logger.info(f"[DRY RUN] Email: {email}")
                if phone:
                    self.logger.info(f"[DRY RUN] Phone: {phone}")
                return {
                    "success": True,
                    "message": "Would create contact in dry-run mode",
                    "contact_id": "DRY_CONTACT_1",
                    "dry_run": True
                }

            # Connect to Odoo if not already connected
            if not self.uid:
                if not self.connect_to_odoo():
                    return {
                        "success": False,
                        "message": "Failed to connect to Odoo",
                        "dry_run": True
                    }

            # Prepare contact data
            contact_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'type': 'contact'
            }

            if company:
                contact_data['parent_id'] = company

            # Create contact
            contact_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'create',
                [contact_data]
            )

            return {
                "success": True,
                "message": "Contact created successfully",
                "contact_id": contact_id,
                "dry_run": False
            }

        except Exception as e:
            self.logger.error(f"Error creating contact: {e}")
            return {
                "success": False,
                "message": f"Error creating contact: {str(e)}",
                "dry_run": self.dry_run
            }

    def get_contacts(self, limit: int = 10, name_filter: str = None) -> Dict[str, Any]:
        """Get contacts from Odoo"""
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would get {limit} contacts")
                if name_filter:
                    self.logger.info(f"[DRY RUN] Filter by name: {name_filter}")

                sample_contacts = [
                    {
                        "id": f"DRY_CONTACT_{i}",
                        "name": f"Sample Contact {i}",
                        "email": f"contact{i}@example.com",
                        "phone": f"+1-555-000-{i:04d}",
                        "company": "Sample Company" if i % 2 == 0 else None
                    }
                    for i in range(limit)
                ]
                return {
                    "success": True,
                    "contacts": sample_contacts,
                    "dry_run": True
                }

            # Connect to Odoo if not already connected
            if not self.uid:
                if not self.connect_to_odoo():
                    return {
                        "success": False,
                        "message": "Failed to connect to Odoo",
                        "dry_run": True
                    }

            # Build domain for search
            domain = [['type', '=', 'contact']]
            if name_filter:
                domain.append(['name', 'ilike', name_filter])

            # Search contacts
            contact_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'search',
                [domain],
                {'limit': limit}
            )

            if not contact_ids:
                return {
                    "success": True,
                    "contacts": [],
                    "message": "No contacts found",
                    "dry_run": False
                }

            # Read contact details
            contacts = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'read',
                [contact_ids, ['name', 'email', 'phone', 'parent_id']]
            )

            formatted_contacts = []
            for contact in contacts:
                formatted_contacts.append({
                    "id": contact['id'],
                    "name": contact['name'],
                    "email": contact['email'],
                    "phone": contact['phone'],
                    "company": contact['parent_id'][1] if contact['parent_id'] else None
                })

            return {
                "success": True,
                "contacts": formatted_contacts,
                "dry_run": False
            }

        except Exception as e:
            self.logger.error(f"Error getting contacts: {e}")
            return {
                "success": False,
                "message": f"Error getting contacts: {str(e)}",
                "dry_run": self.dry_run
            }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        try:
            method = request.get("method")

            if method == "create_invoice":
                params = request.get("params", {})
                result = self.create_invoice(
                    customer=params.get("customer", ""),
                    amount=params.get("amount", 0.0),
                    description=params.get("description", ""),
                    invoice_date=params.get("invoice_date"),
                    reference=params.get("reference")
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }

            elif method == "get_invoices":
                params = request.get("params", {})
                result = self.get_invoices(
                    limit=params.get("limit", 10),
                    customer=params.get("customer")
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }

            elif method == "create_contact":
                params = request.get("params", {})
                result = self.create_contact(
                    name=params.get("name", ""),
                    email=params.get("email"),
                    phone=params.get("phone"),
                    company=params.get("company")
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }

            elif method == "get_contacts":
                params = request.get("params", {})
                result = self.get_contacts(
                    limit=params.get("limit", 10),
                    name_filter=params.get("name_filter")
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }

            elif method == "mcp/initialize":
                # Initialize the MCP server
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "serverInfo": {
                            "name": "odoo-mcp-server",
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
                                        "name": "create_invoice",
                                        "description": "Create an invoice in Odoo accounting system",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "customer": {"type": "string", "description": "Customer name"},
                                                "amount": {"type": "number", "description": "Invoice amount"},
                                                "description": {"type": "string", "description": "Description of the invoice"},
                                                "invoice_date": {"type": "string", "description": "Invoice date (YYYY-MM-DD format, optional)"},
                                                "reference": {"type": "string", "description": "Reference number (optional)"}
                                            },
                                            "required": ["customer", "amount", "description"]
                                        }
                                    },
                                    {
                                        "name": "get_invoices",
                                        "description": "Get invoices from Odoo accounting system",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "limit": {"type": "integer", "description": "Maximum number of invoices to return (default: 10)"},
                                                "customer": {"type": "string", "description": "Filter by customer name (optional)"}
                                            }
                                        }
                                    },
                                    {
                                        "name": "create_contact",
                                        "description": "Create a contact in Odoo CRM",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string", "description": "Contact name"},
                                                "email": {"type": "string", "description": "Contact email (optional)"},
                                                "phone": {"type": "string", "description": "Contact phone (optional)"},
                                                "company": {"type": "string", "description": "Company name (optional)"}
                                            },
                                            "required": ["name"]
                                        }
                                    },
                                    {
                                        "name": "get_contacts",
                                        "description": "Get contacts from Odoo CRM",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "limit": {"type": "integer", "description": "Maximum number of contacts to return (default: 10)"},
                                                "name_filter": {"type": "string", "description": "Filter by name pattern (optional)"}
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }

            elif method == "textDocument/capabilities":
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
                        "message": f"Method {method} not supported"
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
        self.logger.info("Odoo MCP Server starting...")

        # Read from stdin and write to stdout in MCP protocol
        while True:
            try:
                # Read content length (simplified for this example)
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
        server = OdooMCP()
        try:
            asyncio.run(server.run_server())
        except KeyboardInterrupt:
            print("Odoo MCP Server stopped.")
    else:
        # Run in standalone mode for testing
        print("Odoo MCP Server - Standalone mode for testing")
        print("To run as MCP server, use: python odoo_mcp_server.py --mcp")

        # Example usage in standalone mode
        mcp = OdooMCP()
        result = mcp.create_invoice(
            customer="Test Customer",
            amount=1500.00,
            description="Website development services"
        )
        print(f"Test result: {result}")