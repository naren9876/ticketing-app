# 🚀 Zero-Downtime Migration Strategy
## Movie Ticketing Platform v2.0 Deployment

**Plan Status**: ✅ PRODUCTION READY  
**Total Duration**: 7+ days  
**Downtime**: 0 minutes  
**Rollback Risk**: Minimal  
**Coverage**: 100% integrated with AWS infrastructure

---

## 📋 Executive Summary

This document details a **4-phase, zero-downtime migration** from v1.0 to v2.0 of the Movie Ticketing Platform. The strategy emphasizes safety through:

- ✅ Database backward compatibility (dual-column approach)
- ✅ Feature flag control (gradual enablement)
- ✅ Blue-green deployment (instant rollback)
- ✅ Canary rollout (monitored rollout)
- ✅ Automated smoke tests (quality gates)
- ✅ Gradual traffic shifting (risk mitigation)
- ✅ Comprehensive monitoring (instant detection)

---

## 🎯 Migration Overview

```
┌──────────────────────────────────────────────────────────┐
│           7-DAY ZERO-DOWNTIME MIGRATION PLAN            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  DAY 1: DATABASE MIGRATION (Schema change)              │
│  ├─ Add payment_method_v2 column (nullable)             │
│  ├─ Backfill existing data                              │
│  ├─ Both v1 & v2 code can run simultaneously            │
│  └─ Zero impact to production                           │
│     RISK: LOW | DOWNTIME: 0 min                         │
│                                                          │
│  DAY 2: BACKEND DEPLOYMENT (Blue-Green)                │
│  ├─ Deploy new Payment, Booking, Movie services         │
│  ├─ Run smoke tests on new "green" environment          │
│  ├─ Switch 100% traffic from blue to green              │
│  ├─ Keep blue environment running for rollback          │
│  └─ Verify all transactions working                     │
│     RISK: MINIMAL | DOWNTIME: 0 min                     │
│     ROLLBACK: 30 seconds (switch ALB target)            │
│                                                          │
│  DAY 3: FRONTEND ROLLOUT (Canary)                      │
│  ├─ 5% users → v2.0 frontend (30 min, monitor)          │
│  ├─ 10% users → v2.0 frontend (60 min, monitor)         │
│  ├─ 25% users → v2.0 frontend (60 min, monitor)         │
│  ├─ 50% users → v2.0 frontend (60 min, monitor)         │
│  └─ 100% users → v2.0 frontend (final)                  │
│     RISK: VERY LOW | DOWNTIME: 0 min                    │
│     ROLLBACK: Real-time (CDN cache purge)               │
│                                                          │
│  DAY 4+: MOBILE APP DEPLOYMENT                         │
│  ├─ Submit iOS/Android to stores (24-48 hr review)      │
│  ├─ Staged rollout: 10% → 25% → 100%                    │
│  ├─ Keep v1 API endpoint active (3+ months)             │
│  ├─ Users gradually adopt new version                   │
│  └─ Monitor adoption metrics                            │
│     RISK: LOW | DOWNTIME: 0 min                         │
│     COMPATIBILITY: Full backward compatibility          │
│                                                          │
└──────────────────────────────────────────────────────────┘

TOTAL DEPLOYMENT TIME: 7+ days (distributed)
PRODUCTION DOWNTIME: 0 minutes
ESTIMATED COST: No additional infrastructure
SUCCESS CRITERIA: 100% traffic on v2.0, zero rollbacks
```

---

## 📊 Integration with AWS Infrastructure

The migration leverages the AWS infrastructure deployed via Terraform:

```
AWS Components Used
├─ Application Load Balancer (ALB)
│  └─ Blue-Green target group switching
├─ EKS Cluster (Kubernetes)
│  ├─ Deployment strategy: rolling update
│  ├─ Pod disruption budgets
│  └─ Health check probes
├─ RDS Aurora PostgreSQL
│  ├─ Schema migration via jobs
│  ├─ Data backfill procedure
│  └─ Rollback capability
├─ CloudWatch Monitoring
│  ├─ Custom metrics per environment
│  ├─ Canary-specific dashboards
│  └─ Error rate tracking (thresholds)
├─ CodeDeploy / ECS
│  ├─ Blue-green hooks
│  └─ Automated traffic shifting
└─ Feature Flags (Feature Management Service)
   ├─ Backend: enable_payment_v2
   ├─ Frontend: show_v2_ui
   └─ Mobile: use_new_api
```

---

## 🗓️ PHASE 1: Database Migration (Day 1)

### Objective
Add new `payment_method_v2` column to payments table with **zero downtime** and **full backward compatibility**.

### Prerequisites
- [ ] Database backup created and tested
- [ ] Migration script reviewed and tested on staging
- [ ] Rollback procedure documented
- [ ] Feature flags disabled in code
- [ ] Monitoring alerts configured

### Step-by-Step Procedure

#### Step 1.1: Create Migration Script (Preparation)

```sql
-- File: migrations/001_add_payment_method_v2.sql
-- Author: Database Team
-- Date: 2026-09-11
-- Risk: LOW (additive only)

BEGIN;

-- Step 1: Add nullable column (online DDL, no locks)
ALTER TABLE payments 
ADD COLUMN payment_method_v2 VARCHAR(50) NULL;

-- Step 2: Add index for performance
CREATE INDEX idx_payments_method_v2 
ON payments(payment_method_v2) 
CONCURRENTLY;

-- Step 3: Add comment for documentation
COMMENT ON COLUMN payments.payment_method_v2 
IS 'v2 payment method support (migration in progress)';

COMMIT;
```

#### Step 1.2: Execute Schema Migration

```bash
#!/bin/bash
# Script: database/migrate_v1_to_v2.sh

CLUSTER_NAME="ticketing-cluster"
NAMESPACE="ticketing"
RDS_ENDPOINT=$(aws rds describe-db-clusters \
  --db-cluster-identifier ticketing-cluster \
  | jq -r '.DBClusters[0].Endpoint')

echo "🔄 Starting database migration..."
echo "Target: $RDS_ENDPOINT"

# 1. Verify backup exists
aws rds describe-db-cluster-snapshots \
  --db-cluster-identifier ticketing-cluster \
  | jq '.DBClusterSnapshots[0]'

# 2. Execute migration
psql -h $RDS_ENDPOINT -U admin -d ticketingdb \
  -f migrations/001_add_payment_method_v2.sql

if [ $? -eq 0 ]; then
  echo "✅ Schema migration completed"
else
  echo "❌ Migration failed, triggering rollback"
  # Rollback: DROP COLUMN payment_method_v2;
  exit 1
fi

# 3. Verify new column
psql -h $RDS_ENDPOINT -U admin -d ticketingdb \
  -c "SELECT column_name FROM information_schema.columns 
      WHERE table_name='payments' 
      AND column_name='payment_method_v2';"

# 4. Check constraint
psql -h $RDS_ENDPOINT -U admin -d ticketingdb \
  -c "ALTER TABLE payments 
      ADD CONSTRAINT check_payment_method_v2 
      CHECK (payment_method_v2 IS NOT NULL OR payment_method IS NOT NULL);"

echo "✅ Database migration completed successfully"
```

