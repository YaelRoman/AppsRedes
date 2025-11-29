import socket

HOST = "0.0.0.0"
PORT = 8001
ENC = "utf-8"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(1)
    print(f"Listening on {HOST}:{PORT} ...")

    conn, addr = srv.accept()
    with conn:
        print(f"Connection from {addr}")

        # Text-mode file wrappers give you clean line I/O
        rfile = conn.makefile("r", encoding=ENC, newline="\n")
        wfile = conn.makefile("w", encoding=ENC, newline="\n")

        while True:
            line = rfile.readline()          # blocks until a full line or EOF
            if not line:                     # client closed connection
                print("Client closed the connection.")
                break

            msg = line.rstrip("\n")
            print(f"Client: {msg}", flush=True)

            # Prompt AFTER receiving a full message
            try:
                reply = input("You: ")
            except (EOFError, KeyboardInterrupt):
                reply = "exit"

            wfile.write(reply + "\n")        # send with newline terminator
            wfile.flush()

            if reply.strip().lower() in {"exit", "quit"}:
                break



