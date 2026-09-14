#!/usr/bin/env python3
"""
SLO/SLA Tracking System
Tracks error budgets and compliance
"""

import json
from datetime import datetime, timedelta

class SLOTracker:
    def __init__(self):
        self.slos = {
            "availability": {
                "target": 99.95,
                "description": "System uptime"
            },
            "latency": {
                "target_p95": 500,
                "description": "Response time p95"
            },
            "success_rate": {
                "target": 99.9,
                "description": "Request success rate"
            }
        }
        self.error_budget_month = 21.6  # minutes in a month for 99.95%
    
    def calculate_error_budget(self, target_availability: float, period_days: int = 30) -> dict:
        """Calculate monthly error budget"""
        
        minutes_in_period = period_days * 24 * 60
        allowed_downtime_minutes = minutes_in_period * (100 - target_availability) / 100
        
        return {
            "period_days": period_days,
            "total_minutes": minutes_in_period,
            "target_availability": target_availability,
            "allowed_downtime_minutes": allowed_downtime_minutes,
            "allowed_downtime_hours": allowed_downtime_minutes / 60,
            "human_readable": f"{allowed_downtime_minutes:.1f} minutes/month or {allowed_downtime_minutes/60:.2f} hours/month"
        }
    
    def check_slo_compliance(self, actual_availability: float) -> dict:
        """Check if actual metrics meet SLO"""
        
        target = self.slos["availability"]["target"]
        budget = self.calculate_error_budget(target)
        
        # Calculate actual downtime
        total_minutes = budget["total_minutes"]
        actual_downtime = total_minutes * (100 - actual_availability) / 100
        allowed_downtime = budget["allowed_downtime_minutes"]
        
        is_compliant = actual_downtime <= allowed_downtime
        
        return {
            "target_availability": target,
            "actual_availability": actual_availability,
            "allowed_downtime_minutes": allowed_downtime,
            "actual_downtime_minutes": actual_downtime,
            "budget_remaining": allowed_downtime - actual_downtime,
            "budget_used_percent": (actual_downtime / allowed_downtime) * 100,
            "compliant": is_compliant,
            "status": "✅ COMPLIANT" if is_compliant else "❌ VIOLATED"
        }
    
    def generate_slo_report(self, metrics: dict) -> dict:
        """Generate comprehensive SLO report"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "slos": {}
        }
        
        # Availability SLO
        availability_check = self.check_slo_compliance(metrics.get("availability", 99.95))
        report["slos"]["availability"] = availability_check
        
        # Latency SLO (p95 < 500ms)
        latency_p95 = metrics.get("latency_p95", 450)
        latency_target = self.slos["latency"]["target_p95"]
        latency_compliant = latency_p95 < latency_target
        
        report["slos"]["latency"] = {
            "target_p95_ms": latency_target,
            "actual_p95_ms": latency_p95,
            "compliant": latency_compliant,
            "status": "✅ COMPLIANT" if latency_compliant else "❌ VIOLATED"
        }
        
        # Success Rate SLO (99.9%)
        success_rate = metrics.get("success_rate", 99.9)
        success_target = self.slos["success_rate"]["target"]
        success_compliant = success_rate >= success_target
        
        report["slos"]["success_rate"] = {
            "target_percent": success_target,
            "actual_percent": success_rate,
            "compliant": success_compliant,
            "status": "✅ COMPLIANT" if success_compliant else "❌ VIOLATED"
        }
        
        # Overall status
        all_compliant = (availability_check["compliant"] and 
                        latency_compliant and 
                        success_compliant)
        
        report["overall_status"] = "✅ ALL SLOs MET" if all_compliant else "❌ SLO VIOLATED"
        
        return report

if __name__ == "__main__":
    tracker = SLOTracker()
    
    print("════════════════════════════════════════════════════════════")
    print("  SLO/SLA TRACKING SYSTEM")
    print("════════════════════════════════════════════════════════════")
    
    # Error Budget Calculation
    print("\n📊 ERROR BUDGET (99.95% Availability Target)")
    print("─" * 60)
    budget = tracker.calculate_error_budget(99.95)
    print(f"Period: {budget['period_days']} days")
    print(f"Total Minutes: {budget['total_minutes']:,}")
    print(f"Allowed Downtime: {budget['human_readable']}")
    
    # Scenario 1: Compliant
    print("\n" + "="*60)
    print("SCENARIO 1: COMPLIANT DEPLOYMENT")
    print("="*60)
    
    compliant_metrics = {
        "availability": 99.96,      # Above 99.95% target
        "latency_p95": 450,         # Below 500ms target
        "success_rate": 99.92       # Above 99.9% target
    }
    
    report1 = tracker.generate_slo_report(compliant_metrics)
    
    print("\nAvailability SLO:")
    print(f"  Target: {report1['slos']['availability']['target_availability']}%")
    print(f"  Actual: {report1['slos']['availability']['actual_availability']}%")
    print(f"  Status: {report1['slos']['availability']['status']}")
    print(f"  Budget Remaining: {report1['slos']['availability']['budget_remaining']:.1f} minutes")
    
    print("\nLatency SLO:")
    print(f"  Target p95: {report1['slos']['latency']['target_p95_ms']}ms")
    print(f"  Actual p95: {report1['slos']['latency']['actual_p95_ms']}ms")
    print(f"  Status: {report1['slos']['latency']['status']}")
    
    print("\nSuccess Rate SLO:")
    print(f"  Target: {report1['slos']['success_rate']['target_percent']}%")
    print(f"  Actual: {report1['slos']['success_rate']['actual_percent']}%")
    print(f"  Status: {report1['slos']['success_rate']['status']}")
    
    print(f"\n{report1['overall_status']}")
    
    # Scenario 2: SLO Violated
    print("\n" + "="*60)
    print("SCENARIO 2: SLO VIOLATED - AVAILABILITY")
    print("="*60)
    
    violated_metrics = {
        "availability": 99.92,      # Below 99.95% target
        "latency_p95": 450,         # OK
        "success_rate": 99.92       # OK
    }
    
    report2 = tracker.generate_slo_report(violated_metrics)
    
    print("\nAvailability SLO:")
    print(f"  Target: {report2['slos']['availability']['target_availability']}%")
    print(f"  Actual: {report2['slos']['availability']['actual_availability']}%")
    print(f"  Status: {report2['slos']['availability']['status']}")
    print(f"  Budget Used: {report2['slos']['availability']['budget_used_percent']:.1f}%")
    print(f"  Budget Remaining: {report2['slos']['availability']['budget_remaining']:.1f} minutes")
    
    print(f"\n{report2['overall_status']}")
    
    print("\n════════════════════════════════════════════════════════════")
    print("✅ SLO TRACKING COMPLETE")
    print("════════════════════════════════════════════════════════════")
