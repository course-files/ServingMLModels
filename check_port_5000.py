"""
check_port.py

Run this BEFORE `python api.py` to confirm that the port Flask will use is
free. It works the same way in Command Prompt, PowerShell, Git Bash, macOS
Terminal, and Linux, because Python calls the system tools directly instead
of going through your shell.

Usage:
    python check_port.py          # checks port 5000 (Flask's default)
    python check_port.py 5050     # checks any other port
"""

import errno
import platform
import socket
import subprocess
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
HOST = "127.0.0.1"  # the address Flask's app.run() binds to by default
IS_WINDOWS = platform.system() == "Windows"


def find_listeners(port):
    """Return a list of (pid, process_name) for processes listening on the port."""
    listeners = []
    try:
        if IS_WINDOWS:
            output = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True
            ).stdout
            pids = set()
            for line in output.splitlines():
                parts = line.split()
                # Columns: Proto  Local Address  Foreign Address  State  PID
                # A listening socket has a foreign address of 0.0.0.0:0 or [::]:0.
                if (
                    len(parts) == 5
                    and parts[0] == "TCP"
                    and parts[1].endswith(f":{port}")
                    and parts[2] in ("0.0.0.0:0", "[::]:0")
                ):
                    pids.add(parts[4])
            for pid in sorted(pids, key=int):
                row = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                    capture_output=True, text=True,
                ).stdout.strip()
                name = row.split(",")[0].strip('"') if row.startswith('"') else "unknown"
                listeners.append((pid, name))
        else:
            output = subprocess.run(
                ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"],
                capture_output=True, text=True,
            ).stdout
            seen = set()
            for line in output.splitlines()[1:]:
                parts = line.split()
                if parts[1] not in seen:
                    seen.add(parts[1])
                    listeners.append((parts[1], parts[0]))
    except FileNotFoundError:
        print("  (Could not find netstat/lsof to identify the process.)")
    return listeners


def print_listeners(listeners):
    print(f"\nThe following application(s) are listening on port {PORT}:\n")
    for pid, name in listeners:
        print(f"  PID {pid:>7}   {name}")
    print("\nIf you recognise the application and it is safe to close, close it")
    print("normally, or terminate it with:\n")
    pid = listeners[0][0]
    if IS_WINDOWS:
        print(f"  Command Prompt / PowerShell:  taskkill /PID {pid} /F")
        print(f"  Git Bash:                     taskkill //PID {pid} //F")
        if any(p == "4" for p, _ in listeners):
            print("\n  NOTE: PID 4 is the Windows 'System' process. Do NOT try to")
            print("  terminate it. Run api.py on a different port instead.")
    else:
        print(f"  kill {pid}")
    print("\nIf you do not recognise it, do not terminate it. Use another port")
    print("instead, e.g. app.run(debug=True, port=5050).")


def main():
    print(f"Checking whether {HOST}:{PORT} is available for Flask...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((HOST, PORT))
    except OSError as error:
        winerror = getattr(error, "winerror", None)
        listeners = find_listeners(PORT)

        if listeners:
            print(f"\n[BLOCKED] Port {PORT} is already in use.")
            print_listeners(listeners)
        elif winerror == 10013:
            print(f"\n[BLOCKED] Port {PORT} is reserved by Windows, but no application")
            print("is using it. This is usually caused by Hyper-V, WSL 2, or Docker.")
            print("\nTo confirm, run this command and see whether the port falls")
            print("inside one of the listed ranges:\n")
            print("  netsh interface ipv4 show excludedportrange protocol=tcp")
            print("\nThe simplest fix is to run api.py on a different port,")
            print("e.g. app.run(debug=True, port=5050).")
        elif error.errno == errno.EADDRINUSE or winerror == 10048:
            print(f"\n[BLOCKED] Port {PORT} is in use, but the application could not")
            print("be identified. Use a different port instead.")
        else:
            print(f"\n[BLOCKED] Port {PORT} cannot be used: {error}")
        sys.exit(1)
    finally:
        sock.close()

    print(f"\n[OK] Port {PORT} is free. You can now run: python api.py")


if __name__ == "__main__":
    main()