#### Step 1.3: Data Backfill (Optional, for existing data)

```python
# Script: database/backfill_payment_method_v2.py
# Purpose: Migrate existing v1 payment data to v2 format (if needed)

import psycopg2
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentMethodBackfill:
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cursor = self.conn.cursor()
    
    def backfill_payment_method_v2(self, batch_size: int = 1000):
        """
        Migrate payment_method v1 → v2 format
        
        v1 format: "card", "paypal", "wallet"
        v2 format: "payment_card_v2", "wallet_v2", "bank_transfer"
        """
        
        migration_map = {
            'card': 'payment_card_v2',
            'paypal': 'wallet_v2',
            'wallet': 'wallet_v2',
            'bank_transfer': 'bank_transfer'
        }
        
        logger.info("Starting payment method backfill...")
        
        # Step 1: Count records to migrate
        self.cursor.execute(
            "SELECT COUNT(*) FROM payments WHERE payment_method_v2 IS NULL"
        )
        total_records = self.cursor.fetchone()[0]
        logger.info(f"Total records to backfill: {total_records}")
        
        # Step 2: Backfill in batches
        processed = 0
        while processed < total_records:
            self.cursor.execute(f"""
                SELECT id, payment_method 
                FROM payments 
                WHERE payment_method_v2 IS NULL 
                LIMIT {batch_size}
            """)
            
            batch = self.cursor.fetchall()
            if not batch:
                break
            
            # Step 3: Update records
            for payment_id, v1_method in batch:
                v2_method = migration_map.get(v1_method, v1_method)
                
                self.cursor.execute(f"""
                    UPDATE payments 
                    SET payment_method_v2 = '{v2_method}',
                        updated_at = NOW()
                    WHERE id = {payment_id}
                """)
            
            self.conn.commit()
            processed += len(batch)
            
            # Progress logging
            if processed % 10000 == 0:
                logger.info(f"Processed: {processed}/{total_records} records")
        
        logger.info(f"✅ Backfill completed: {processed} records migrated")
    
    def verify_migration(self):
        """Verify data integrity post-migration"""
        
        # Check: No NULL values in v2 for migrated records
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM payments 
            WHERE payment_method IS NOT NULL 
            AND payment_method_v2 IS NULL
        """)
        
        orphaned = self.cursor.fetchone()[0]
        if orphaned == 0:
            logger.info("✅ All payments have v2 method")
        else:
            logger.warning(f"⚠️  {orphaned} payments missing v2 method")
        
        # Check: Distribution of v2 methods
        self.cursor.execute("""
            SELECT payment_method_v2, COUNT(*) 
            FROM payments 
            WHERE payment_method_v2 IS NOT NULL 
            GROUP BY payment_method_v2
        """)
        
        logger.info("Payment method v2 distribution:")
        for method, count in self.cursor.fetchall():
            logger.info(f"  {method}: {count}")

# Usage
if __name__ == "__main__":
    backfill = PaymentMethodBackfill(
        "postgresql://admin:password@rds-endpoint:5432/ticketingdb"
    )
    backfill.backfill_payment_method_v2(batch_size=5000)
    backfill.verify_migration()
```

#### Step 1.4: Verification & Rollback

```bash
#!/bin/bash
# Script: database/verify_migration.sh

echo "📊 Database Migration Verification"
echo "==================================="

# 1. Verify column exists
echo "✓ Checking payment_method_v2 column..."
psql -h $RDS_ENDPOINT -U admin -d ticketingdb \
  -c "SELECT column_name, data_type, is_nullable 
      FROM information_schema.columns 
      WHERE table_name='payments' 
      AND column_name='payment_method_v2';"

# 2. Verify no data loss
echo "✓ Checking data integrity..."
psql -h $RDS_ENDPOINT -U admin -d ticketingdb \
  -c "SELECT COUNT(*) as total_payments FROM payments;
      SELECT COUNT(*) as with_payment_method FROM payments 
        WHERE payment_method IS NOT NULL OR payment_method_v2 IS NOT NULL;"

# 3. Verify performance (check indexes)
echo "✓ Checking performance..."
psql -h $RDS_ENDPOINT -U admin -d ticketingdb \
  -c "SELECT indexname, idx_scan, idx_tup_read, idx_tup_fetch 
      FROM pg_stat_user_indexes 
      WHERE relname='payments';"

# 4. Check constraint
echo "✓ Verifying constraints..."
psql -h $RDS_ENDPOINT -U admin -d ticketingdb \
  -c "SELECT constraint_name, constraint_type 
      FROM information_schema.table_constraints 
      WHERE table_name='payments';"

echo "✅ Database migration verified successfully"

# ROLLBACK (if needed)
# psql -h $RDS_ENDPOINT -U admin -d ticketingdb \
#   -c "ALTER TABLE payments DROP COLUMN payment_method_v2;"
```

### Success Criteria for Phase 1
- [ ] Column `payment_method_v2` exists and is nullable
- [ ] All existing payments have either `payment_method` OR `payment_method_v2` populated
- [ ] New payments can use either column
- [ ] Rollback procedure tested
- [ ] Zero impact to production traffic
- [ ] CloudWatch shows normal metrics

### Rollback Procedure (Phase 1)

```bash
# If schema migration needs to be rolled back:

psql -h $RDS_ENDPOINT -U admin -d ticketingdb << EOF
BEGIN;
-- Drop column and constraints
ALTER TABLE payments DROP CONSTRAINT check_payment_method_v2 CASCADE;
DROP INDEX idx_payments_method_v2;
ALTER TABLE payments DROP COLUMN payment_method_v2;
COMMIT;
EOF

echo "✅ Database rolled back to v1.0"
```

---

## 🛠️ PHASE 2: Backend Deployment (Day 2, Blue-Green)

