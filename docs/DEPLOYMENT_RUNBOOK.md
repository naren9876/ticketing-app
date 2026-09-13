# Deployment Runbook

## Overview
This runbook provides step-by-step instructions for deploying the Ticketing App.

## Pre-Deployment Checklist

- [ ] Code reviewed and approved
- [ ] All tests passing (unit, integration, smoke)
- [ ] Security scans passed (7 gates)
- [ ] Change ticket created (ServiceNow)
- [ ] CAB approval received
- [ ] Backup database
- [ ] Notify on-call team
- [ ] Incident commander assigned

## Phase 1: Database Migration

**Duration:** 30 minutes  
**Risk Level:** Medium  
**Rollback Time:** 15 minutes

### Steps
1. Create new database column (nullable)
2. Backfill existing data (batch size: 5000)
3. Deploy new application version
4. Monitor replication lag
5. Verify all data copied

### Success Criteria
- ✅ Zero downtime
- ✅ All rows migrated
- ✅ No data loss
- ✅ Replication lag < 1 second

### Rollback Procedure
```bash
./scripts/rollback_phase_1.sh
```

---

## Phase 2: Backend Deployment (Blue-Green)

**Duration:** 1 hour  
**Risk Level:** Low  
**Rollback Time:** 30 seconds

### Steps
1. Deploy v2.0 to green environment
2. Run 5 smoke tests
3. Monitor metrics for 5 minutes
4. Switch ALB traffic to green
5. Monitor for 10 minutes
6. Keep blue environment for 24 hours

### Success Criteria
- ✅ All 5 smoke tests pass
- ✅ Error rate < 0.5%
- ✅ Latency p95 < 2000ms
- ✅ No customer impact

### Rollback Procedure
```bash
./scripts/rollback_phase_2.sh
```

---

## Phase 3: Frontend Deployment (Canary)

**Duration:** 50 minutes  
**Risk Level:** Low  
**Rollback Time:** 1 minute

### Canary Rollout Schedule
- 5%:   10 minutes (traffic sample)
- 10%:  10 minutes (larger sample)
- 25%:  10 minutes (quarter traffic)
- 50%:  10 minutes (half traffic)
- 100%: Complete

### Success Criteria per Stage
- ✅ Error rate < 0.5%
- ✅ Page load < 3000ms
- ✅ JS errors < 0.5%
- ✅ No critical alerts

### Automatic Rollback
If any metric exceeds threshold:
- Set Redis canary flag to 0
- Revert to v1.0 UI
- Rollback time: 60 seconds

---

## Phase 4: Mobile Deployment

**Duration:** 1-2 hours (per platform)  
**Risk Level:** Medium  
**Rollback Time:** 1-2 hours (app store)

### iOS Deployment
1. Build with Xcode
2. Sign with certificate
3. Submit to App Store
4. Use TestFlight for beta

### Android Deployment
1. Build with Gradle
2. Sign release APK
3. Submit to Google Play
4. Use beta track for testing

---

## Incident Response

### If Something Goes Wrong

1. **Immediate:** Trigger automatic rollback (if enabled)
2. **5 minutes:** Notify incident commander
3. **10 minutes:** Brief on-call team
4. **15 minutes:** Assess impact
5. **Document:** Create incident ticket

### Who to Notify
- On-call engineer: [PagerDuty]
- Manager: [Email/Slack]
- Leadership: [Optional, if critical]

---

## Post-Deployment

1. Monitor for 72 hours
2. Check all critical flows
3. Review metrics vs SLOs
4. Document any issues
5. Schedule retrospective

---

## Useful Commands

```bash
# Check deployment status
kubectl rollout status deployment/ticketing-api

# View logs
kubectl logs -f deployment/ticketing-api

# Rollback last deployment
kubectl rollout undo deployment/ticketing-api

# Check metrics
aws cloudwatch get-metric-statistics ...

# View audit trail
python3 monitoring/audit_trail.py
```

---

## Approval

- [ ] Deployment Owner: ___________  Date: ________
- [ ] Engineering Lead: ___________  Date: ________
- [ ] Operations Lead: ___________  Date: ________
