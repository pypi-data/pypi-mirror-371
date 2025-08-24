import yaml
import subprocess
import os
import sys
import shutil
from sshup import __version__

# Try to import curses, use a fallback on Windows
try:
    import curses
except ImportError:
    if os.name == 'nt':
        try:
            import pip
            subprocess.run([sys.executable, "-m", "pip", "install", "windows-curses"])
            import curses
        except Exception:
            curses = None
    else:
        curses = None

DEFAULT_CONFIG = """servers:
  - name: My VPS
    host: user@123.45.67.89
  - name: Dev Server
    host: devuser@10.0.0.5
  - name: Production
    host: root@prod.example.com
"""

CONFIG_DIR = os.path.expanduser("~/.sshup")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")

def ensure_config():
    """Create default config if it doesn't exist."""
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            f.write(DEFAULT_CONFIG)

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)["servers"]

def draw_menu(stdscr, servers, selected_idx):
    stdscr.clear()
    stdscr.addstr(0, 0, "Select a server and press Enter to SSH:", curses.A_BOLD)

    for idx, server in enumerate(servers):
        x = 2
        y = idx + 2
        if idx == selected_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, f"> {server['name']} ({server['host']})")
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, f"  {server['name']} ({server['host']})")

    stdscr.refresh()

def run_launcher(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    servers = load_config(CONFIG_FILE)
    current_idx = 0

    while True:
        draw_menu(stdscr, servers, current_idx)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
        elif key == curses.KEY_DOWN and current_idx < len(servers) - 1:
            current_idx += 1
        elif key in [curses.KEY_ENTER, 10, 13]:  # Enter key
            selected_server = servers[current_idx]["host"]
            curses.endwin()  # Close curses UI
            subprocess.run(["ssh", selected_server])
            break
        elif key == 27:  # ESC to quit
            break

def edit_config():
    """Open the config in the user's editor (cross-platform)."""
    editor = os.environ.get("EDITOR")
    if not editor:
        if os.name == "nt":
            # Use notepad on Windows
            subprocess.run(["notepad", CONFIG_FILE])
        else:
            # Use nano or vi on Unix-like systems
            editor = "nano" if shutil.which("nano") else "vi"
            subprocess.run([editor, CONFIG_FILE])
    else:
        # Environment variable defined
        subprocess.run([editor, CONFIG_FILE])

def list_servers():
    """Print all configured servers."""
    servers = load_config(CONFIG_FILE)
    print("Configured servers:")
    for s in servers:
        print(f"- {s['name']} ({s['host']})")

def run_command_on_server(stdscr, servers, command):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    current_idx = 0
    while True:
        draw_menu(stdscr, servers, current_idx)
        stdscr.addstr(len(servers) + 3, 2, f"Command: {command}", curses.A_DIM)
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
        elif key == curses.KEY_DOWN and current_idx < len(servers) - 1:
            current_idx += 1
        elif key in [curses.KEY_ENTER, 10, 13]:  # Enter
            selected_server = servers[current_idx]["host"]
            curses.endwin()  # Exit TUI before running command
            subprocess.run(["ssh", "-t", selected_server, command])
            break
        elif key == 27:  # ESC
            break

def print_version():
    print(f"sshup version {__version__}")

def print_help():
    """Show available options."""
    help_text = """
sshup - A simple SSH Manager

Commands:
  sshup             Start the interactive menu
  sshup --edit      Open the config file in your default editor
  sshup --list      List configured servers
  sshup --cmd       Run a command on the host
  sshup --version   Get sshup version number
  sshup --help      Show this help message

Flags:
  -e, --edit    Edit the config file
  -l, --list    List all servers
  -c, --cmd     Run command on host
  -v, --version Show version number
  -h, --help    Show this help message
"""
    print(help_text.strip())

def main():
    ensure_config()

    # Check for command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("--edit", "-e"):
            edit_config()
            return
        elif arg in ("--list", "-l"):
            list_servers()
            return
        elif arg in ("--cmd", "-c"):
            if len(sys.argv) < 3:
                print("Usage: sshup --cmd <command>")
                return
            command = " ".join(sys.argv[2:])
            servers = load_config(CONFIG_FILE)
            curses.wrapper(run_command_on_server, servers, command)
            return
        elif arg in ("--version", "-v"):
            print_version()
            return
        elif arg in ("--help", "-h"):
            print_help()
            return
        else:
            print(f"Unknown option: {arg}\n")
            print_help()
            return
    
    curses.wrapper(run_launcher)