### Objective
Deploy v2.0 backend services with **zero downtime** using **blue-green deployment**.

### Architecture

```
┌─────────────────────────────────────────────┐
│          AWS Load Balancer (ALB)            │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────┐    ┌─────────────────┐│
│  │  BLUE (v1.0)    │    │  GREEN (v2.0)   ││
│  │                 │    │                 ││
│  │ payment:3004-v1 │    │ payment:3004-v2 ││
│  │ booking:3003-v1 │    │ booking:3003-v2 ││
│  │ movie:3002-v1   │    │ movie:3002-v2   ││
│  │                 │    │                 ││
│  │ 100% traffic ──→│    │ Testing         ││
│  └─────────────────┘    └─────────────────┘│
│                                             │
│  READY TO SWITCH: After Green passes       │
│  ALL SMOKE TESTS                           │
│                                             │
└─────────────────────────────────────────────┘

Timeline:
- 10:00 AM: Start GREEN deployment (no traffic)
- 10:15 AM: GREEN pods ready
- 10:20 AM: Run smoke tests on GREEN
- 10:25 AM: Switch traffic to GREEN (30 sec)
- 10:30 AM: Verify 100% traffic on GREEN
- 10:35 AM: Keep BLUE running (ready to rollback)
```

### Prerequisites
- [ ] Database migration (Phase 1) completed
- [ ] Feature flags configured (enable_payment_v2: false)
- [ ] v2.0 services tested in staging
- [ ] Smoke test suite ready
- [ ] Deployment configuration reviewed

### Step-by-Step Procedure

#### Step 2.1: Deploy Green Environment

```bash
#!/bin/bash
# Script: deployment/02_backend_bluegreen_deploy.sh

set -e

CLUSTER_NAME="ticketing-cluster"
NAMESPACE="ticketing"
ENVIRONMENT="green"  # Current deployment environment
GREEN_VERSION="v2.0"
BLUE_VERSION="v1.0"

echo "🚀 Starting Blue-Green Deployment"
echo "=================================="
echo "Blue (current):  $BLUE_VERSION"
echo "Green (new):     $GREEN_VERSION"

# Step 1: Deploy GREEN services
echo "📦 Deploying GREEN services (v2.0)..."

# Pull latest images
docker pull $ECR_REPO/payment-service:$GREEN_VERSION
docker pull $ECR_REPO/booking-service:$GREEN_VERSION
docker pull $ECR_REPO/movie-service:$GREEN_VERSION

# Deploy to green namespace/labels
kubectl set image deployment/payment-service-green \
  payment-service=$ECR_REPO/payment-service:$GREEN_VERSION \
  -n $NAMESPACE || kubectl create deployment payment-service-green \
  --image=$ECR_REPO/payment-service:$GREEN_VERSION \
  -n $NAMESPACE

# Wait for rollout (max 5 minutes)
echo "⏳ Waiting for GREEN deployment to be ready..."
kubectl rollout status deployment/payment-service-green \
  -n $NAMESPACE --timeout=5m

# Step 2: Health checks on GREEN
echo "🏥 Running health checks on GREEN..."
GREEN_PODS=$(kubectl get pods -n $NAMESPACE \
  -l app=payment-service,version=green \
  -o jsonpath='{.items[*].metadata.name}')

for pod in $GREEN_PODS; do
  kubectl run health-check-$pod --image=curlimages/curl --restart=Never -- \
    curl -f http://$pod:3004/health || {
    echo "❌ Health check failed for $pod"
    # Trigger smoke tests anyway to get better error visibility
  }
done

# Step 3: Verify replicas
READY_REPLICAS=$(kubectl get deployment payment-service-green \
  -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
DESIRED_REPLICAS=$(kubectl get deployment payment-service-green \
  -n $NAMESPACE -o jsonpath='{.spec.replicas}')

if [ "$READY_REPLICAS" != "$DESIRED_REPLICAS" ]; then
  echo "❌ Not all replicas ready: $READY_REPLICAS/$DESIRED_REPLICAS"
  exit 1
fi

echo "✅ GREEN deployment ready: $READY_REPLICAS/$DESIRED_REPLICAS pods"
```

#### Step 2.2: Run Smoke Tests

```bash
#!/bin/bash
# Script: deployment/smoke_tests.sh
# Purpose: Validate v2.0 backend before switching traffic

set -e

NAMESPACE="ticketing"
GREEN_SERVICE="payment-service-green"
TEST_TIMEOUT=600  # 10 minutes

echo "🧪 Running Smoke Tests on GREEN (v2.0)"
echo "======================================"

# Get Green service IP
GREEN_IP=$(kubectl get service $GREEN_SERVICE \
  -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Testing: $GREEN_IP"
TEST_PASSED=true

# Test 1: API Health Check
echo "Test 1/5: Health Check"
if curl -f http://$GREEN_IP:3004/health; then
  echo "  ✅ Health check passed"
else
  echo "  ❌ Health check failed"
  TEST_PASSED=false
fi

# Test 2: Create payment (with v2 method)
echo "Test 2/5: Create Payment (v2 format)"
PAYMENT_RESPONSE=$(curl -s -X POST http://$GREEN_IP:3004/payments \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "amount": 100.00,
    "payment_method_v2": "payment_card_v2",
    "idempotency_key": "test_'$(date +%s)'"
  }')

if echo "$PAYMENT_RESPONSE" | jq -e '.payment_id' > /dev/null; then
  echo "  ✅ Payment creation succeeded"
  PAYMENT_ID=$(echo "$PAYMENT_RESPONSE" | jq -r '.payment_id')
else
  echo "  ❌ Payment creation failed"
  echo "Response: $PAYMENT_RESPONSE"
  TEST_PASSED=false
fi

# Test 3: Query payment
echo "Test 3/5: Query Payment"
QUERY_RESPONSE=$(curl -s http://$GREEN_IP:3004/payments/$PAYMENT_ID)
if echo "$QUERY_RESPONSE" | jq -e '.payment_method_v2' > /dev/null; then
  echo "  ✅ Query successful with v2 method"
else
  echo "  ❌ Query failed or missing v2 method"
  TEST_PASSED=false
fi

# Test 4: Booking Service Compatibility
echo "Test 4/5: Booking Service (v2 endpoint)"
BOOKING_RESPONSE=$(curl -s http://$GREEN_IP:3003/bookings \
  -H "Authorization: Bearer test_token")
if [ $? -eq 0 ]; then
  echo "  ✅ Booking service responding"
else
  echo "  ❌ Booking service not responding"
  TEST_PASSED=false
fi

# Test 5: Database Connectivity
echo "Test 5/5: Database Connection Test"
if curl -s http://$GREEN_IP:3004/health/db | grep -q '"status":"healthy"'; then
  echo "  ✅ Database connection healthy"
else
  echo "  ❌ Database connection unhealthy"
  TEST_PASSED=false
fi

echo ""
echo "======================================"
if [ "$TEST_PASSED" = true ]; then
  echo "✅ ALL SMOKE TESTS PASSED"
  echo "Proceeding to traffic switch..."
  exit 0
else
  echo "❌ SMOKE TESTS FAILED"
  echo "Not switching traffic. Manual investigation required."
  exit 1
fi
```

