import socket

HOST = "127.0.0.1"
PORT = 5000

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORT))

print("SENSOR VIRTUAL")
print("Conectado al sistema embebido de Kevin Yahir Bernal Aguirre.")

temperatura = 25.5
mensaje = str(temperatura)
cliente.sendall(mensaje.encode("utf-8"))

mensaje = str(temperatura)
cliente.sendall(mensaje.encode("utf-8"))

print("Temperatura enviada: ", temperatura, "*C")
cliente.close()