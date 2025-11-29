import socket as sock

# Crear socket UDP
miSocket = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)

# Asociar el socket a una dirección IP y puerto
miSocket.bind(('', 8003))

print('Servidor UDP de Yael escuchando en el puerto 8003...')

while True:
    # Recibir datos (máx 1024 bytes)
    data, addr = miSocket.recvfrom(1024)
    print(f"Mensaje recibido de {addr}: {data.decode('utf-8')}")

    # Responder al cliente
    miSocket.sendto(b'Hola desde el servidor UDP de Yael!',addr)