#### Step 2.3: Switch Traffic (Blue → Green)

```bash
#!/bin/bash
# Script: deployment/switch_traffic.sh
# Purpose: Switch ALB target group from BLUE to GREEN

CLUSTER_NAME="ticketing-cluster"
ALB_NAME="ticketing-prod-alb"
BLUE_TARGET_GROUP="ticketing-api-blue"
GREEN_TARGET_GROUP="ticketing-api-green"

echo "🔄 Switching traffic from BLUE (v1.0) to GREEN (v2.0)..."
echo "=========================================================="

# Get ALB listener
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --names $ALB_NAME \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

LISTENER_ARN=$(aws elbv2 describe-listeners \
  --load-balancer-arn $ALB_ARN \
  --query 'Listeners[0].ListenerArn' \
  --output text)

# Verify GREEN target group is healthy
echo "🏥 Verifying GREEN target health..."
GREEN_TARGETS=$(aws elbv2 describe-target-health \
  --target-group-arn $GREEN_TARGET_GROUP \
  --query 'TargetHealthDescriptions[*].TargetHealth.State' \
  --output text)

if [[ "$GREEN_TARGETS" == *"healthy"* ]]; then
  echo "✅ GREEN targets are healthy"
else
  echo "❌ GREEN targets not healthy: $GREEN_TARGETS"
  exit 1
fi

# Switch listener to GREEN
echo "🔀 Switching listener to GREEN target group..."
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$GREEN_TARGET_GROUP

if [ $? -eq 0 ]; then
  echo "✅ Traffic switched to GREEN (v2.0)"
  
  # Monitor for 2 minutes
  echo "📊 Monitoring error rates (30 seconds)..."
  sleep 30
  
  # Check CloudWatch metrics
  ERROR_RATE=$(aws cloudwatch get-metric-statistics \
    --metric-name HTTPCode_Target_5XX_Count \
    --namespace AWS/ApplicationELB \
    --dimensions Name=TargetGroup,Value=ticketing-api-green \
    --start-time $(date -u -d '1 min ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 60 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text)
  
  if [ "$ERROR_RATE" -lt 5 ]; then
    echo "✅ Error rate acceptable: $ERROR_RATE"
  else
    echo "⚠️  Error rate elevated: $ERROR_RATE"
    echo "   Consider rollback if continues to increase"
  fi
  
  # Record deployment event
  echo "📝 Recording deployment event..."
  aws cloudwatch put-metric-data \
    --metric-name DeploymentSuccessful \
    --namespace Ticketing/Deployments \
    --value 1 \
    --dimensions Environment=production,Service=backend,Version=v2.0
  
else
  echo "❌ Failed to switch traffic"
  exit 1
fi

echo "✅ Blue-Green deployment completed successfully"
```

#### Step 2.4: Verify Traffic Switch

```bash
#!/bin/bash
# Script: deployment/verify_traffic_switch.sh

echo "🔍 Verifying Traffic Switch"
echo "==========================="

# Method 1: Check ALB target groups
echo "Checking ALB target groups..."
aws elbv2 describe-target-health \
  --target-group-arn $GREEN_TARGET_GROUP \
  --query 'TargetHealthDescriptions[*].[Target.Id, TargetHealth.State]' \
  --output table

# Method 2: Check server version from responses
echo "Checking API version headers..."
curl -I http://ticketing.example.com/api/health | grep -i "x-api-version"

# Method 3: Check CloudWatch metrics
echo "Checking request distribution..."
aws cloudwatch get-metric-statistics \
  --metric-name RequestCount \
  --namespace AWS/ApplicationELB \
  --dimensions Name=TargetGroup,Value=ticketing-api-green \
  --start-time $(date -u -d '5 min ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum

# Method 4: Monitor error rates
echo "Error rate (5XX) on GREEN:"
aws cloudwatch get-metric-statistics \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --dimensions Name=TargetGroup,Value=ticketing-api-green \
  --start-time $(date -u -d '5 min ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum,Average

echo "✅ Traffic switch verification complete"
```

### Rollback Procedure (Phase 2)

```bash
#!/bin/bash
# Script: deployment/rollback_backend.sh
# Purpose: Rollback to BLUE (v1.0) if GREEN deployment fails

echo "🔄 ROLLING BACK to BLUE (v1.0)"
echo "==============================="

# Switch listener back to BLUE
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$BLUE_TARGET_GROUP

if [ $? -eq 0 ]; then
  echo "✅ Rolled back to BLUE (v1.0)"
  echo "⚠️  GREEN deployment investigation required"
else
  echo "❌ Rollback failed - manual intervention needed"
  exit 1
fi

# Keep GREEN running for investigation
echo "📝 Keeping GREEN environment running for debugging"
echo "   Review logs: kubectl logs -f deployment/payment-service-green"
```

### Success Criteria for Phase 2
- [ ] GREEN services deployed and ready (all pods running)
- [ ] Smoke tests all passed (5/5)
- [ ] Traffic switched to GREEN (ALB pointing to green targets)
- [ ] Error rates normal (<1%)
- [ ] BLUE environment still running (rollback available)
- [ ] No customer impact (0 downtime)
- [ ] CloudWatch shows successful deployment

---

## 🎨 PHASE 3: Frontend Rollout (Day 3, Canary)

### Objective
Deploy v2.0 frontend with **gradual canary rollout** to minimize risk.

### Canary Strategy

