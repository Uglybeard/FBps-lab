import os
from flask import Flask, Response, send_from_directory, abort, render_template, request


class CaseInsensitivePrefixMiddleware:
    def __init__(self, wsgi_app, prefix: str):
        self.wsgi_app = wsgi_app
        self.prefix = prefix.rstrip("/")
        self.prefix_slash = self.prefix + "/"

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "") or ""
        lower = path.lower()

        if lower == self.prefix or lower.startswith(self.prefix_slash):
            environ["PATH_INFO"] = lower

        return self.wsgi_app(environ, start_response)

app = Flask(__name__)
app.url_map.strict_slashes = False

# Make only /services/myservice/* case-insensitive
app.wsgi_app = CaseInsensitivePrefixMiddleware(app.wsgi_app, "/services/myservice")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRIVATE_DIR = os.path.join(BASE_DIR, "private")

def render_index_with_dynamic_length():
    # Fixed-point iteration: find L such that L == len(render(index_len=L))
    index_len = 0
    html = render_template("index.html", index_len=index_len)

    for _ in range(5):
        index_len = len(html.encode("utf-8"))
        new_html = render_template("index.html", index_len=index_len)
        new_len = len(new_html.encode("utf-8"))

        if new_len == index_len:
            # Stable length found
            return new_html

        html = new_html

    # Fallback: return last render even if not perfectly stable
    return html

@app.get("/")
def index():
    html = render_index_with_dynamic_length()
    return Response(html, mimetype="text/html")

@app.get("/admin/")
def admin_page():
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Admin Area</title>
</head>
<body>
  <h1>Admin Area</h1>
  <p><strong>This page should be protected.</strong></p>
  <p>
    If you are seeing this page while <code>/admin/</code> returns
    <code>403 Forbidden</code>, you have successfully bypassed an
    access control restriction.
  </p>
</body>
</html>"""
    return Response(html, mimetype="text/html")

@app.get("/private/")
def private_index():
    return send_from_directory(PRIVATE_DIR, "index.html")

@app.get("/private/<path:filename>")
def private_files(filename):
    # basic hardening against weird paths
    if ".." in filename or filename.startswith("/"):
        abort(400)
    return send_from_directory(PRIVATE_DIR, filename)

@app.get("/local/")
def local_only_page():
  return """
<head>
  <title>Local Area</title>
</head>
<body>
  <h1>Local Area</h1>
  <p><strong>This page should be protected.</strong></p>
  <p>
    Access to <code>/local</code> is intended to be allowed only when the
    <code>X-Forwarded-For</code> header indicates <code>127.0.0.1</code>.
  </p>
  <p>
    If you are seeing this page while <code>/local</code> normally returns
    <code>403 Forbidden</code>, you have successfully bypassed an
    <code>X-Forwarded-For</code>-based access control restriction.
  </p>
</body>
""", 200

@app.get("/trim")
def trim_inconsistency():
    return """
<head>
  <title>Trim Inconsistency</title>
</head>
<body>
  <h1>Trim Inconsistency</h1>
  <p><strong>This page should be protected.</strong></p>
  <p>
    Access to <code>/trim</code> is intended to be denied. The protection rule
    relies on an “exact match” check performed by <strong>nginx</strong> on the
    incoming request path.
  </p>
  <p>
    If you are seeing this page while an equivalent request normally returns
    <code>403 Forbidden</code>, you have exploited a <em>trim inconsistency</em>
    between <strong>nginx</strong> and <strong>Flask</strong>: nginx evaluates
    one version of the path, but Flask receives a differently trimmed/decoded
    version (e.g., due to whitespace or non-printable characters), allowing the
    request to bypass the intended restriction.
  </p>
</body>
""", 200

@app.get("/api/v1/secrets")
def api_version_downgrade():
    return """
<head>
  <title>API Version Downgrade</title>
</head>
<body>
  <h1>API Version Downgrade</h1>
  <p><strong>This endpoint should be protected.</strong></p>
  <p>
    Access to <code>/api/v2/secrets</code> is intended to be denied by an
    upstream rule, while <code>/api/v1/secrets</code> is supposed to be
    retired or equally protected.
  </p>
  <p>
    If you are seeing this page while a request to <code>/api/v2/secrets</code>
    returns <code>403 Forbidden</code>, you have exploited an
    <em>API version downgrade</em>: the newer version is blocked, but the
    legacy <code>v1</code> endpoint is still accessible.
  </p>
</body>
""", 200


@app.get("/user_agent")
def user_agent_allowlist():
    return """
<head>
  <title>User-Agent Allowlist</title>
</head>
<body>
  <h1>User-Agent Allowlist</h1>
  <p><strong>This endpoint should be protected.</strong></p>
  <p>
    Access to <code>/user_agent</code> is intended to be denied by an upstream
    rule unless the request’s <code>User-Agent</code> matches an allowlist
    pattern (e.g. <code>^FBps(\\b|/|$)</code>).
  </p>
  <p>
    If you are seeing this page while requests without a matching User-Agent
    return <code>403 Forbidden</code>, you have satisfied the allowlist by
    sending an accepted value such as <code>FBps/1.0</code>.
  </p>
</body>
""", 200

@app.get("/services/myservice/status")
def myservice_status():
    return """
<head>
  <title>MyService Status</title>
</head>
<body>
  <h1>MyService Status</h1>
  <p><strong>This endpoint should be protected.</strong></p>
  <p>
    Access to <code>/services/myservice/status</code> is intended to be denied by an upstream
    rule that is incorrectly configured to match only a specific letter case
    (e.g., it blocks <code>/services/myservice/status</code> but not
    <code>/SERVICES/MYSERVICE/STATUS</code>).
  </p>
  <p>
    If you are seeing this page while a request to the canonical lowercase URL returns
    <code>403 Forbidden</code>, you have successfully bypassed access control via a
    <em>case mismatch</em>.
  </p>
</body>
""", 200
