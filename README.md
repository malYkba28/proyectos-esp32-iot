# Proyectos con ESP32, IoT y visión por computadora

Prácticas de la materia de **Sistemas Embebidos**: desde control básico de pines con **MicroPython** hasta sistemas que combinan **visión por computadora** en la laptop con un **ESP32** que actúa en el mundo físico (LEDs, servo y buzzer).

**Tecnologías:** ESP32, MicroPython, C++ (Arduino/PlatformIO), Python, OpenCV, YOLO (Ultralytics), MQTT (Mosquitto), comunicación serial UART y sockets TCP.

## Proyectos

| # | Proyecto | Qué hace | Tecnologías |
|---|---|---|---|
| 01 | Semáforo peatonal | Al presionar un botón, el semáforo pasa de rojo a precaución y verde con cuenta regresiva y antirrebote. | MicroPython, GPIO |
| 02 | Control de LED por serial | Enciende o apaga un LED según el comando recibido (`ALERT` / `NORMAL`). | MicroPython, UART |
| 03 | Clasificador por color con cámara | La laptop analiza la cámara con OpenCV (HSV) y envía `CLASS:OK` o `CLASS:DEFECT` al ESP32, que enciende un LED verde o rojo. | OpenCV, pyserial, MicroPython |
| 04 | Ventilación con TCP/IP | Un sensor virtual envía la temperatura a un sistema embebido virtual mediante sockets en localhost. | Python, sockets TCP |
| 05 | Detección de personas con YOLO | YOLO11n detecta personas en la cámara y avisa al ESP32 por serial (`AI:PERSON` / `AI:EMPTY`). | YOLO, OpenCV, pyserial |
| 06 | Cerradura con reconocimiento facial | La laptop reconoce rostros y publica `conocido` o `desconocido` por MQTT. El ESP32 abre la puerta con un servo o activa alarma con buzzer y LED rojo. | OpenCV (YuNet + SFace), MQTT, MicroPython, C++ |

## Proyecto destacado: cerradura con reconocimiento facial

```
Cámara → Laptop (OpenCV: detecta y reconoce el rostro) → MQTT (Mosquitto) → ESP32 → Servo / LEDs / Buzzer
```

- **Detección:** modelo YuNet.
- **Reconocimiento:** modelo SFace, comparando contra las fotos de `caras_conocidas/` con similitud coseno (umbral 0.363).
- **Estabilidad:** solo publica un cambio cuando el resultado se mantiene 5 cuadros seguidos, para evitar parpadeos.
- **ESP32:** se reconecta solo si se cae el WiFi o el broker, y valida que el broker sea alcanzable antes de conectar.
- Incluye dos versiones del código del ESP32: **MicroPython** (servo, LEDs y buzzer) y **C++ con PlatformIO** (LEDs).

### Cómo ejecutarlo

1. Instala y abre **Mosquitto** en la laptop.
2. Descarga los modelos `face_detection_yunet_2023mar.onnx` y `face_recognition_sface_2021dec.onnx` desde el repositorio **opencv_zoo** de OpenCV y colócalos en `06-cerradura-reconocimiento-facial/pc/`.
3. Pon fotos de las personas autorizadas en `pc/caras_conocidas/`. El nombre del archivo será el nombre mostrado. Por privacidad, este repositorio no incluye fotos.
4. En `esp32_micropython/main.py` cambia `WIFI_SSID`, `WIFI_PASS` y `MQTT_IP`. En `pc/detecta_rostros_mqtt.py` cambia `BROKER_IP`.
5. Carga `main.py` al ESP32 (por ejemplo con Thonny) y ejecuta:

```bash
pip install opencv-python numpy paho-mqtt
python detecta_rostros_mqtt.py
```

## Otros proyectos

- **01 y 02:** carga el archivo al ESP32 con Thonny.
- **03:** carga `esp32_leds.py` al ESP32, ajusta `PUERTO` (por ejemplo `COM3`) en `pc_ia_camara.py` y ejecútalo.
- **05:** ajusta `PUERTO` en `detectar_personas.py` e instala `ultralytics`; el modelo `yolo11n.pt` se descarga solo la primera vez. Este repositorio incluye solo la parte de la laptop.
- **04:** ejecuta primero `servidor.py` y luego `sensor.py`.
