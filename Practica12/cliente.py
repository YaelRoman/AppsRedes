import socket

SERVER_HOST = "192.168.0.105"
PORT = 8001
ENC = "utf-8"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cli:
    cli.connect((SERVER_HOST, PORT))
    print(f"Connected to {SERVER_HOST}:{PORT}")

    # Wrap in text-mode files for clean line I/O
    rfile = cli.makefile("r", encoding=ENC, newline="\n")
    wfile = cli.makefile("w", encoding=ENC, newline="\n")

    while True:
        try:
            msg = input("You: ")
        except (EOFError, KeyboardInterrupt):
            msg = "exit"

        # Send one line (newline-terminated)
        wfile.write(msg + "\n")
        wfile.flush()

        if msg.strip().lower() in {"exit", "quit"}:
            break

        # Wait for one full line from server
        line = rfile.readline()
        if not line:  # server closed
            print("Server closed the connection.")
            break

        print(f"Server: {line.rstrip()}")