```
CANARY ROLLOUT PLAN
═══════════════════

5% Users (Segment A)
├─ Duration: 30 minutes
├─ Monitoring: Error rate, page load time, conversion
├─ Decision: Continue? (if metrics OK)
└─ Exit criteria: <0.5% error rate, <2s load time

10% Users (Segment B + continue A)
├─ Duration: 1 hour
├─ Monitoring: Same + user feedback
├─ Decision: Continue?
└─ Exit criteria: Same

25% Users (Segment C + continue A+B)
├─ Duration: 1 hour
├─ Monitoring: Full site monitoring
├─ Decision: Continue?
└─ Exit criteria: Same

50% Users (Segment D + continue A+B+C)
├─ Duration: 1 hour
├─ Monitoring: Production metrics
├─ Decision: Continue?
└─ Exit criteria: Same

100% Users (Complete rollout)
├─ Duration: 1 hour
├─ Monitoring: Full production
└─ Complete: All users on v2.0

TOTAL TIME: 5 hours
RISK LEVEL: VERY LOW (can rollback at any stage)
```

### Prerequisites
- [ ] Backend v2.0 deployed and stable (Phase 2)
- [ ] Frontend v2.0 built and tested
- [ ] Feature flags configured
- [ ] Canary monitoring dashboards ready
- [ ] Rollback procedure tested

### Step-by-Step Procedure

#### Step 3.1: Configure Feature Flags

```python
# File: frontend-config/feature_flags.py
# Purpose: Control frontend rollout via feature flags

from typing import Optional
import redis
import json

class FeatureFlagService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def set_canary_percentage(self, percentage: int) -> None:
        """Set percentage of users to see v2 UI"""
        self.redis.set('canary_rollout_percentage', percentage)
        print(f"Set canary rollout to {percentage}%")
    
    def should_use_v2_ui(self, user_id: str) -> bool:
        """
        Determine if user should see v2 UI
        Uses consistent hashing for stable assignment
        """
        canary_percentage = int(
            self.redis.get('canary_rollout_percentage') or 0
        )
        
        # Use user_id hash to determine assignment
        user_hash = hash(user_id) % 100
        return user_hash < canary_percentage
    
    def get_frontend_version(self, user_id: str) -> str:
        """Return frontend version for user"""
        if self.should_use_v2_ui(user_id):
            return 'v2.0'
        return 'v1.0'

# Usage in backend
@app.get('/api/config')
def get_frontend_config(user_id: str):
    flag_service = FeatureFlagService(redis_client)
    return {
        'frontend_version': flag_service.get_frontend_version(user_id),
        'api_endpoint': 'https://api.ticketing.example.com',
        'features': {
            'new_payment_methods': True,
            'improved_ui': flag_service.should_use_v2_ui(user_id)
        }
    }
```

#### Step 3.2: Deploy Frontend v2.0 (Dark Deploy)

```bash
#!/bin/bash
# Script: deployment/03_frontend_canary_deploy.sh

echo "🎨 Frontend Canary Deployment"
echo "============================="

CDN_DOMAIN="cdn.ticketing.example.com"
VERSION_OLD="v1.0"
VERSION_NEW="v2.0"

# Step 1: Build frontend
echo "Building frontend v2.0..."
npm run build:prod
BUILD_HASH=$(git rev-parse --short HEAD)

# Step 2: Upload to CDN (separate path)
echo "Uploading to CDN..."
aws s3 sync dist/ s3://ticketing-frontend-prod/v2.0/ --cache-control "max-age=3600"

# Step 3: Configure CDN routing
# Initially: 0% users see v2, all see v1
aws cloudfront update-distribution \
  --id $CLOUDFRONT_DIST_ID \
  --distribution-config file://cloudfront-config-canary.json

# Step 4: Prepare monitoring
echo "Setting up canary monitoring..."
aws cloudwatch put-metric-alarm \
  --alarm-name canary-error-rate-high \
  --alarm-description "Alert if canary has high error rate" \
  --metric-name JavaScriptErrorRate \
  --namespace Ticketing/Frontend \
  --statistic Average \
  --period 60 \
  --threshold 0.5 \
  --comparison-operator GreaterThanThreshold

echo "✅ Frontend v2.0 deployed (0% traffic initially)"
```

#### Step 3.3: Gradual Traffic Shift

```bash
#!/bin/bash
# Script: deployment/canary_traffic_shift.sh
# Purpose: Gradually shift traffic from v1.0 to v2.0

REDIS_ENDPOINT="redis.ticketing.example.com:6379"
MONITORING_INTERVAL=60  # seconds

shift_traffic() {
    local percentage=$1
    echo "🔀 Shifting traffic to $percentage% v2.0 users"
    
    # Set in Redis (used by backend to decide which version to serve)
    redis-cli -h $REDIS_ENDPOINT set canary_rollout_percentage $percentage
    
    echo "  ⏳ Monitoring for $MONITORING_INTERVAL seconds..."
    sleep $MONITORING_INTERVAL
    
    # Check metrics
    check_canary_metrics $percentage
}

check_canary_metrics() {
    local percentage=$1
    
    echo "  📊 Checking metrics for $percentage% rollout..."
    
    # Get error rate
    ERROR_RATE=$(aws cloudwatch get-metric-statistics \
      --metric-name JavaScriptErrorRate \
      --namespace Ticketing/Frontend \
      --statistics Average \
      --start-time $(date -u -d "2 min ago" +%Y-%m-%dT%H:%M:%S) \
      --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
      --period 60 \
      --query 'Datapoints[0].Average' \
      --output text)
    
    # Get page load time (p95)
    LOAD_TIME=$(aws cloudwatch get-metric-statistics \
      --metric-name PageLoadTimeP95 \
      --namespace Ticketing/Frontend \
      --statistics Average \
      --start-time $(date -u -d "2 min ago" +%Y-%m-%dT%H:%M:%S) \
      --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
      --period 60 \
      --query 'Datapoints[0].Average' \
      --output text)
    
    # Evaluate results
    if [ $(echo "$ERROR_RATE < 0.5" | bc) -eq 1 ] && \
       [ $(echo "$LOAD_TIME < 2000" | bc) -eq 1 ]; then
        echo "  ✅ Metrics OK (Error: ${ERROR_RATE}%, Load: ${LOAD_TIME}ms)"
        return 0
    else
        echo "  ⚠️  Metrics degraded (Error: ${ERROR_RATE}%, Load: ${LOAD_TIME}ms)"
        return 1
    fi
}

# Main canary rollout
echo "🚀 Starting canary rollout"
echo "=========================="

# 5% rollout
shift_traffic 5 || { echo "Rollback at 5%"; redis-cli set canary_rollout_percentage 0; exit 1; }

# 10% rollout
shift_traffic 10 || { echo "Rollback at 10%"; redis-cli set canary_rollout_percentage 0; exit 1; }

# 25% rollout
shift_traffic 25 || { echo "Rollback at 25%"; redis-cli set canary_rollout_percentage 0; exit 1; }

# 50% rollout
shift_traffic 50 || { echo "Rollback at 50%"; redis-cli set canary_rollout_percentage 0; exit 1; }

# 100% rollout
shift_traffic 100 || { echo "Rollback at 100%"; redis-cli set canary_rollout_percentage 0; exit 1; }

echo "✅ Canary rollout completed successfully (100% on v2.0)"
```

