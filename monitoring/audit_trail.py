#!/usr/bin/env python3
"""
Audit Trail Logging System
Logs all deployment events for compliance and debugging
"""

import json
import os
from datetime import datetime

class AuditTrail:
    def __init__(self):
        self.log_dir = "monitoring/audit_logs"
        os.makedirs(self.log_dir, exist_ok=True)
    
    def log_event(self, event_type: str, phase: str, status: str, details: dict) -> str:
        """Log a deployment event"""
        
        event = {
            "event_id": f"{phase}-{event_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "phase": phase,
            "status": status,
            "details": details
        }
        
        # Save to JSON file
        log_path = f"{self.log_dir}/{event['event_id']}.json"
        with open(log_path, 'w') as f:
            json.dump(event, f, indent=2)
        
        print(f"✅ Event logged: {event['event_id']}")
        return event['event_id']
    
    def get_events(self, phase: str = None) -> list:
        """Retrieve audit events"""
        
        events = []
        for filename in os.listdir(self.log_dir):
            if filename.endswith('.json'):
                if phase is None or phase in filename:
                    with open(f"{self.log_dir}/{filename}", 'r') as f:
                        events.append(json.load(f))
        
        return sorted(events, key=lambda x: x['timestamp'])
    
    def generate_report(self) -> dict:
        """Generate audit trail report"""
        
        events = self.get_events()
        return {
            "total_events": len(events),
            "timestamp": datetime.now().isoformat(),
            "events": events
        }

if __name__ == "__main__":
    audit = AuditTrail()
    
    # Test logging
    print("Testing audit trail logging...\n")
    
    audit.log_event(
        event_type="deployment_start",
        phase="phase-1-database",
        status="started",
        details={"user": "engineer", "environment": "local"}
    )
    
    audit.log_event(
        event_type="security_check",
        phase="phase-1-database",
        status="passed",
        details={"scan_type": "sast", "issues": 0}
    )
    
    audit.log_event(
        event_type="deployment_complete",
        phase="phase-1-database",
        status="success",
        details={"duration_minutes": 5}
    )
    
    # Generate report
    print("\n📋 Audit Trail Report:")
    report = audit.generate_report()
    print(f"Total Events: {report['total_events']}")
    print("\nEvents:")
    for event in report['events']:
        print(f"  - {event['timestamp']}: {event['event_type']} ({event['status']})")
