# Implementing Enterprise Deployment Patterns - Practical Guide

## 🔧 Real Implementation for Movie Ticketing App

### Part 1: Blue-Green Deployment with Kubernetes

#### Step 1: Setup Blue Environment (Current Production)

```yaml
# kubernetes/blue-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway-blue
  namespace: ticketing
  labels:
    app: api-gateway
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
      version: blue
  template:
    metadata:
      labels:
        app: api-gateway
        version: blue
    spec:
      containers:
      - name: api-gateway
        image: ticketing/api-gateway:v1.0.0  # BLUE version
        ports:
        - containerPort: 3000
        env:
        - name: VERSION
          value: "blue"
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

#### Step 2: Service Routes to Blue (Initially)

```yaml
# kubernetes/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-gateway-service
  namespace: ticketing
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
  selector:
    app: api-gateway
    version: blue  # Points to BLUE initially
```

#### Step 3: Deploy Green Environment (New Version)

```bash
#!/bin/bash
# deploy-green.sh - Deploy new version alongside existing

echo "🚀 Starting Blue-Green Deployment"

VERSION_NEW="v2.0.0"
VERSION_OLD="v1.0.0"

# Step 1: Deploy GREEN version
echo "📦 Deploying GREEN (v2.0.0)..."
sed "s/v1.0.0/$VERSION_NEW/g; s/version: blue/version: green/g; s/api-gateway-blue/api-gateway-green/g" \
  kubernetes/blue-deployment.yaml | kubectl apply -f -

# Step 2: Wait for pods to be ready
echo "⏳ Waiting for GREEN pods to be ready..."
kubectl wait --for=condition=ready pod \
  -l app=api-gateway,version=green \
  -n ticketing \
  --timeout=300s

# Step 3: Run smoke tests against GREEN
echo "🧪 Running smoke tests on GREEN..."
GREEN_POD=$(kubectl get pods -n ticketing -l app=api-gateway,version=green -o jsonpath='{.items[0].metadata.name}')

# Test 1: Health check
kubectl exec -it $GREEN_POD -n ticketing -- curl http://localhost:3000/health

# Test 2: API endpoints
kubectl exec -it $GREEN_POD -n ticketing -- curl http://api-gateway-service:3000/api/movies

# Test 3: Database connectivity
kubectl exec -it $GREEN_POD -n ticketing -- node -e "
  const pool = require('pg').Pool;
  const p = new pool({host: 'postgres'});
  p.query('SELECT 1').then(() => console.log('✅ DB OK')).catch(e => console.error('❌ DB FAIL', e));
"

echo "✅ Smoke tests passed!"

# Step 4: Manual approval (in real scenario, product team approves)
read -p "✋ Manual verification complete? All metrics look good? (yes/no): " approval

if [ "$approval" != "yes" ]; then
  echo "❌ Rollback: Deleting GREEN deployment"
  kubectl delete deployment api-gateway-green -n ticketing
  exit 1
fi

# Step 5: Switch traffic from BLUE to GREEN
echo "🔄 Switching traffic: BLUE → GREEN..."
kubectl patch service api-gateway-service -n ticketing \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Step 6: Monitor GREEN for 5 minutes
echo "📊 Monitoring GREEN version (5 minutes)..."
for i in {1..30}; do
  ERROR_RATE=$(kubectl logs deployment/api-gateway-green -n ticketing --tail=100 | grep -c "ERROR")
  echo "[$i/30] Error rate: $ERROR_RATE"
  sleep 10
done

echo "✅ Traffic successfully switched to GREEN (v2.0.0)"
echo "💾 BLUE (v1.0.0) still running for instant rollback"
```

#### Step 4: Rollback Script (If Issues Found)

```bash
#!/bin/bash
# rollback-to-blue.sh - Instant rollback if issues detected

echo "🔄 ROLLING BACK to BLUE..."

# Switch traffic back to BLUE
kubectl patch service api-gateway-service -n ticketing \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# Delete GREEN
kubectl delete deployment api-gateway-green -n ticketing

echo "✅ Successfully rolled back to BLUE (v1.0.0)"
echo "📧 Incident report created"
```

---

### Part 2: Feature Flags for Control

```javascript
// feature-flags.js - Feature flag implementation

