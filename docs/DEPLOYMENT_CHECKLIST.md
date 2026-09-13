# Pre-Deployment Checklist

## 24 Hours Before Deployment

- [ ] Code review complete
- [ ] All PR approvals received
- [ ] Merge to main branch
- [ ] Schedule deployment time
- [ ] Notify stakeholders

## 2 Hours Before Deployment

- [ ] Create change ticket (ServiceNow)
- [ ] Request CAB approval
- [ ] Backup database
- [ ] Notify on-call team
- [ ] Set incident commander

## 1 Hour Before Deployment

- [ ] Final smoke test in staging
- [ ] Verify CI/CD pipeline
- [ ] Test rollback procedure
- [ ] Check all monitoring dashboards
- [ ] Team standup (all on call)

## At Deployment Start

- [ ] Verify CAB approval
- [ ] Begin Phase 1 (database)
- [ ] Monitor metrics continuously
- [ ] Communicate progress

## Post-Deployment

- [ ] All phases complete
- [ ] Verify v2.0 live in production
- [ ] Customer-facing tests
- [ ] Monitor error rate < 0.5%
- [ ] Monitor latency < 2000ms p95

## 72-Hour Monitoring

- [ ] No critical incidents
- [ ] All SLOs met
- [ ] Customer satisfaction confirmed
- [ ] Close deployment ticket
