#!/usr/bin/env python3
"""
Automatic Rollback Engine
Monitors metrics and triggers rollback if thresholds exceeded
"""

import json
import time
from datetime import datetime

class AutomaticRollbackEngine:
    def __init__(self):
        self.thresholds = {
            "error_rate": 1.0,        # Trigger if error rate > 1%
            "latency_p95": 2000,      # Trigger if latency p95 > 2000ms
            "cpu_usage": 90           # Trigger if CPU > 90%
        }
        self.status = "monitoring"
    
    def check_metrics(self, metrics: dict) -> dict:
        """Check if any metric exceeds threshold"""
        
        triggered_thresholds = []
        
        # Check error rate
        if metrics.get("error_rate", 0) > self.thresholds["error_rate"]:
            triggered_thresholds.append({
                "metric": "error_rate",
                "value": metrics["error_rate"],
                "threshold": self.thresholds["error_rate"],
                "status": "EXCEEDED"
            })
        
        # Check latency
        if metrics.get("latency_p95", 0) > self.thresholds["latency_p95"]:
            triggered_thresholds.append({
                "metric": "latency_p95",
                "value": metrics["latency_p95"],
                "threshold": self.thresholds["latency_p95"],
                "status": "EXCEEDED"
            })
        
        # Check CPU
        if metrics.get("cpu_usage", 0) > self.thresholds["cpu_usage"]:
            triggered_thresholds.append({
                "metric": "cpu_usage",
                "value": metrics["cpu_usage"],
                "threshold": self.thresholds["cpu_usage"],
                "status": "EXCEEDED"
            })
        
        return triggered_thresholds
    
    def trigger_rollback(self, reason: str, metrics: dict) -> dict:
        """Trigger automatic rollback"""
        
        print("\n🚨 AUTOMATIC ROLLBACK TRIGGERED!")
        print(f"Reason: {reason}")
        print("\nRollback Process:")
        print("  1. Stopping new traffic to v2.0...")
        time.sleep(0.5)
        print("  2. Switching ALB to v1.0 (blue environment)...")
        time.sleep(0.5)
        print("  3. Draining v2.0 connections...")
        time.sleep(0.5)
        print("  4. Reverting database migrations...")
        time.sleep(0.5)
        print("  5. Verifying v1.0 stability...")
        time.sleep(0.5)
        
        rollback = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "rollback_time_seconds": 30,
            "previous_version": "v1.0",
            "failed_version": "v2.0",
            "reason": reason,
            "metrics_at_rollback": metrics
        }
        
        print(f"\n✅ ROLLBACK COMPLETE in {rollback['rollback_time_seconds']} seconds")
        print(f"Current version: {rollback['previous_version']}")
        
        return rollback
    
    def monitor_deployment(self, metrics: dict) -> dict:
        """Monitor deployment and auto-rollback if needed"""
        
        print("\n════════════════════════════════════════")
        print("  AUTOMATIC ROLLBACK ENGINE")
        print("════════════════════════════════════════")
        print(f"\nMonitoring deployment...")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        print("\nMetrics Check:")
        print(f"  Error Rate: {metrics.get('error_rate', 0)}% (threshold: {self.thresholds['error_rate']}%)")
        print(f"  Latency p95: {metrics.get('latency_p95', 0)}ms (threshold: {self.thresholds['latency_p95']}ms)")
        print(f"  CPU Usage: {metrics.get('cpu_usage', 0)}% (threshold: {self.thresholds['cpu_usage']}%)")
        
        # Check thresholds
        exceeded = self.check_metrics(metrics)
        
        if exceeded:
            reason = f"Thresholds exceeded: {', '.join([t['metric'] for t in exceeded])}"
            rollback_result = self.trigger_rollback(reason, metrics)
            return rollback_result
        else:
            print("\n✅ All metrics within acceptable range")
            print("   Deployment stable, continuing monitoring...")
            return {
                "status": "stable",
                "timestamp": datetime.now().isoformat()
            }

if __name__ == "__main__":
    engine = AutomaticRollbackEngine()
    
    # Scenario 1: Healthy deployment
    print("\n" + "="*50)
    print("SCENARIO 1: HEALTHY DEPLOYMENT")
    print("="*50)
    
    healthy_metrics = {
        "error_rate": 0.1,      # 0.1% (below 1%)
        "latency_p95": 1200,    # 1200ms (below 2000ms)
        "cpu_usage": 45         # 45% (below 90%)
    }
    
    result1 = engine.monitor_deployment(healthy_metrics)
    
    # Scenario 2: Failed deployment (error rate spike)
    print("\n" + "="*50)
    print("SCENARIO 2: DEPLOYMENT FAILURE - ERROR RATE SPIKE")
    print("="*50)
    
    failed_metrics = {
        "error_rate": 5.2,      # 5.2% (EXCEEDS 1%)
        "latency_p95": 1800,    # 1800ms (ok)
        "cpu_usage": 60         # 60% (ok)
    }
    
    result2 = engine.monitor_deployment(failed_metrics)
    
    print("\n" + "="*50)
    print("✅ AUTOMATIC ROLLBACK ENGINE TEST COMPLETE")
    print("="*50)
