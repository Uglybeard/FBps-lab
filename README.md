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

FBpsLab demonstrates common misconfigurations that lead to 401/403 bypasses: location matching edge cases (prefix vs exact-match, trailing slashes), regex vs prefix precedence issues, unsafe header-based controls (forwarded headers), normalization discrepancies between proxy and backend, legacy/versioned API paths where newer versions are protected but older ones remain accessible, case-sensitivity mismatches, and allowlist logic based on client-controlled patterns.

Backend endpoints return clear responses confirming whether requests were blocked at the proxy or reached the application.

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

### Hostname setup (Recommended)

Nginx is configured to serve requests for the hostname `fbps.com`.

For the most realistic reverse-proxy behavior, map that name to localhost:

**On Linux/macOS**, edit:
```
/etc/hosts
```

**On Windows** (as Administrator), edit:
```
C:\Windows\System32\drivers\etc\hosts
```

Add this line:
```
127.0.0.1 fbps.com
```

Then you can test via: http://fbps.com/

### Alternative (No Hosts File Change)

If you cannot edit hosts, you can still target localhost and force the Host header, e.g.:

```bash
curl -i http://127.0.0.1/ -H "Host: fbps.com"
```

or

```bash
python3 fbps.py -H "Host: fbps.com" http://127.0.0.1
```

## Disclaimer

FBpsLab is a deliberately insecure laboratory for educational use.
Do not deploy it on exposed or production systems.
