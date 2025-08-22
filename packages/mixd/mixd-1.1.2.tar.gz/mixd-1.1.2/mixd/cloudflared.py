import subprocess
import threading
from rich.console import Console

console = Console()

def run_cloudflared(port):
    try:
        subprocess.run(["cloudflared", "--version"], check=True, stdout=subprocess.DEVNULL)
    except Exception:
        console.print("[red]cloudflared is not installed or not in PATH[/red]")
        raise SystemExit(1)

    console.print("[cyan]Starting cloudflared tunnel...[/cyan]")
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    def grab_url():
        for line in proc.stdout:
            if "trycloudflare.com" in line:
                url = line.strip().split()[-1]
                console.print(f"[bold green]Cloudflare Tunnel:[/bold green] {url}")
                break

    threading.Thread(target=grab_url, daemon=True).start()
    return proc
