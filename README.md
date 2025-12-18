# FBpsLab (Forbidden Bypass Laboratory)

FBpsLab is a small, containerized lab environment that demonstrates how **401 Unauthorized**
and **403 Forbidden** controls can be accidentally bypassed when a **reverse proxy (Nginx)**
and a **backend (Flask)** interpret or match requests differently.

It is intended for **academic, training, and demonstrative** purposes in controlled environments,
and can be tested with **FBps** or similar tools that generate request variations (path, headers,
methods, normalization quirks).

## Architecture

FBpsLab runs two main services via Docker Compose:

- **Nginx**: reverse proxy and access-control enforcement layer (intentionally misconfigured in places)
- **Flask**: backend application exposing endpoints used to verify whether a request reached the app

A simplified request flow:

```
+--------------------+      HTTP        +------------------------+      HTTP       +-------------------+
|       Client       | -------------->  |   Nginx Reverse Proxy  | --------------> | Flask Backend App |
| (FBps, curl, etc.) |  Host: fbps.com  | (locations, auth, ACL) |  upstream :8000 |  (routes, resp.)  |
|                    |                  |                        |                 |                   |
+--------------------+                  +------------------------+                 +-------------------+
```

## What you can test with this lab

FBpsLab includes multiple intentionally vulnerable patterns that commonly cause 401/403 bypasses,
such as:

- Location matching edge cases (prefix vs exact-match, slash differences)
- Regex vs prefix precedence issues (routing to an unexpected handler)
- Header-based controls that can be unsafe if based on client-controlled values (e.g., forwarded headers)
- Normalization discrepancies (different trimming / decoding between proxy and backend)
- Legacy / versioned API paths (newer paths protected while older equivalents remain reachable)
- Case-sensitivity mismatches between proxy matching and backend routing
- Allowlist logic based on patterns (e.g., User-Agent gating)

The backend endpoints return clear responses so you can confirm whether the request was stopped at
the proxy or successfully reached the application.

## Usage

### Requirements
- Docker + Docker Compose
- curl / browser (optionally FBps)

### Start the lab
From the project root:

```bash
docker-compose up --build
```

This starts:

- Nginx on port 80 (published as 80:80 on the host)
- Flask app on port 8000 (internal service port, reached via Nginx upstream)

### Hostname setup (recommended)

Nginx is configured to serve requests for the hostname "fbps.com".
For the most realistic reverse-proxy behavior, map that name to localhost:

On Linux/macOS, edit:
  /etc/hosts

Add this line:
  127.0.0.1 fbps.com

On Windows, edit (as Administrator):
  C:\Windows\System32\drivers\etc\hosts

Add the same line:
  127.0.0.1 fbps.com

Then you can test via:
  http://fbps.com/

### Alternative (no hosts file change)

If you cannot edit hosts, you can still target localhost and force the Host header, e.g.:

curl -i http://127.0.0.1/ -H "Host: fbps.com"

This is also useful when driving tests via scripts/tools that can set custom headers.

### Typical workflow

1) Start the lab (docker compose up --build)
2) Confirm the homepage loads (http://fbps.com/ or curl with Host header)
3) Probe baseline endpoints that should return 401/403
4) Use FBps (or similar) to generate request variants and observe response changes that indicate a bypass
5) Iterate: adjust proxy rules, re-test, and document findings

---

## Disclaimer

FBpsLab is a deliberately insecure laboratory for educational use.
Do not deploy it on exposed or production systems.
