// LICDIA UNLu — Web Vitals Tracker
// Sends Core Web Vitals (LCP, CLS, INP, FCP, TTFB) to n8n webhook.
// - 10% sampling
// - Respects Do Not Track
// - Uses navigator.sendBeacon with fetch keepalive fallback

(function () {
  'use strict';

  var ENDPOINT = 'https://n8n.impulsate.lat/webhook/licdia-vitals';
  var SAMPLE_RATE = 0.1;

  // Respect Do Not Track
  if (navigator.doNotTrack === '1') {
    return;
  }

  // Sampling: only track 10% of sessions
  if (Math.random() > SAMPLE_RATE) {
    return;
  }

  function sendMetric(metric) {
    var payload = {
      metric: metric.name,
      value: metric.value,
      rating: metric.rating,
      delta: metric.delta,
      id: metric.id,
      page: window.location.pathname,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      timestamp: Date.now()
    };

    var body = JSON.stringify(payload);

    try {
      if (navigator.sendBeacon) {
        var blob = new Blob([body], { type: 'application/json' });
        var ok = navigator.sendBeacon(ENDPOINT, blob);
        if (ok) return;
      }
    } catch (e) {
      // fall through to fetch
    }

    // Fallback: fetch with keepalive
    try {
      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body,
        keepalive: true,
        mode: 'no-cors'
      });
    } catch (e) {
      // swallow — tracking is best-effort
    }
  }

  // Load web-vitals library from CDN as ES module
  import('https://unpkg.com/web-vitals@3?module')
    .then(function (webVitals) {
      if (webVitals.onLCP) webVitals.onLCP(sendMetric);
      if (webVitals.onCLS) webVitals.onCLS(sendMetric);
      if (webVitals.onINP) webVitals.onINP(sendMetric);
      if (webVitals.onFCP) webVitals.onFCP(sendMetric);
      if (webVitals.onTTFB) webVitals.onTTFB(sendMetric);
    })
    .catch(function () {
      // Library load failed — silent
    });
})();
