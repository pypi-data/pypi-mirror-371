import argparse
from .server import run_server

def main():
    parser = argparse.ArgumentParser(description="Mixd HTTP Dev Server")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--file", type=str, default="index")
    parser.add_argument("--mode", choices=["dev", "prod"], default="dev")
    parser.add_argument("--cloudflared", action="store_true")
    parser.add_argument("--logs", action="store_true")
    parser.add_argument("--minlog", choices=["debug", "info", "warn"], default="info")
    parser.add_argument("--no-pass", action="store_true")
    parser.add_argument("--set-password", type=str, help="Set custom password")
    args = parser.parse_args()

    run_server(args)

if __name__ == "__main__":
    main()