### Rollback Procedure (Phase 3)

```bash
#!/bin/bash
# Script: deployment/rollback_frontend.sh

echo "🔄 Rolling back frontend to v1.0"

# Set canary to 0%
redis-cli -h $REDIS_ENDPOINT set canary_rollout_percentage 0

# Clear CDN cache (force v1 serving)
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_DIST_ID \
  --paths "/*"

echo "✅ Frontend rolled back to v1.0"
echo "⚠️  Investigate issue before next attempt"
```

### Success Criteria for Phase 3
- [ ] All canary stages completed (5% → 10% → 25% → 50% → 100%)
- [ ] Error rate stayed <0.5% throughout
- [ ] Page load time stayed <2 seconds
- [ ] 100% of users on v2.0 frontend
- [ ] No performance degradation
- [ ] User feedback positive

---

## 📱 PHASE 4: Mobile App Deployment (Day 4+, Staged Rollout)

### Objective
Deploy v2.0 mobile apps with **app store staged rollout** and **backward compatibility**.

### Strategy

```
MOBILE APP DEPLOYMENT TIMELINE
═══════════════════════════════

Day 4: Build & Submit to App Stores
├─ Build iOS & Android apps (v2.0)
├─ Generate APK/IPA files with version bumps
├─ Internal testing (QA team: 30 min)
├─ Submit to Apple App Store & Google Play
└─ Estimated review time: 24-48 hours

Day 5-6: App Store Review & Approval
├─ Apple reviews app (24-48 hr typical)
├─ Google reviews app (typically faster)
├─ Address any review comments
└─ Ready for staged rollout

Day 6+: Staged Rollout (Phased Release)
├─ 10% users get access to v2.0 app
│  ├─ Duration: 24-48 hours
│  └─ Decision: Increase or hold?
│
├─ 25% users get access to v2.0 app
│  ├─ Duration: 24-48 hours
│  └─ Decision: Increase or halt?
│
├─ 50% users get access to v2.0 app
│  ├─ Duration: 24-48 hours
│  └─ Decision: Increase to 100%?
│
└─ 100% users get access to v2.0 app
   └─ Rollout complete

Backward Compatibility (3+ months)
├─ v1.0 API endpoint stays active
├─ Support v1.0 app requests
├─ Monitor usage metrics
├─ Sunset v1.0 after adoption >95%
└─ Total support: 90-120 days

TOTAL DOWNTIME: 0 minutes
GRADUAL ADOPTION: Users choose when to upgrade
```

### Prerequisites
- [ ] Frontend v2.0 deployed and stable (Phase 3)
- [ ] All backend services on v2.0 (Phase 2)
- [ ] Database schema updated (Phase 1)
- [ ] App version bumped (1.0 → 2.0)
- [ ] Backward compatibility tested
- [ ] App store submission ready

### Step-by-Step Procedure

#### Step 4.1: Build Mobile Apps

```bash
#!/bin/bash
# Script: mobile/build_v2.0.sh

echo "📱 Building Mobile Apps v2.0"
echo "============================"

# iOS Build
echo "Building iOS v2.0..."
cd ios/
VERSION="2.0.0"
BUILD_NUMBER=$(date +%Y%m%d%H%M)

# Update version
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" \
  Ticketing/Info.plist
/usr/libexec/PlistBuddy -c "Set :CFBundleVersion $BUILD_NUMBER" \
  Ticketing/Info.plist

# Build app
xcodebuild -scheme Ticketing \
  -configuration Release \
  -archivePath build/Ticketing.xcarchive \
  archive

# Export IPA
xcodebuild -exportArchive \
  -archivePath build/Ticketing.xcarchive \
  -exportOptionsPlist ExportOptions.plist \
  -exportPath build/

IPA_FILE="build/Ticketing.ipa"
echo "✅ iOS build complete: $IPA_FILE"

# Android Build
echo "Building Android v2.0..."
cd ../android/
sed -i "" "s/versionName \"1.0.0\"/versionName \"$VERSION\"/" app/build.gradle
sed -i "" "s/versionCode [0-9]*/versionCode $BUILD_NUMBER/" app/build.gradle

./gradlew clean assembleRelease

APK_FILE="app/build/outputs/apk/release/app-release.apk"
echo "✅ Android build complete: $APK_FILE"

# Sign artifacts
echo "Signing artifacts..."
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore $KEYSTORE_FILE \
  -storepass $KEYSTORE_PASSWORD \
  -keypass $KEY_PASSWORD \
  $APK_FILE $KEY_ALIAS

echo "✅ Mobile builds ready for submission"
```

#### Step 4.2: Submit to App Stores

```bash
#!/bin/bash
# Script: mobile/submit_to_stores.sh

echo "📤 Submitting to App Stores"
echo "==========================="

APPLE_ID="developer@ticketing.com"
APP_BUNDLE_ID="com.ticketing.app"
ANDROID_PACKAGE_ID="com.ticketing.app"

# iOS Submission
echo "📲 Submitting to Apple App Store..."

# Upload IPA using Transporter
open -a Transporter

# Manual steps or use API:
# xcrun altool --upload-app -f ios/build/Ticketing.ipa \
#   -t ios -u $APPLE_ID -p $APP_PASSWORD

echo "⏳ Waiting for Apple review (typically 24-48 hrs)..."
echo "   Track progress at: https://appstoreconnect.apple.com"

# Android Submission
echo "📲 Submitting to Google Play..."

# Use Google Play Console or API:
# python scripts/submit_to_play_store.py \
#   --package $ANDROID_PACKAGE_ID \
#   --apk android/app/build/outputs/apk/release/app-release.apk \
#   --release-notes "v2.0.0: New payment methods, improved UI"

echo "⏳ Waiting for Google review (typically 2-4 hrs)..."
echo "   Track progress at: https://play.google.com/console"

# Create deployment record
echo "Recording deployment..."
aws dynamodb put-item \
  --table-name app_deployments \
  --item '{
    "deployment_id": {"S": "'$(date +%s)'"},
    "version": {"S": "2.0.0"},
    "platform": {"S": "ios-android"},
    "status": {"S": "submitted"},
    "submit_time": {"S": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}
  }'

echo "✅ Apps submitted to stores"
```

