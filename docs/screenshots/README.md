# 📸 Performance Dashboard Screenshots

This directory should contain screenshots of the New Relic performance dashboards.

## Required Screenshots

### 1. Backend APM Dashboard (`backend-apm-dashboard.png`)
**What to capture:**
- URL: https://one.newrelic.com/apm
- Click on "GoComet-Backend" application
- Capture the main dashboard showing:
  - Request throughput
  - Average response time
  - Error rate
  - Top endpoints

**How to capture:**
- Use Cmd+Shift+4 (Mac) or Windows+Shift+S (Windows)
- Or use browser DevTools → Capture Full Screenshot
- Or Print → Save as PDF

### 2. Browser Monitoring Dashboard (`browser-dashboard.png`)
**What to capture:**
- URL: https://one.newrelic.com/browser
- Click on "GoComet-Frontend" application
- Capture the dashboard showing:
  - Page views
  - Browser types
  - JavaScript errors
  - Real user monitoring data

---

## 🎯 Steps to Capture Screenshots

1. **Backend Dashboard:**
   ```
   1. Go to https://one.newrelic.com/apm
   2. Wait for "GoComet-Backend" to appear (5-10 minutes after starting)
   3. Click on it
   4. Take screenshot of the dashboard
   5. Save as: backend-apm-dashboard.png
   6. Place in: docs/screenshots/
   ```

2. **Frontend Dashboard:**
   ```
   1. Go to https://one.newrelic.com/browser
   2. Click on "GoComet-Frontend"
   3. Let some traffic flow through the app
   4. Take screenshot of the browser dashboard
   5. Save as: browser-dashboard.png
   6. Place in: docs/screenshots/
   ```

---

## ⚠️ Important Notes

- **DO NOT include any sensitive data** in screenshots
- **DO NOT show license keys** or API credentials
- Make sure **URL bar is cropped/hidden** if it contains sensitive info
- Screenshots should show **general layout and metrics only**

---

## 📖 How to Use

Once you have the screenshots:

1. Place them in this directory
2. They will automatically appear in the main README.md
3. Push to git (screenshots are not sensitive - they're just images of public dashboards)

---

## Placeholder Images (Until Screenshots Are Added)

If you want to use placeholder images temporarily:

1. Save any image file as `backend-apm-dashboard.png`
2. Save any image file as `browser-dashboard.png`
3. The README will display them with the captions

---

**Last Update:** 2026-02-10
