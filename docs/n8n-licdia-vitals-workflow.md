# n8n Workflow — LICDIA Web Vitals

Workflow spec to ingest Core Web Vitals from the LICDIA UNLu sites
(`webLaboratorio/index.html`, `dev-ia/`, `blockchain-dev/`, `charla/*`).

## Endpoint

- **URL**: `https://n8n.impulsate.lat/webhook/licdia-vitals`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Response**: `204 No Content` (immediate, no body) — keeps the browser
  beacon fast and avoids blocking page unload.

Client uses `navigator.sendBeacon` (fallback: `fetch` with `keepalive: true`,
`mode: 'no-cors'`). The webhook must accept CORS preflight or return
no CORS headers (no-cors fetch is fine; sendBeacon doesn't preflight).

## Incoming Payload

```json
{
  "metric": "LCP",
  "value": 2345.6,
  "rating": "good",
  "delta": 2345.6,
  "id": "v3-1700000000000-1234567890",
  "page": "/dev-ia/",
  "referrer": "https://google.com/",
  "userAgent": "Mozilla/5.0 ...",
  "timestamp": 1700000000000
}
```

Metrics emitted: `LCP`, `CLS`, `INP`, `FCP`, `TTFB`.
Rating values: `good` | `needs-improvement` | `poor`.

## Workflow Nodes

1. **Webhook** (trigger)
   - Path: `licdia-vitals`
   - HTTP Method: `POST`
   - Respond: `Immediately`
   - Response Code: `204`
   - Response Data: (empty)

2. **Google Sheets — Append Row**
   - Operation: `Append`
   - Document: `licdia-web-vitals` (suggested name, located in shared Drive)
   - Sheet: `vitals` (tab 1)
   - Columns (in order):
     | Column     | Source                                          |
     |------------|-------------------------------------------------|
     | timestamp  | `={{ new Date($json.body.timestamp).toISOString() }}` |
     | page       | `={{ $json.body.page }}`                        |
     | metric     | `={{ $json.body.metric }}`                      |
     | value      | `={{ $json.body.value }}`                       |
     | rating     | `={{ $json.body.rating }}`                      |
     | userAgent  | `={{ $json.body.userAgent }}`                   |
     | referrer   | `={{ $json.body.referrer }}`                    |

   Header row in the sheet:
   `timestamp | page | metric | value | rating | userAgent | referrer`

## Operational Notes

- **Sampling**: client samples 10% of sessions, so volume = ~10% of pageviews × 5 metrics.
- **DNT**: clients with `navigator.doNotTrack === '1'` are excluded at source.
- **Google OAuth**: if writes stop, re-authorize the Google Sheets credential
  in n8n (the OAuth token expires periodically — common cause of silent failures).
- **Recommended dashboard**: pivot in Google Sheets / Looker Studio by `page` × `metric`
  with median + p75 over a 7-day rolling window. Track % `good` per metric per page.