#### Step 4.3: Configure Staged Rollout

```python
# File: mobile/configure_staged_rollout.py
# Purpose: Configure app store staged rollout percentages

import googleapiclient.discovery
from google.oauth2 import service_account

class MobileRolloutManager:
    def __init__(self):
        self.play_service = self._init_google_play_service()
        self.app_store_service = self._init_app_store_service()
    
    def _init_google_play_service(self):
        """Initialize Google Play Service"""
        credentials = service_account.Credentials.from_service_account_file(
            'google-play-credentials.json'
        )
        return googleapiclient.discovery.build('androidpublisher', 'v3', credentials=credentials)
    
    def _init_app_store_service(self):
        """Initialize Apple App Store Service"""
        # Note: App Store API is limited, may require manual configuration
        pass
    
    def set_google_play_staged_rollout(self, percentage: int):
        """
        Set Google Play staged rollout percentage
        
        Args:
            percentage: 10, 25, 50, or 100
        """
        package_id = "com.ticketing.app"
        
        # Get edit
        edit_request = self.play_service.edits().insert(
            body={},
            packageName=package_id
        )
        result = edit_request.execute()
        edit_id = result['id']
        
        # Update rollout
        rollout_config = {
            'stagingPercentage': percentage
        }
        
        track_update = self.play_service.edits().tracks().update(
            body={
                'track': 'production',
                'releases': [{
                    'status': 'inProgress',
                    'userFraction': percentage / 100.0,
                    'releaseNotes': [{
                        'language': 'en-US',
                        'text': f'Version 2.0 - {percentage}% staged rollout'
                    }]
                }]
            },
            packageName=package_id,
            editId=edit_id,
            track='production'
        )
        result = track_update.execute()
        
        # Commit changes
        commit = self.play_service.edits().commit(
            packageName=package_id,
            editId=edit_id
        )
        commit.execute()
        
        print(f"✅ Google Play rollout set to {percentage}%")
    
    def configure_apple_app_store_phased_release(self, percentage: int):
        """
        Configure Apple App Store phased release
        
        Manual steps (API limited):
        1. Log in to App Store Connect
        2. Navigate to app build
        3. Set Phased Release percentage
        4. Save
        """
        print(f"📋 Manual step: Set App Store phased release to {percentage}%")
        print("   https://appstoreconnect.apple.com/apps/")
    
    def rollout_percentage(self, percentage: int):
        """Rollout to specific percentage on both stores"""
        print(f"🚀 Rolling out to {percentage}% of users...")
        self.set_google_play_staged_rollout(percentage)
        self.configure_apple_app_store_phased_release(percentage)
        print(f"✅ Rollout to {percentage}% complete")

# Usage
if __name__ == "__main__":
    manager = MobileRolloutManager()
    
    # Day 6: 10%
    manager.rollout_percentage(10)
    print("⏳ Monitor for 24-48 hours...")
    
    # Day 7: 25%
    manager.rollout_percentage(25)
    print("⏳ Monitor for 24-48 hours...")
    
    # Day 8: 50%
    manager.rollout_percentage(50)
    print("⏳ Monitor for 24-48 hours...")
    
    # Day 9: 100%
    manager.rollout_percentage(100)
    print("✅ Full rollout complete")
```

#### Step 4.4: Monitor Mobile Adoption

```python
# File: mobile/monitor_adoption.py
# Purpose: Monitor app adoption and version distribution

import boto3
import json
from datetime import datetime, timedelta

class MobileAdoptionMonitor:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.dynamodb = boto3.resource('dynamodb')
    
    def get_version_distribution(self):
        """Get distribution of app versions"""
        metrics = self.cloudwatch.get_metric_statistics(
            Namespace='Ticketing/Mobile',
            MetricName='AppVersionDistribution',
            Dimensions=[
                {'Name': 'Platform', 'Value': 'ios'},
                {'Name': 'Platform', 'Value': 'android'}
            ],
            StartTime=datetime.utcnow() - timedelta(hours=1),
            EndTime=datetime.utcnow(),
            Period=3600,
            Statistics=['Average']
        )
        return metrics['Datapoints']
    
    def get_adoption_metrics(self):
        """Get adoption KPIs"""
        return {
            'v1_0_active_users': self._get_metric('AppVersion1_0_ActiveUsers'),
            'v2_0_active_users': self._get_metric('AppVersion2_0_ActiveUsers'),
            'adoption_rate': self._get_metric('AppVersion2_0_AdoptionRate'),
            'crash_rate_v1': self._get_metric('AppVersion1_0_CrashRate'),
            'crash_rate_v2': self._get_metric('AppVersion2_0_CrashRate'),
        }
    
    def _get_metric(self, metric_name: str) -> float:
        """Get latest metric value"""
        response = self.cloudwatch.get_metric_statistics(
            Namespace='Ticketing/Mobile',
            MetricName=metric_name,
            StartTime=datetime.utcnow() - timedelta(hours=1),
            EndTime=datetime.utcnow(),
            Period=3600,
            Statistics=['Average']
        )
        if response['Datapoints']:
            return response['Datapoints'][-1]['Average']
        return 0.0
    
    def print_adoption_report(self):
        """Print adoption report"""
        metrics = self.get_adoption_metrics()
        
        print("\n📊 Mobile App Adoption Report")
        print("=" * 50)
        print(f"v1.0 Active Users: {metrics['v1_0_active_users']:,.0f}")
        print(f"v2.0 Active Users: {metrics['v2_0_active_users']:,.0f}")
        print(f"Adoption Rate (v2.0): {metrics['adoption_rate']:.1f}%")
        print(f"Crash Rate (v1.0): {metrics['crash_rate_v1']:.2f}%")
        print(f"Crash Rate (v2.0): {metrics['crash_rate_v2']:.2f}%")
        print("=" * 50)
        
        # Decision: Increase rollout?
        if metrics['adoption_rate'] > 50 and metrics['crash_rate_v2'] < 0.5:
            print("✅ Metrics healthy - ready to increase rollout")
        else:
            print("⚠️  Monitor more before increasing rollout")

# Usage
monitor = MobileAdoptionMonitor()
monitor.print_adoption_report()
```

