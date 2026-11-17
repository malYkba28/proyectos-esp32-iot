import socket

HOST = "127.0.0.1"
PORT = 5000

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORT))
servidor.listen()

print("SISTEMA EMBEBIDO VIRTUAL DE Kevin Yahir Bernal Aguirre")
print("Esperando conexión del sensor...")

conexion, direccion = servidor.accept()

print("Sensor conectado.")  

datos = conexion.recv(1024)
temperatura = datos.decode("utf-8")

print("Temperatura recibida: ", temperatura, "*C")

conexion.close()
servidor.close()