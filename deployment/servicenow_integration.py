#!/usr/bin/env python3
"""
ServiceNow Integration for Change Management
Local mock version for development
"""

import json
import os
from datetime import datetime

class ServiceNowIntegration:
    def __init__(self):
        self.env = os.getenv("ENVIRONMENT", "local")
        self.ticket_dir = "deployment/servicenow/tickets"
        os.makedirs(self.ticket_dir, exist_ok=True)
    
    def create_change_ticket(self, title: str, description: str = "") -> str:
        """Create a change ticket"""
        ticket = {
            "ticket_number": f"CHG{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "description": description,
            "status": "new",
            "created_at": datetime.utcnow().isoformat(),
            "approvers": ["Engineer1", "Engineer2", "Engineer3"],
            "approvals": 0,
            "approval_status": "pending"
        }
        
        # Save locally
        ticket_path = f"{self.ticket_dir}/{ticket['ticket_number']}.json"
        with open(ticket_path, 'w') as f:
            json.dump(ticket, f, indent=2)
        
        print(f"✅ Change ticket created: {ticket['ticket_number']}")
        print(f"   Saved to: {ticket_path}")
        return ticket['ticket_number']
    
    def get_ticket(self, ticket_number: str) -> dict:
        """Get ticket details"""
        ticket_path = f"{self.ticket_dir}/{ticket_number}.json"
        if os.path.exists(ticket_path):
            with open(ticket_path, 'r') as f:
                return json.load(f)
        return None
    
    def approve_ticket(self, ticket_number: str, approver: str) -> dict:
        """Simulate CAB approval"""
        ticket = self.get_ticket(ticket_number)
        if ticket:
            ticket['approvals'] += 1
            if ticket['approvals'] >= 2:
                ticket['approval_status'] = 'approved'
            
            ticket_path = f"{self.ticket_dir}/{ticket_number}.json"
            with open(ticket_path, 'w') as f:
                json.dump(ticket, f, indent=2)
            
            print(f"✅ Approval from {approver}: {ticket['approval_status']}")
            return ticket
        return None

if __name__ == "__main__":
    sns = ServiceNowIntegration()
    
    # Create test ticket
    ticket = sns.create_change_ticket(
        title="v1.0 → v2.0 Zero-Downtime Migration",
        description="Database migration with blue-green deployment"
    )
    
    print(f"\n📋 Ticket: {ticket}")
    
    # Get ticket
    details = sns.get_ticket(ticket)
    print(f"Status: {details['approval_status']}")
    print(f"Approvals: {details['approvals']}/3")