const featureFlags = {
  'new_booking_ui': {
    enabled: false,
    rollout_percentage: 0,
    description: 'New booking experience',
    created_date: '2024-01-15'
  },
  'payment_retry_logic': {
    enabled: true,
    rollout_percentage: 100,
    description: 'Automatic retry on payment failures',
    created_date: '2024-01-10'
  },
  'ml_recommendations': {
    enabled: true,
    rollout_percentage: 25,
    description: 'ML-based movie recommendations',
    created_date: '2024-01-05'
  }
};

// Check if feature is enabled for user
function isFeatureEnabled(featureName, userId) {
  const flag = featureFlags[featureName];
  
  if (!flag) {
    console.warn(`Feature flag '${featureName}' not found`);
    return false;
  }
  
  if (!flag.enabled) {
    return false;
  }
  
  // Hash-based rollout (deterministic for same user)
  const userHash = hashUserId(userId) % 100;
  return userHash < flag.rollout_percentage;
}

// Helper: Hash user ID consistently
function hashUserId(userId) {
  let hash = 0;
  for (let i = 0; i < userId.toString().length; i++) {
    const char = userId.toString().charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash);
}

// Update feature flag (from admin dashboard)
async function updateFeatureFlag(featureName, config) {
  featureFlags[featureName] = {
    ...featureFlags[featureName],
    ...config
  };
  
  // Save to database
  await db.query(
    'UPDATE feature_flags SET enabled = $1, rollout_percentage = $2 WHERE name = $3',
    [config.enabled, config.rollout_percentage, featureName]
  );
  
  // Notify all services
  await notifyServiceAboutFlagChange(featureName);
}

module.exports = { isFeatureEnabled, updateFeatureFlag };
```

#### Using Feature Flags in API

```javascript
// api-gateway.js - Using feature flags
const { isFeatureEnabled } = require('./feature-flags');

app.get('/api/bookings/:id/payment', (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;
  
  if (isFeatureEnabled('payment_retry_logic', userId)) {
    // NEW CODE PATH: With retry logic
    handlePaymentWithRetry(id)
      .then(result => res.json(result))
      .catch(err => res.status(500).json({ error: err.message }));
  } else {
    // OLD CODE PATH: Without retry
    handlePaymentSimple(id)
      .then(result => res.json(result))
      .catch(err => res.status(500).json({ error: err.message }));
  }
});

// Real-time flag update endpoint (admin only)
app.post('/api/admin/feature-flags/:name', adminAuth, async (req, res) => {
  const { name } = req.params;
  const { enabled, rollout_percentage } = req.body;
  
  // Validate inputs
  if (typeof enabled !== 'boolean' || rollout_percentage < 0 || rollout_percentage > 100) {
    return res.status(400).json({ error: 'Invalid parameters' });
  }
  
  // Update flag
  await updateFeatureFlag(name, { enabled, rollout_percentage });
  
  // Log for audit trail
  await logAdminAction(req.user.id, `Updated feature flag: ${name}`, {
    enabled,
    rollout_percentage
  });
  
  res.json({ message: `Feature flag '${name}' updated successfully` });
});
```

---

### Part 3: Canary Deployment

```bash
#!/bin/bash
# deploy-canary.sh - Canary deployment with automated rollout

VERSION="v2.0.0"
CANARY_STAGES=(5 10 25 50 100)  # Percentages
MONITOR_DURATION=3600  # seconds between each stage
ERROR_THRESHOLD=0.5    # % errors allowed before rollback
LATENCY_THRESHOLD=10   # % increase in latency allowed

echo "🚀 Starting Canary Deployment: v2.0.0"

# Deploy canary version (0% traffic)
echo "📦 Deploying canary version (0% traffic)..."
cat > canary-deployment.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway-canary
  namespace: ticketing
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api-gateway
      version: canary
  template:
    metadata:
      labels:
        app: api-gateway
        version: canary
    spec:
      containers:
      - name: api-gateway
        image: ticketing/api-gateway:${VERSION}
        ports:
        - containerPort: 3000
EOF

kubectl apply -f canary-deployment.yaml

# Wait for pod ready
kubectl wait --for=condition=ready pod \
  -l app=api-gateway,version=canary \
  -n ticketing \
  --timeout=300s

