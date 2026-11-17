from machine import Pin, PWM, unique_id
import network
import socket
import time
import ubinascii
from umqtt.simple import MQTTClient, MQTTException

# ====== CONFIGURACION ======
WIFI_SSID = "NOMBRE_DE_TU_RED"       # <-- cambia por tu red WiFi
WIFI_PASS = "CONTRASENA_DE_TU_RED"   # <-- cambia por tu contrasena
MQTT_IP = "192.168.1.50"         # IPv4 de la laptop con Mosquitto (verificar con ipconfig)
BROKER_PORT = 1883
MQTT_USER = None                 # poner usuario/contrasena si el broker los exige
MQTT_PASS = None
ID_DISPOSITIVO = "esp32_02"      # unico en cada ESP32
TOPIC = b"casa/rostro/estado"    # topic al que se SUSCRIBE (lo publica la laptop)
# PROVISIONAL: confirmar con el otro equipo
TOPIC_PUBLICAR = ("casa/" + ID_DISPOSITIVO + "/puerta").encode()
# Client ID unico: dispositivo + parte de la MAC, evita choques entre ESP32
CLIENT_ID = (ID_DISPOSITIVO + "_" + ubinascii.hexlify(unique_id()).decode()[-4:]).encode()

# ---- PINES ----
PIN_SERVO = 18
PIN_LED_VERDE = 33
PIN_LED_ROJO = 27
PIN_BUZZER = 25

# ---- ANGULOS ----
ANGULO_CERRADA = 0
ANGULO_ABIERTA = 90
# ===========================

servo = PWM(Pin(PIN_SERVO), freq=50)
led_verde = Pin(PIN_LED_VERDE, Pin.OUT)
led_rojo = Pin(PIN_LED_ROJO, Pin.OUT)
buzzer = Pin(PIN_BUZZER, Pin.OUT)


def mover(angulo):
    angulo = max(0, min(180, angulo))
    pulso_us = 500 + (angulo / 180) * 2000
    servo.duty_u16(int(pulso_us / 20000 * 65535))

def apagar_todo():
    led_verde.value(0)
    led_rojo.value(0)
    buzzer.value(0)


def acceso_valido():
    apagar_todo()
    led_verde.value(1)
    mover(ANGULO_ABIERTA)
    time.sleep(5)            # puerta abierta 5 s
    mover(ANGULO_CERRADA)
    time.sleep(1)
    apagar_todo()


def acceso_denegado():
    apagar_todo()
    mover(ANGULO_CERRADA)
    led_rojo.value(1)
    for _ in range(5):       # alarma: 5 pitidos
        buzzer.value(1)
        time.sleep(0.3)
        buzzer.value(0)
        time.sleep(0.3)
    time.sleep(1)
    apagar_todo()


# ---- WIFI ----
wlan = network.WLAN(network.STA_IF)


def conectar_wifi():
    wlan.active(True)
    try:
        wlan.config(pm=network.WLAN.PM_NONE)   # sin ahorro de energia: conexion mas estable
    except Exception:
        pass
    while not wlan.isconnected():
        print("Conectando a WiFi:", WIFI_SSID)
        wlan.disconnect()
        wlan.connect(WIFI_SSID, WIFI_PASS)
        t0 = time.time()
        while not wlan.isconnected() and time.time() - t0 < 20:
            time.sleep(0.5)
            print(".", end="")
        if not wlan.isconnected():
            print("\nNo se pudo conectar. status =", wlan.status())
            print("Redes visibles (ssid, canal, RSSI):")
            try:
                for r in wlan.scan():
                    print("  ", r[0], r[2], r[3])
            except OSError as e:
                print("  fallo el escaneo:", e)
            time.sleep(3)
    ip, mascara, gateway, dns = wlan.ifconfig()
    print("\nWiFi OK -> IP:", ip, "| mascara:", mascara, "| gateway:", gateway)


def probar_tcp(ip, puerto, timeout=5):
    """Prueba el puerto del broker con timeout. Devuelve True si responde."""
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((ip, puerto))
        return True
    except OSError as e:
        # 116 = timeout (firewall/aislamiento), 111/104 = broker no escucha ahi
        print("TCP falla hacia %s:%d -> %s" % (ip, puerto, e))
        return False
    finally:
        s.close()


# ---- MQTT ----
pendiente = None   # el callback solo guarda el mensaje; la accion corre en el bucle principal


def al_mensaje(topic, msg):
    global pendiente
    texto = msg.decode().strip()
    print(topic.decode(), "=", texto)
    if texto in ("conocido", "desconocido"):
        pendiente = texto
    else:
        print("Payload no reconocido")


def conectar_mqtt():
    # 1) Verificar primero que el puerto del broker sea alcanzable (con timeout)
    if not probar_tcp(MQTT_IP, BROKER_PORT):
        raise OSError("Broker inalcanzable en %s:%d" % (MQTT_IP, BROKER_PORT))
    # 2) Conectar MQTT
    cliente = MQTTClient(CLIENT_ID, MQTT_IP, port=BROKER_PORT,
                         user=MQTT_USER, password=MQTT_PASS, keepalive=60)
    cliente.set_callback(al_mensaje)
    cliente.connect()
    cliente.subscribe(TOPIC)
    print("MQTT OK, client_id =", CLIENT_ID.decode(), "| suscrito a", TOPIC.decode())
    return cliente


# ---- INICIO ----
print("Iniciando puerta inteligente...")
mover(ANGULO_CERRADA)
apagar_todo()
time.sleep(1)

conectar_wifi()
cliente = None
ultimo_ping = time.time()

while True:
    try:
        if not wlan.isconnected():
            print("WiFi caido, reconectando...")
            cliente = None
            conectar_wifi()

        if cliente is None:
            cliente = conectar_mqtt()
            ultimo_ping = time.time()

        cliente.check_msg()

        if time.time() - ultimo_ping > 30:
            cliente.ping()
            ultimo_ping = time.time()

        if pendiente is not None:
            accion = pendiente
            pendiente = None
            cliente.publish(TOPIC_PUBLICAR, accion.encode(), qos=0)
            print("Publicado", TOPIC_PUBLICAR.decode(), "=", accion)
            if accion == "conocido":
                print("Rostro valido")
                acceso_valido()
            else:
                print("Rostro desconocido")
                acceso_denegado()

        time.sleep(0.05)

    except MQTTException as e:
        # Codigos CONNACK: 1=version, 2=client id rechazado, 3=broker no disponible,
        # 4=usuario/clave malos, 5=no autorizado
        print("Error MQTT (broker rechazo la conexion), codigo:", e)
        cliente = None
        time.sleep(3)

    except OSError as e:
        print("Error de red/MQTT:", e)
        cliente = None
        time.sleep(3)

    except Exception as e:
        print("Error inesperado:", repr(e))
        cliente = None
        time.sleep(3)