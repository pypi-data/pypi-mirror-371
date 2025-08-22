import os
import sys
import ssl
import time
import socketserver
import subprocess
from rich.console import Console
from rich.panel import Panel
from .utils import clear_console, get_external_ip, generate_password, generate_username
from .handler import CustomHTTPRequestHandler
from .cloudflared import run_cloudflared

console = Console()

def run_server(args):
    clear_console()
    console.print(Panel.fit(f"🚀  starting {args.mode} server", style="bold green"))

    directory = os.getcwd()
    file_to_serve = f"{args.file}.html"

    if not os.path.exists(os.path.join(directory, file_to_serve)):
        console.print("[red]index not found, stopped[/red]")
        sys.exit(1)

    username = None
    password = None
    require_auth = False

    if args.mode == "dev" and (args.cloudflared or not args.no_pass):
        password = args.set_password if args.set_password else generate_password()
        username = generate_username()
        require_auth = True
        console.print(f"[bold yellow]username:[/bold yellow] {username}")
        console.print(f"[bold yellow]password:[/bold yellow] {password}")

    log_file = os.path.join(directory, f"server_{time.strftime('%Y%m%d_%H%M%S')}.log") if args.logs else None

    class HandlerFactory:
        def __call__(self, *handler_args, **handler_kwargs):
            return CustomHTTPRequestHandler(
                *handler_args,
                directory=directory,
                log_file=log_file,
                enable_logs=args.logs,
                log_level=args.minlog,
                username=username,
                password=password,
                require_auth=require_auth,
                no_logs=not args.logs,
                **handler_kwargs
            )

    with socketserver.ThreadingTCPServer(("localhost", args.port), HandlerFactory()) as httpd:
        httpd.allow_reuse_address = True
        ext_ip = get_external_ip()

        # HTTPS setup
        cert_file = os.path.join(directory, "cert.pem")
        key_file = os.path.join(directory, "key.pem")

        if not (os.path.exists(cert_file) and os.path.exists(key_file)):
            console.print("[yellow]Generating self-signed certificate...[/yellow]")
            subprocess.run([
                "openssl", "req", "-new", "-x509", "-days", "365",
                "-nodes", "-out", cert_file, "-keyout", key_file,
                "-subj", "/CN=localhost"
            ], check=True)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

        console.print(f"[bold cyan]mode[/bold cyan] {args.mode}")
        console.print(f"[bold cyan]host[/bold cyan] localhost")
        console.print(f"[bold cyan]port[/bold cyan] {args.port}")
        console.print(f"[bold cyan]file[/bold cyan] {file_to_serve}")
        console.print(f"[bold cyan]directory[/bold cyan] {directory}")
        console.print(f"HTTPS enabled: {cert_file} + {key_file}")

        if args.cloudflared:
            run_cloudflared(args.port)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("[red]Server stopped[/red]")
            httpd.server_close()