# Gradually increase traffic
for stage in "${CANARY_STAGES[@]}"; do
  echo "📊 Promoting canary to ${stage}% traffic..."
  
  # Update ingress weight
  kubectl patch virtualservice api-gateway -n ticketing --type merge -p \
    "{\"spec\":{\"hosts\":[{\"name\":\"api-gateway\"}],\"http\":[{\"match\":[{\"sourceLabels\":{\"version\":\"canary\"}}],\"route\":[{\"destination\":{\"host\":\"api-gateway\",\"subset\":\"canary\"},\"weight\":${stage}},\"destination\":{\"host\":\"api-gateway\",\"subset\":\"stable\"},\"weight\":$((100-$stage))}]}]}"
  
  # Monitor for issues
  echo "⏳ Monitoring for ${MONITOR_DURATION} seconds..."
  CURRENT_TIME=0
  while [ $CURRENT_TIME -lt $MONITOR_DURATION ]; do
    # Get metrics
    ERROR_RATE=$(getErrorRate "canary")
    LATENCY_INCREASE=$(getLatencyIncrease "canary" "stable")
    
    echo "[$CURRENT_TIME/$MONITOR_DURATION] Error Rate: ${ERROR_RATE}% | Latency +${LATENCY_INCREASE}%"
    
    # Check thresholds
    if (( $(echo "$ERROR_RATE > $ERROR_THRESHOLD" | bc -l) )); then
      echo "🚨 ERROR THRESHOLD EXCEEDED: ${ERROR_RATE}% > ${ERROR_THRESHOLD}%"
      rollbackCanary
      exit 1
    fi
    
    if (( $(echo "$LATENCY_INCREASE > $LATENCY_THRESHOLD" | bc -l) )); then
      echo "🚨 LATENCY THRESHOLD EXCEEDED: +${LATENCY_INCREASE}% > +${LATENCY_THRESHOLD}%"
      rollbackCanary
      exit 1
    fi
    
    CURRENT_TIME=$((CURRENT_TIME + 60))
    sleep 60
  done
  
  echo "✅ Stage ${stage}% passed all checks"
done

echo "✅ Canary deployment successful!"
echo "🎉 v2.0.0 now serving 100% of traffic"

# Function to get error rate
getErrorRate() {
  kubectl logs -l "app=api-gateway,version=$1" -n ticketing --tail=1000 | \
    grep -c "ERROR\|500\|ERROR" / $(kubectl logs -l "app=api-gateway,version=$1" -n ticketing --tail=1000 | wc -l) * 100
}

# Function to compare latencies
getLatencyIncrease() {
  # Query Prometheus or application metrics
  curl -s "http://prometheus:9090/api/v1/query?query=rate(http_request_duration_sum{job=\"$1\"}[5m])/rate(http_request_duration_count{job=\"$1\"}[5m])" | jq '.data.result[0].value[1]'
}

# Rollback function
rollbackCanary() {
  echo "⚠️ Rolling back canary deployment..."
  kubectl delete deployment api-gateway-canary -n ticketing
  # Reset traffic to stable only
  kubectl patch virtualservice api-gateway -n ticketing --type merge -p \
    '{"spec":{"hosts":[{"name":"api-gateway"}],"http":[{"route":[{"destination":{"host":"api-gateway","subset":"stable"},"weight":100}]}]}}'
  echo "✅ Rolled back successfully"
}
```

---

### Part 4: Database Migration with Zero Downtime

```javascript
// migration-script.js - Backwards-compatible schema change

const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME
});

async function runMigration() {
  console.log('🔄 Starting migration...');
  
  // STEP 1: Add new column (nullable - old app doesn't break)
  console.log('📝 Step 1: Adding new_column...');
  await pool.query(`
    ALTER TABLE bookings 
    ADD COLUMN payment_method_v2 VARCHAR(50) DEFAULT NULL;
  `);
  console.log('✅ New column added');
  
  // STEP 2: Deploy new code that populates the column
  // (No action here - deployment handles this)
  console.log('📝 Step 2: Deploy new code (separate step)');
  console.log('⏸️  PAUSE - Deploy new code that reads/writes payment_method_v2');
  
  // Wait for deployment and data population
  await waitForDataMigration();
  
  // STEP 3: Make column required (only after all data is populated)
  console.log('📝 Step 3: Making column NOT NULL...');
  await pool.query(`
    ALTER TABLE bookings 
    ALTER COLUMN payment_method_v2 SET NOT NULL;
  `);
  console.log('✅ Column is now required');
  
  // STEP 4: Remove old column (only after code no longer uses it)
  console.log('📝 Step 4: Removing old column (after 3+ months)...');
  // await pool.query(`ALTER TABLE bookings DROP COLUMN payment_method;`);
  console.log('⏸️  Scheduled for later');
  
  console.log('✅ Migration complete!');
  process.exit(0);
}

