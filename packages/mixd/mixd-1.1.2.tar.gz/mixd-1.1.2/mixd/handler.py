import os
import sys
import datetime
from http.server import SimpleHTTPRequestHandler
from base64 import b64decode
from urllib.parse import unquote
from rich.console import Console
from .utils import save_log
import random
import string

console = Console()

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    server_version = "mixd/1.1"
    sys_version = ""

    mixd_api_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def __init__(self, *args, directory=None, log_file=None, enable_logs=True, log_level="info",
                 username=None, password=None, require_auth=False, no_logs=False, **kwargs):
        self.log_file = log_file
        self.enable_logs = enable_logs
        self.log_level = log_level
        self.username = username
        self.password = password
        self.require_auth = require_auth
        self.no_logs = no_logs
        super().__init__(*args, directory=directory, **kwargs)

    # --------------------
    # Logging
    # --------------------
    def log_message(self, format, *args):
        if self.no_logs:
            return
        msg = "%s - - [%s] %s" % (
            self.client_address[0],
            self.log_date_time_string(),
            format % args
        )
        console.log(msg)
        if self.log_file:
            save_log(self.log_file, msg)

    # --------------------
    # Authentication
    # --------------------
    def check_auth(self):
        if not self.require_auth:
            return True
        auth_header = self.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Basic "):
            return False
        encoded = auth_header.split(" ", 1)[1].strip()
        decoded = b64decode(encoded).decode('utf-8')
        username, password = decoded.split(":", 1)
        return username == self.username and password == self.password

    def send_auth_request(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="mixd"')
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Authentication required")

    # --------------------
    # HTTP Methods
    # --------------------
    def do_HEAD(self):
        if self.require_auth and not self.check_auth():
            self.send_auth_request()
            return
        super().do_HEAD()

    def do_GET(self):
        if self.require_auth and not self.check_auth():
            self.send_auth_request()
            return

        path = self.translate_path(self.path)

        if os.path.exists(path) and not os.path.isdir(path):
            if path.endswith(".html"):
                self.serve_html(path)
            else:
                super().do_GET()
        elif os.path.isdir(path):
            index_path = os.path.join(path, "index.html")
            if os.path.exists(index_path):
                self.path = os.path.join(self.path, "index.html")
                return self.do_GET()
            else:
                self.list_directory(path)
        else:
            self.serve_404()

    # --------------------
    # HTML Serving
    # --------------------
    def serve_html(self, path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        footer = f"""
        <hr>
        <p style="text-align:center; font-size:0.8em; color:#888;">
            Powered by mixd | mixdAPI: <strong>{self.mixd_api_key}</strong> | mixdTime: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ⚡
        </p>
        """

        if "</body>" in content:
            content = content.replace("</body>", f"{footer}</body>")
        else:
            content += footer

        encoded = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    # --------------------
    # 404 Page
    # --------------------
    def serve_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content = """
        <html><head><title>404 Not Found</title></head>
        <body style="font-family:sans-serif; text-align:center; margin-top:50px;">
        <h1>404 - page not found</h1>
        <p>Oops! The page you requested does not exist.</p>
        </body></html>
        """
        self.wfile.write(content.encode('utf-8'))

    # --------------------
    # Directory Listing
    # --------------------
    def list_directory(self, path):
        try:
            listing = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None
        listing.sort(key=lambda a: a.lower())
        r = []
        displaypath = unquote(self.path)
        r.append(f'<!DOCTYPE html><html><head><title>Directory listing for {displaypath}</title>'
                 f'<style>body{{font-family:sans-serif; background:#f9f9f9;}}ul{{list-style:none;padding:0;}}li{{margin:5px 0;}}'
                 f'a{{text-decoration:none;color:#0366d6;}}a:hover{{text-decoration:underline;}}</style></head>')
        r.append('<body>')
        r.append(f'<h2>Directory listing for {displaypath}</h2>')
        r.append('<hr><ul>')
        for name in listing:
            fullname = os.path.join(path, name)
            displayname = name + ("/" if os.path.isdir(fullname) else "")
            linkname = name + ("/" if os.path.isdir(fullname) else "")
            r.append(f'<li><a href="{linkname}">{displayname}</a></li>')
        r.append('</ul><hr></body></html>')
        encoded = '\n'.join(r).encode('utf-8')
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None
