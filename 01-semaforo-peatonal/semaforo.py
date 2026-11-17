from machine import Pin
from time import sleep_ms

PIN_ROJO = 23
PIN_VERDE = 21
PIN_PRECAUCION = 22
PIN_BOTON = 18

rojo = Pin(PIN_ROJO, Pin.OUT)
verde = Pin(PIN_VERDE, Pin.OUT)
precaucion = Pin(PIN_PRECAUCION, Pin.OUT)
boton = Pin(PIN_BOTON, Pin.IN, Pin.PULL_UP)

def parpadear_con_cuenta(led, segundos, etiqueta):
    # Cada segundo: 4 cambios de 250 ms (parpadeo) y un mensaje de cuenta regresiva
    for restante in range(segundos, 0, -1):
        print(etiqueta, restante)
        for _ in range(4):
            led.value(not led.value())
            sleep_ms(250)
    led.value(0)

def encender_con_cuenta(led, segundos, etiqueta):
    led.value(1)
    for restante in range(segundos, 0, -1):
        print(etiqueta, restante)
        sleep_ms(1000)
    led.value(0)

while True:
    # Reposo: rojo encendido
    rojo.value(1)
    verde.value(0)
    precaucion.value(0)
    print("ROJO: No se debe pasar todavia")
    print("Presiona el boton para pasar")

    # Esperar botón (presionado = 0 por el PULL_UP)
    while boton.value() == 1:
        sleep_ms(20)
    sleep_ms(50)  # antirrebote

    print("Has solicitado el cruce")

    # 1) Rojo se apaga y precaución parpadea 5 s
    rojo.value(0)
    parpadear_con_cuenta(precaucion, 5, "PRECAUCION, espera:")

    # 2) Verde 5 s
    print("VERDE: tienes 5 segundos para pasar")
    encender_con_cuenta(verde, 5, "Tiempo para pasar:")

    # 3) Precaución parpadea 5 s
    parpadear_con_cuenta(precaucion, 5, "PRECAUCION, el paso termina en:")
    # El ciclo reinicia: rojo encendido y mensaje de no pasar