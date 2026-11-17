import glob
import os
import time

import cv2
import numpy as np
import paho.mqtt.client as mqtt

# ====== CONFIGURACION ======
BROKER_IP = "192.168.1.50"      # <-- IP de la laptop con Mosquitto
BROKER_PORT = 1883
TOPIC = "casa/rostro/estado"
CARPETA_CONOCIDOS = "caras_conocidas"
UMBRAL_COSENO = 0.363           # recomendado para SFace; subir = mas estricto
FRAMES_ESTABLES = 5             # frames seguidos iguales antes de publicar
SEGUNDOS_SIN_ROSTRO = 3         # tras esto se "reinicia" y se vuelve a publicar
MODELO_DET = "face_detection_yunet_2023mar.onnx"
MODELO_REC = "face_recognition_sface_2021dec.onnx"
# ===========================

# --- MQTT ---
cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="detector_rostro")
cliente.connect_async(BROKER_IP, BROKER_PORT)
cliente.loop_start()  # reconecta solo si el broker cae

# --- Modelos ---
detector = cv2.FaceDetectorYN.create(MODELO_DET, "", (320, 320), 0.8, 0.3, 5000)
reconocedor = cv2.FaceRecognizerSF.create(MODELO_REC, "")


def embedding(img, cara):
    alineada = reconocedor.alignCrop(img, cara)
    return reconocedor.feature(alineada)


# --- Cargar rostros conocidos ---
conocidos = {}
for ruta in glob.glob(os.path.join(CARPETA_CONOCIDOS, "*")):
    img = cv2.imread(ruta)
    if img is None:
        continue
    detector.setInputSize((img.shape[1], img.shape[0]))
    _, caras = detector.detect(img)
    if caras is None:
        print(f"AVISO: sin rostro en {ruta}")
        continue
    nombre = os.path.splitext(os.path.basename(ruta))[0]
    conocidos[nombre] = embedding(img, caras[0])
print(f"Rostros conocidos cargados: {list(conocidos)}")
if not conocidos:
    raise SystemExit("ERROR: agrega fotos en la carpeta caras_conocidas/")

camara = cv2.VideoCapture(0)
if not camara.isOpened():
    raise SystemExit("ERROR: No se pudo abrir la camara")

ultimo_publicado = None
candidato, contador = None, 0
ultima_vez_con_rostro = time.time()

print("Presiona Q para salir")
try:
    while True:
        ok, frame = camara.read()
        if not ok:
            print("Error al capturar imagen")
            break

        detector.setInputSize((frame.shape[1], frame.shape[0]))
        _, caras = detector.detect(frame)

        if caras is not None:
            ultima_vez_con_rostro = time.time()
            hay_conocido = False
            for cara in caras:
                feat = embedding(frame, cara)
                mejor, mejor_nombre = 0.0, None
                for nombre, ref in conocidos.items():
                    s = reconocedor.match(feat, ref, cv2.FaceRecognizerSF_FR_COSINE)
                    if s > mejor:
                        mejor, mejor_nombre = s, nombre
                es_conocido = mejor >= UMBRAL_COSENO
                hay_conocido = hay_conocido or es_conocido

                x, y, w, h = cara[:4].astype(int)
                color = (0, 200, 0) if es_conocido else (0, 0, 255)
                etiqueta = mejor_nombre if es_conocido else "desconocido"
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, etiqueta, (x, y - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            estado = "conocido" if hay_conocido else "desconocido"

            # Estabilizar para evitar parpadeos
            if estado == candidato:
                contador += 1
            else:
                candidato, contador = estado, 1

            if contador >= FRAMES_ESTABLES and estado != ultimo_publicado:
                cliente.publish(TOPIC, estado, qos=1)
                print(f"Publicado {TOPIC} = {estado}")
                ultimo_publicado = estado

        elif time.time() - ultima_vez_con_rostro > SEGUNDOS_SIN_ROSTRO:
            # Nadie frente a la camara: permite re-publicar al volver
            ultimo_publicado, candidato, contador = None, None, 0

        cv2.imshow("Detector de rostro -> MQTT", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    camara.release()
    cv2.destroyAllWindows()
    cliente.loop_stop()
    cliente.disconnect()
    print("Sistema finalizado")