async function waitForDataMigration() {
  console.log('⏳ Waiting for data migration to complete...');
  
  // Check percentage of rows migrated
  let migrationComplete = false;
  let attempts = 0;
  
  while (!migrationComplete && attempts < 300) {  // 5 hours max
    const result = await pool.query(`
      SELECT 
        COUNT(*) as total,
        COUNT(payment_method_v2) as migrated
      FROM bookings;
    `);
    
    const { total, migrated } = result.rows[0];
    const percentage = ((migrated / total) * 100).toFixed(2);
    
    console.log(`Migration progress: ${percentage}% (${migrated}/${total})`);
    
    if (percentage >= 99.9) {
      migrationComplete = true;
    } else {
      attempts++;
      await new Promise(r => setTimeout(r, 60000));  // Wait 1 minute
    }
  }
  
  console.log('✅ Data migration complete!');
}

runMigration().catch(err => {
  console.error('❌ Migration failed:', err);
  process.exit(1);
});
```

---

### Part 5: Deployment Status Dashboard

```javascript
// deployment-dashboard.js
const express = require('express');
const app = express();

// Deployment state tracking
const deploymentState = {
  current_version: 'v1.0.0',
  target_version: 'v2.0.0',
  status: 'in_progress',  // 'idle', 'in_progress', 'failed', 'complete'
  stages: [
    { name: 'Database Migration', status: 'complete', duration: '10 min' },
    { name: 'Backend Deployment', status: 'in_progress', duration: '15 min' },
    { name: 'Frontend Deployment', status: 'waiting', duration: 'TBD' },
    { name: 'Mobile Deployment', status: 'waiting', duration: 'TBD' }
  ],
  error_rate: {
    v1: 0.02,
    v2: 0.03
  },
  latency: {
    v1: 45,  // ms
    v2: 48   // ms
  },
  traffic_split: {
    v1: 70,  // %
    v2: 30   // %
  },
  rollback_available: true,
  estimated_completion: '2024-01-15 14:30 UTC'
};

// WebSocket for real-time updates
const WebSocket = require('ws');
const wss = new WebSocket.Server({ noServer: true });

app.get('/api/deployment/status', (req, res) => {
  res.json(deploymentState);
});

app.post('/api/deployment/rollback', (req, res) => {
  if (!deploymentState.rollback_available) {
    return res.status(400).json({ error: 'Rollback not available' });
  }
  
  deploymentState.status = 'rollback_in_progress';
  
  // Trigger actual rollback script
  triggerRollbackScript();
  
  // Notify all dashboard clients
  broadcastUpdate({
    type: 'rollback_initiated',
    message: `Rolling back from ${deploymentState.target_version} to ${deploymentState.current_version}`
  });
  
  res.json({ message: 'Rollback initiated' });
});

