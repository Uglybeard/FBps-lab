# FBpsLab (Forbidden Bypass Laboratory)

![FBps banner](/img/fbpslab.png)

[![Docker](https://img.shields.io/badge/Docker-required-blue)](https://www.docker.com/)
[![Educational](https://img.shields.io/badge/Purpose-Educational-orange)]()

FBpsLab is a small, containerized lab environment that demonstrates how **401 Unauthorized**
and **403 Forbidden** controls can be bypassed when a **reverse proxy (Nginx)**
and a **backend (Flask)** interpret or match requests differently.

It is intended for **academic, training, and demonstrative** purposes in controlled environments,
and can be tested with **[FBps](https://github.com/Uglybeard/FBps)** or similar tools that generate request variations (path, headers,
methods, normalization quirks).

## Architecture

FBpsLab runs two main services via Docker Compose:

- **Nginx**: reverse proxy and access-control enforcement layer (intentionally misconfigured in places)
- **Flask**: backend application exposing endpoints used to verify whether a request reached the app

A simplified request flow:

```
+--------------------+      HTTP        +------------------------+      HTTP       +------------------+
|       Client       | -------------->  |   Nginx Reverse Proxy  | --------------> |  Flask Backend   |
| (FBps, curl, etc.) |  Host: fbps.com  | (locations, auth, ACL) |  upstream :8000 |   (app logic)    |
|                    |                  |                        |                 |                  |
+--------------------+                  +------------------------+                 +------------------+
```

## Vulnerable Patterns Included

FBpsLab includes intentionally misconfigured scenarios that mirror real-world 401/403 bypass vulnerabilities:

- **Location matching edge cases**: prefix vs exact-match confusion, trailing slash handling
- **Routing precedence issues**: regex locations overriding prefix-based deny rules
- **Unsafe header-based controls**: access decisions based on client-controlled headers
- **Normalization discrepancies**: different path decoding/trimming between proxy and backend
- **API versioning gaps**: newer endpoints protected while legacy versions remain accessible
- **Case-sensitivity mismatches**: proxy matches case-sensitively but backend routes case-insensitively (or vice versa)

Backend endpoints return clear responses indicating whether the request was stopped at the proxy or successfully reached the application.

## Usage

### Requirements
- Docker and Docker Compose installed
- Basic HTTP client (curl, browser, or [FBps](https://github.com/Uglybeard/FBps))

### Start the lab
From the project root:

```bash
docker-compose up --build
```

This starts:

- Nginx on port 80 (published as 80:80 on the host)
- Flask app on port 8000 (internal service port, reached via Nginx upstream)

## Expected Vulnerabilities

This lab demonstrates common 401/403 bypass classes. Examples include:

1. **Path matching quirks**: `/admin/` blocked but `/admin` reaches the backend due to trailing slash differences hitting different Nginx locations
2. **Exact-match gaps**: `/private/` requires auth but `/private/index.html` bypasses it when authentication applies only to the exact path
3. **Location precedence**: `/static/internal/users` blocked but `/static/internal/users.json` allowed when regex locations (e.g., matching `.json`) override prefix denies
4. **Header-based bypasses**: `/local/` grants access when `X-Forwarded-For: 127.0.0.1` is present, `/user_agent` allows specific `User-Agent` values. Demonstrates risks of trusting client-controlled headers for authorization
5. **API version downgrade**: `/api/v2/secrets` protected but `/api/v1/secrets` remains accessible (legacy path forgotten in proxy rules)

**A complete list of vulnerable endpoints with detailed descriptions is available at the root endpoint** when the lab is running. This index page documents each vulnerability class, the expected behavior, and hints for exploitation.

## Disclaimer

FBpsLab is a deliberately insecure laboratory for educational use. Do **NOT** deploy it on exposed or production systems.
