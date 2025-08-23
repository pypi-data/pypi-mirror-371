#!/usr/bin/env python
import os
import sys
from wsgiref.simple_server import make_server
from rich.console import Console

console = Console()

class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    GRAY = "\033[90m"
    RED = "\033[91m"
    GREEN = "\033[92m"


def cprint(text, color=Color.RESET):
    print(f"{color}{text}{Color.RESET}")


def main():

    project_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    os.environ['DJANGINEER_PROJECT_PATH'] = project_path

    # Point to your Django settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangineer.config.settings")

    # Import the WSGI app
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

    # Start WSGI server
    port = 8000
    with make_server("127.0.0.1", port, application) as httpd:
        cprint("🎨 Djangineer IDE running", Color.MAGENTA)
        cprint(f"🚀 Project path: {project_path}", Color.CYAN)
        cprint(f"🌍 Open in browser: http://127.0.0.1:{port}", Color.YELLOW)
        cprint("Press CTRL+C to quit", Color.GRAY)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\n🛑 Djangineer IDE stopped")

if __name__ == "__main__":
    main()