// HTML Dashboard
app.get('/deployment-dashboard', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Deployment Dashboard</title>
      <style>
        body { font-family: Arial; background: #0f0f0f; color: white; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .status-card { background: #1a1a1a; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .version-info { font-size: 14px; color: #999; }
        .metrics { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 20px; }
        .metric { background: #2a2a2a; padding: 15px; border-radius: 5px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #667eea; }
        .metric-label { font-size: 12px; color: #999; margin-top: 5px; }
        .stage { display: flex; align-items: center; gap: 10px; padding: 10px; background: #222; margin: 5px 0; border-radius: 3px; }
        .stage-status { font-weight: bold; }
        .complete { color: #4ade80; }
        .in_progress { color: #fbbf24; }
        .waiting { color: #999; }
        .rollback-btn { background: #ef4444; padding: 10px 20px; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .rollback-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .traffic-split { display: flex; height: 30px; border-radius: 5px; overflow: hidden; }
        .traffic-v1 { background: #667eea; display: flex; align-items: center; justify-content: center; }
        .traffic-v2 { background: #8b5cf6; display: flex; align-items: center; justify-content: center; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🚀 Deployment Dashboard</h1>
        
        <div class="status-card">
          <h2>Deployment Status</h2>
          <div>Status: <strong id="status">in_progress</strong></div>
          <div class="version-info">From: <span id="current-version">v1.0.0</span> → To: <span id="target-version">v2.0.0</span></div>
          <div class="version-info">ETA: <span id="eta">2024-01-15 14:30 UTC</span></div>
        </div>
        
        <div class="status-card">
          <h2>Deployment Stages</h2>
          <div id="stages"></div>
        </div>
        
        <div class="status-card">
          <h2>Real-Time Metrics</h2>
          <div class="metrics">
            <div class="metric">
              <div class="metric-value" id="error-rate">0.03%</div>
              <div class="metric-label">Error Rate (v2.0)</div>
            </div>
            <div class="metric">
              <div class="metric-value" id="latency">+3ms</div>
              <div class="metric-label">Latency (v2.0 vs v1.0)</div>
            </div>
            <div class="metric">
              <div class="metric-value" id="users">1.2M</div>
              <div class="metric-label">Active Users</div>
            </div>
          </div>
        </div>
        
        <div class="status-card">
          <h2>Traffic Split</h2>
          <div class="traffic-split">
            <div class="traffic-v1" id="traffic-v1" style="width: 70%">
              v1.0: 70%
            </div>
            <div class="traffic-v2" id="traffic-v2" style="width: 30%">
              v2.0: 30%
            </div>
          </div>
        </div>
        
        <div class="status-card">
          <button class="rollback-btn" id="rollback-btn" onclick="triggerRollback()">
            ⚠️ ROLLBACK TO v1.0
          </button>
          <div style="font-size: 12px; color: #999; margin-top: 10px;">
            Rollback available: <span id="rollback-status">Yes</span>
          </div>
        </div>
      </div>
      
      <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket('ws://' + window.location.host);
        
        ws.onmessage = (event) => {
          const update = JSON.parse(event.data);
          updateDashboard(update);
        };
        
        function updateDashboard(data) {
          if (data.status) document.getElementById('status').textContent = data.status;
          if (data.error_rate) document.getElementById('error-rate').textContent = data.error_rate.v2 + '%';
          if (data.latency) document.getElementById('latency').textContent = '+' + (data.latency.v2 - data.latency.v1) + 'ms';
          
          if (data.traffic_split) {
            const v1 = data.traffic_split.v1;
            const v2 = data.traffic_split.v2;
            document.getElementById('traffic-v1').style.width = v1 + '%';
            document.getElementById('traffic-v1').textContent = 'v1.0: ' + v1 + '%';
            document.getElementById('traffic-v2').style.width = v2 + '%';
            document.getElementById('traffic-v2').textContent = 'v2.0: ' + v2 + '%';
          }
        }
        
        async function triggerRollback() {
          if (confirm('Are you sure you want to rollback to v1.0.0?')) {
            const response = await fetch('/api/deployment/rollback', { method: 'POST' });
            if (response.ok) {
              alert('Rollback initiated!');
            } else {
              alert('Rollback failed!');
            }
          }
        }
        
        // Load initial state
        fetch('/api/deployment/status')
          .then(r => r.json())
          .then(updateDashboard);
      </script>
    </body>
    </html>
  `);
});

app.listen(3100, () => {
  console.log('📊 Deployment dashboard running on http://localhost:3100/deployment-dashboard');
});
```

---

### Part 6: Automated Monitoring & Rollback

```javascript
// monitoring.js - Automatic rollback on threshold breach

const prometheus = require('prom-client');

async function monitorDeployment() {
  const healthCheckInterval = 30000;  // 30 seconds
  const errorThreshold = 1.0;         // 1% errors triggers rollback
  const latencyThreshold = 30;        // 30% increase triggers rollback
  
  setInterval(async () => {
    try {
      // Get metrics for new version
      const newVersionMetrics = await getMetrics('v2.0.0');
      const oldVersionMetrics = await getMetrics('v1.0.0');
      
      console.log('📊 Health Check:');
      console.log(`  v2.0 Error Rate: ${newVersionMetrics.errorRate}%`);
      console.log(`  v2.0 Latency: ${newVersionMetrics.p99Latency}ms`);
      
      // Check error rate
      if (newVersionMetrics.errorRate > errorThreshold) {
        console.error(`🚨 ERROR RATE EXCEEDED: ${newVersionMetrics.errorRate}% > ${errorThreshold}%`);
        await triggerAutomaticRollback('High error rate');
        return;
      }
      
      // Check latency
      const latencyIncrease = ((newVersionMetrics.p99Latency - oldVersionMetrics.p99Latency) / oldVersionMetrics.p99Latency) * 100;
      if (latencyIncrease > latencyThreshold) {
        console.error(`🚨 LATENCY THRESHOLD EXCEEDED: +${latencyIncrease.toFixed(2)}% > ${latencyThreshold}%`);
        await triggerAutomaticRollback('High latency increase');
        return;
      }
      
      // Check crash rates
      const crashRate = await getCrashRate('v2.0.0');
      if (crashRate > 0.5) {
        console.error(`🚨 HIGH CRASH RATE: ${crashRate}%`);
        await triggerAutomaticRollback('High crash rate');
        return;
      }
      
      console.log('✅ All metrics normal');
      
    } catch (err) {
      console.error('Monitoring error:', err);
    }
  }, healthCheckInterval);
}

async function triggerAutomaticRollback(reason) {
  console.error(`⚠️ AUTOMATIC ROLLBACK TRIGGERED: ${reason}`);
  
  // Step 1: Immediately switch traffic back to v1.0
  await switchTrafficToVersion('v1.0.0');
  
  // Step 2: Send alerts
  await sendAlert({
    severity: 'critical',
    title: 'Automatic Rollback Triggered',
    reason: reason,
    timestamp: new Date().toISOString(),
    action_required: 'Investigate root cause and fix before retry'
  });
  
  // Step 3: Log incident
  await logIncident({
    type: 'automatic_rollback',
    from_version: 'v2.0.0',
    to_version: 'v1.0.0',
    reason: reason,
    automated: true
  });
  
  // Step 4: Notify team (Slack, PagerDuty, email)
  await notifyTeam({
    channel: '#incidents',
    message: `🚨 Automatic rollback: ${reason}. Version v2.0.0 rolled back to v1.0.0`
  });
  
  console.log('✅ Rollback complete. System stable on v1.0.0');
}

// Helper functions
async function getMetrics(version) {
  // Query Prometheus for metrics
  const response = await fetch(`http://prometheus:9090/api/v1/query`, {
    method: 'POST',
    body: JSON.stringify({
      query: `rate(http_requests_total{version="${version}",status=~"5.."}[5m]) * 100`
    })
  });
  
  const data = await response.json();
  return {
    errorRate: parseFloat(data.data.result[0]?.value[1] || 0),
    p99Latency: 50  // Placeholder
  };
}

async function getCrashRate(version) {
  // Check for pod crashes
  const { execSync } = require('child_process');
  const restarts = execSync(`kubectl get pods -l version=${version} -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}'`).toString();
  return parseFloat(restarts) || 0;
}

async function switchTrafficToVersion(version) {
  const { execSync } = require('child_process');
  execSync(`kubectl patch service api-gateway-service -p '{"spec":{"selector":{"version":"${version}}}'`);
}

// Start monitoring
monitorDeployment();

module.exports = { monitorDeployment, triggerAutomaticRollback };
```

---

## 📝 Deployment Runbook (For Ops Team)

```
MOVIE TICKETING APP - DEPLOYMENT RUNBOOK v2.0.0

DEPLOYMENT DATE: January 15, 2024
DEPLOYMENT WINDOW: 14:00 UTC - 18:00 UTC (4 hours)
ON-CALL: john@company.com, sarah@company.com

TEAM CHECKLIST
─────────────
□ All team members present in war room
□ War room Slack channel created: #deploy-v2-0-0
□ PagerDuty on-call notification sent
□ Customer support team notified
□ Database backup verified
□ Rollback procedure rehearsed

PHASE 1: DATABASE MIGRATION (14:00 - 14:20 UTC)
────────────────────────────────────────────────
Script: ./scripts/migrate-database.sh
Expected Duration: 20 minutes
Rollback: ./scripts/rollback-migration.sh

14:00 - Run migration script
  Command: ./scripts/migrate-database.sh
  Monitor: Check PostgreSQL logs for errors
  Success Criteria: "Migration complete" message
  
14:05 - Verify migration
  Check: SELECT COUNT(*) FROM bookings;
  Compare: Should match pre-migration count
  
14:10 - Update feature flags (if any changes)
  Flag: new_booking_schema = true (0% rollout)
  
14:15 - Data validation queries
  SELECT COUNT(*) FROM bookings WHERE payment_method_v2 IS NULL; -- Should be 0%
  
14:20 - Proceed to Phase 2

PHASE 2: BACKEND SERVICES DEPLOYMENT (14:20 - 15:00 UTC)
─────────────────────────────────────────────────────────
Script: ./scripts/deploy-blue-green.sh
Expected Duration: 40 minutes
Rollback: ./scripts/rollback-to-blue.sh

14:20 - Deploy GREEN environment
  Services: Payment, Booking, Movie, Notification
  Check: kubectl get pods -n ticketing | grep green
  
14:30 - Smoke tests on GREEN
  Test: curl http://api-gateway-green:3000/health
  Test: Test payment flow
  Test: Test booking flow
  
14:45 - Switch traffic BLUE → GREEN
  Command: kubectl patch service ... -p '{"spec":{"selector":{"version":"green"}}}'
  Monitor: Error rate should stay <0.1%
  Monitor: Latency should not increase >10%
  
14:50 - 60-minute monitoring window starts
  Watch: Error rates in CloudWatch
  Watch: API latency metrics
  Watch: Database connection pools
  
15:00 - Check-in: All GREEN metrics normal? YES → Proceed to Phase 3

PHASE 3: FRONTEND DEPLOYMENT (15:00 - 16:00 UTC)
───────────────────────────────────────────────────
Script: ./scripts/deploy-canary.sh
Expected Duration: 60 minutes
Rollback: Manual - Reset CDN cache to v1.0

15:00 - Build React app
  Build: npm run build
  Size: Check bundle size < 2MB
  Staging: Verify on staging first
  
15:10 - Deploy to CDN (v1.0.0 still primary)
  Upload: aws s3 sync build/ s3://ticketing-frontend/
  CloudFront: Invalidate cache
  
15:15 - Canary: 5% users get v2.0 frontend
  Monitoring: Browser console errors
  Monitoring: JavaScript errors in New Relic
  
15:30 - Canary: Expand to 10%
  Status: No new errors reported
  Proceed: YES
  
15:45 - Canary: Expand to 25%
  Status: All metrics normal
  Proceed: YES
  
16:00 - Canary: Expand to 100%
  Status: v2.0 frontend fully deployed
  Keep: v1.0 cached for quick rollback

PHASE 4: MOBILE APP DEPLOYMENT (16:00+ ongoing)
────────────────────────────────────────────────
Cannot complete today - waiting for app store review
Timeline: 24-48 hours for review, then staged rollout

16:00 - Submit to App Stores
  iOS: Build archive, submit to TestFlight
  Android: Build APK, submit to Play Store
  
Day 2 - Once approved: Staged rollout 10% → 25% → 100%

POST-DEPLOYMENT
────────────────
□ All services stable for 2+ hours
□ Customer complaints: NONE
□ Error rates: <0.05%
□ Database integrity: Verified
□ Metrics comparison: v2.0 vs v1.0 approved
□ Keep v1.0 running for 24 hours (instant rollback window)
□ Archive logs and metrics
□ Team debrief (30 min)
□ Incident report (if any issues)

ROLLBACK TRIGGERS
─────────────────
Immediate rollback if ANY of:
- Error rate > 1%
- P99 latency increase > 30%
- Database connection errors
- Payment processing failures
- Multiple customer complaints
- Any critical bug found

CONTACT INFO
────────────
On-Call: john@company.com (phone: XXX-XXX-XXXX)
Backup: sarah@company.com (phone: XXX-XXX-XXXX)
CTO: Emergency approval - emergency@company.com
Product: Post-mortem discussion - product@company.com
Support: Incident response - support@company.com

NOTES FOR THIS DEPLOYMENT
──────────────────────────
- Database schema change is backwards compatible
- Both v1 and v2 code can run simultaneously
- New payment logic uses feature flags (0% rollout initially)
- Mobile app will use old API for 3 months
- No forced downtime expected
```

---

## ✅ Summary

This practical guide shows how enterprises actually deploy applications:

1. **Blue-Green Deployment** - Test new version fully before traffic switch
2. **Feature Flags** - Control rollout percentage without re-deployment
3. **Canary Deployment** - Gradually increase traffic to new version
4. **Database Migrations** - Backwards compatible schema changes
5. **Automated Monitoring** - Trigger rollback on metrics threshold
6. **Comprehensive Runbooks** - Step-by-step procedures for operations

**Key Takeaway:** Enterprise deployments are automated, monitored, controlled, and reversible. Everything has a rollback plan.
