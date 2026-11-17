

import cv2
import serial
import time
from ultralytics import YOLO

# ===================================
# CONFIGURACION DE ESP32
# ===================================

PUERTO = "COM3"
VELOCIDAD = 115200

print("Conectando con ESP32...")

esp32 = serial.Serial(PUERTO, VELOCIDAD, timeout=1)

# Esperar a que la ESP32 se reinicie
time.sleep(2)

print("ESP32 conectada correctamente")

# ===================================
# INTELIGENCIA ARTIFICIAL
# ===================================

modelo = YOLO("yolo11n.pt")

camara = cv2.VideoCapture(0)

if not camara.isOpened():
    esp32.close()
    raise SystemExit("ERROR: No se pudo abrir la camara")

ultimo_mensaje = ""

print("Sistema de seguridad iniciado")
print("Presiona Q para salir")

# ===================================
# DETECCION Y COMUNICACION
# ===================================

try:
    while True:
        correcto, imagen = camara.read()

        if not correcto:
            print("Error al capturar imagen")
            break

        # Detectar personas mediante IA
        resultados = modelo.predict(
            imagen,
            classes=[0],
            conf=0.5,
            imgsz=320,
            device="cpu",
            verbose=False
        )

        personas = len(resultados[0].boxes)

        # Determinar el mensaje
        if personas > 0:
            mensaje = "AI:PERSON"
        else:
            mensaje = "AI:EMPTY"

        # Enviar mensaje cuando cambie
        if mensaje != ultimo_mensaje:
            esp32.write((mensaje + "\n").encode())
            esp32.flush()

            print("Enviado a ESP32:", mensaje)

            ultimo_mensaje = mensaje

        # Mostrar detecciones en pantalla
        imagen = resultados[0].plot()

        cv2.imshow("Seguridad con IA + ESP32", imagen)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Apagar LED al finalizar
    try:
        esp32.write(b"AI:EMPTY\n")
        esp32.flush()
    except serial.SerialException:
        pass

    camara.release()
    esp32.close()
    cv2.destroyAllWindows()

    print("Sistema finalizado")