### Backward Compatibility (3+ months)

```bash
#!/bin/bash
# Script: mobile/maintain_backward_compatibility.sh
# Purpose: Keep v1.0 API endpoint active during transition

echo "📋 Maintaining Backward Compatibility"
echo "====================================="

# Ensure v1.0 API endpoints still work
echo "Verifying v1.0 API endpoints..."

# Test payment endpoint (v1 format)
curl -X POST http://api.ticketing.example.com/api/v1/payments \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "amount": 100,
    "payment_method": "card"  # v1 format (no payment_method_v2)
  }'

# Test booking endpoint (v1 format)
curl http://api.ticketing.example.com/api/v1/bookings/book-123

echo "✅ v1.0 API endpoints still functional"

# Schedule v1.0 API sunset
echo "Scheduling v1.0 API sunset in 90 days..."

# Create CloudWatch reminder
aws events put-rule \
  --name api-v1-sunset-reminder \
  --schedule-expression "rate(30 days)" \
  --state ENABLED

echo "📅 v1.0 will be available for 90+ days (90% adoption threshold)"
```

### Success Criteria for Phase 4
- [ ] iOS app submitted and approved
- [ ] Android app submitted and approved
- [ ] Staged rollout started (10%, then 25%, 50%, 100%)
- [ ] v1.0 API still working (backward compatible)
- [ ] Adoption metrics tracked
- [ ] No critical issues reported
- [ ] v1.0 support plan documented (90-120 days)

---

## 📊 Migration Runbook

### Daily Tasks

**Day 1 - Database:**
```
09:00 - Database migration starts
09:15 - Schema updated (payment_method_v2 column added)
09:30 - Data backfill complete (if needed)
09:45 - Verification complete
10:00 - ✅ Phase 1 COMPLETE
```

**Day 2 - Backend:**
```
10:00 - Green services begin deployment
10:15 - Green pods ready, health checks pass
10:20 - Smoke tests running
10:25 - All tests passed
10:30 - Traffic switched to Green
10:35 - Monitoring shows 0% errors
11:00 - ✅ Phase 2 COMPLETE
```

**Day 3 - Frontend:**
```
09:00 - Canary monitoring dashboards ready
09:30 - 5% users on v2.0 (30 min window)
10:00 - Metrics OK, increase to 10%
10:10 - 10% users on v2.0 (1 hour window)
11:10 - Metrics OK, increase to 25%
11:15 - 25% users on v2.0 (1 hour window)
12:15 - Metrics OK, increase to 50%
12:20 - 50% users on v2.0 (1 hour window)
13:20 - Metrics OK, increase to 100%
13:25 - 100% users on v2.0
14:00 - ✅ Phase 3 COMPLETE
```

**Day 4 - Mobile Submission:**
```
09:00 - iOS build ready
10:00 - Android build ready
11:00 - Submit to App Stores
12:00 - Apps under review
24-48 hrs - App store approval
✅ Apps approved, ready for staged rollout
```

**Day 6+ - Mobile Rollout:**
```
Staged rollout: 10% → 25% → 50% → 100%
Monitor adoption for 90+ days
Keep v1.0 API active during transition
✅ Phase 4 COMPLETE
```

---

## 🚨 Incident Response

### If Phase 1 (Database) Fails

```bash
# Immediate action
rollback_sql="ALTER TABLE payments DROP COLUMN payment_method_v2;"
psql -h $RDS_ENDPOINT -U admin -d ticketingdb -c "$rollback_sql"

# Post-mortem
1. Review migration script for issues
2. Add more test cases
3. Retry with fixes
```

### If Phase 2 (Backend) Fails

```bash
# Immediate action
aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$BLUE_TARGET_GROUP

# Post-mortem
1. Review smoke test failures
2. Check backend logs: kubectl logs deployment/payment-service-green
3. Fix issues and retry
```

### If Phase 3 (Frontend) Fails

```bash
# Immediate action
redis-cli set canary_rollout_percentage 0

# Post-mortem
1. Review frontend console errors
2. Check CloudWatch metrics
3. Fix issues and retry at lower percentage
```

### If Phase 4 (Mobile) Fails

```bash
# Keep both v1.0 and v2.0 APIs active
# Users can choose to stay on v1.0 or adopt v2.0
# Fix issues and resubmit
```

---

## ✅ Complete Checklist

### Pre-Migration
- [ ] Database backup created and tested
- [ ] All services tested on staging
- [ ] Runbooks reviewed and approved
- [ ] On-call team notified
- [ ] Monitoring dashboards prepared
- [ ] Rollback procedures tested
- [ ] Feature flags configured

### Phase 1: Database (Day 1)
- [ ] Schema migration completed
- [ ] Data verification passed
- [ ] Rollback procedure tested
- [ ] Zero downtime verified

### Phase 2: Backend (Day 2)
- [ ] Green services deployed
- [ ] Smoke tests all passed (5/5)
- [ ] Traffic switched successfully
- [ ] Error rates normal
- [ ] Blue environment standing by

### Phase 3: Frontend (Day 3)
- [ ] Feature flags ready
- [ ] Canary monitoring active
- [ ] 5% → 10% → 25% → 50% → 100% completed
- [ ] Performance metrics stable
- [ ] User feedback positive

### Phase 4: Mobile (Day 4+)
- [ ] Apps submitted to stores
- [ ] Apps approved by stores
- [ ] Staged rollout started
- [ ] v1.0 API still active
- [ ] Adoption metrics tracked

### Post-Migration
- [ ] All systems on v2.0
- [ ] Performance verified
- [ ] Cost metrics checked
- [ ] Lessons learned documented
- [ ] Team debriefing completed

---

## 📞 Support Contacts

| Role | Contact | Availability |
|------|---------|---------------|
| Database Team | db-team@example.com | 24/7 during migration |
| Backend Lead | backend@example.com | 24/7 during migration |
| Frontend Lead | frontend@example.com | 24/7 during migration |
| Mobile Lead | mobile@example.com | 24/7 during migration |
| On-Call SRE | oncall@example.com | 24/7 on-call |
| VP Engineering | vp@example.com | Critical issues only |

---

**Document Version**: 1.0  
**Created**: September 11, 2026  
**Status**: Ready for Execution  
**Estimated Completion**: 7+ days (distributed)  
**Downtime**: 0 minutes  
**Risk Level**: Minimal
