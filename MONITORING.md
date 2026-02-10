# New Relic Performance Monitoring Setup

This guide walks you through setting up real-time performance monitoring for both the backend API and frontend React application using New Relic.

## Prerequisites

- New Relic account (https://newrelic.com - free tier available)
- Backend running with Python 3.14+
- Frontend built with React + TypeScript

---

## Backend Setup (FastAPI with New Relic APM)

### Step 1: Get Your License Key

1. Visit: https://one.newrelic.com/api-keys
2. Click **Create Key** → **Ingest - License**
3. Copy the 40-character license key (starts with the key you created)

### Step 2: Configure Backend

**File:** `backend/newrelic.ini`

```ini
[newrelic]
license_key = YOUR_40_CHAR_LICENSE_KEY
app_name = GoComet-Backend
monitor_mode = true
log_level = info
distributed_tracing.enabled = true
```


### Step 3: Start Backend with Monitoring

```bash
cd backend
NEW_RELIC_CONFIG_FILE=newrelic.ini python -m uvicorn app.main:app --reload
```

### Step 4: Generate Test Data

```bash
python generate_data.py
```

This generates 60 requests to create monitoring data.

### Step 5: View APM Dashboard

1. Go to: https://one.newrelic.com/apm
2. Look for **"GoComet-Backend"** application
3. View real-time metrics:
   - Request throughput
   - Response times (average, max, 95th percentile)
   - Error rates
   - Database performance

---

## Frontend Setup (React Browser Monitoring)

### Step 1: Get Browser License Key

1. Visit: https://one.newrelic.com/browser
2. If "GoComet-Frontend" doesn't exist:
   - Click **Install Browser** → React → Name: `GoComet-Frontend`
3. Copy the provided JavaScript snippet

### Step 2: Add to Frontend

**File:** `frontend/index.html`

Add this in the `<head>` section (replace with YOUR values):

```html
<!-- New Relic Browser Agent -->
<script>
  ;(function(){window.NREUM||(NREUM={});NREUM.info={
    "beacon":"bam.nr-data.net",
    "errorBeacon":"bam.nr-data.net",
    "licenseKey":"YOUR_BROWSER_LICENSE_KEY",
    "applicationID":"YOUR_APPLICATION_ID",
    "applicationName":"GoComet-Frontend",
    "spa":true
  }}());
</script>
<script src="https://js-agent.newrelic.com/nr-spa-XXXXX.min.js" defer></script>
```

### Step 3: Build & Deploy Frontend

```bash
cd frontend
npm run build
npm preview  # or deploy to production
```

### Step 4: View Browser Monitoring

1. Go to: https://one.newrelic.com/browser
2. Click **"GoComet-Frontend"**
3. View metrics:
   - Page load time
   - User interactions
   - JavaScript errors
   - Real user monitoring (RUM)

---

## Creating Custom Dashboards

### NRQL Query Examples

**Average Response Time Over Time:**
```nrql
SELECT average(duration) as 'Avg Response (ms)', max(duration) as 'Max Response (ms)', percentile(duration, 95) as '95th Percentile'
FROM Transaction
WHERE appName = 'GoComet-Backend'
TIMESERIES
```

**Error Rate:**
```nrql
SELECT percentage(count(*), WHERE error IS true) as 'Error Rate %'
FROM Transaction
WHERE appName = 'GoComet-Backend'
TIMESERIES
```

**Request Throughput:**
```nrql
SELECT rate(count(*), 1 minute) as 'Requests/sec'
FROM Transaction
WHERE appName = 'GoComet-Backend'
TIMESERIES
```

### Creating Dashboard

1. Go to: https://one.newrelic.com/dashboards
2. Click **Create a dashboard**
3. For each query:
   - Click **Add a chart**
   - Select **NRQL**
   - Paste query
   - Customize title and colors
   - Click **Save**


---

## Performance Benchmarks

### Expected Metrics

| Metric | Expected Value |
|--------|---|
| Average Response Time | 5-20ms |
| 95th Percentile | 30-50ms |
| Max Response Time | 100-200ms |
| Error Rate | <0.1% |
| Throughput | 100+ req/sec |
| Database Query Time | <5ms |

---

## Troubleshooting

### Backend Not Showing in APM

1. Check license key format (should be 40 characters)
2. Check `monitor_mode = true` in `newrelic.ini`
3. Verify environment variable: `echo $NEW_RELIC_CONFIG_FILE`
4. Check New Relic agent logs: Enable `log_level = debug`

### Frontend Not Showing in Browser

1. Verify applicati<br>onID and license key in HTML
2. Check `spa: true` for React apps
3. Look for JavaScript errors in browser console
4. Verify script loads: Check Network tab in DevTools

### Data Not Appearing

1. Wait 2-5 minutes for data ingestion
2. Generate more traffic: Run `generate_data.py` again
3. Check network connectivity (can app reach New Relic servers?)
4. Verify license key is valid: https://one.newrelic.com/api-keys

---

## Resources

- **New Relic Documentation:** https://docs.newrelic.com/
- **Python Agent Docs:** https://docs.newrelic.com/docs/agents/python-agent/
- **Browser Agent Docs:** https://docs.newrelic.com/docs/agents/browser-agent/
- **NRQL Docs:** https://docs.newrelic.com/docs/insights/nrql-new-relic-query-language/using-nrql/introduction-nrql/

---

## Support

For issues or questions:
1. Check New Relic docs
2. Review logs: `tail -f logs/newrelic_*.log`
3. Test connectivity to New Relic servers
4. Verify license key validity
