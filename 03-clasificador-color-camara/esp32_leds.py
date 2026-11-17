from machine import Pin

PIN_VERDE = 19
PIN_ROJO = 18

led_verde = Pin(PIN_VERDE, Pin.OUT)
led_rojo = Pin(PIN_ROJO, Pin.OUT)

led_verde.value(0)
led_rojo.value(0)

print("Sistema listo")
while True:
    mensaje = input("Mensaje [CLASS:OK / CLASS:DEFECT]: ")
    mensaje = mensaje.strip().upper()

    if mensaje == "":
        continue

    if mensaje == "CLASS:OK":
        led_verde.value(1)
        led_rojo.value(0)
        print("OK -> LED VERDE")

    elif mensaje == "CLASS:DEFECT":
        led_verde.value(0)
        led_rojo.value(1)
        print("DEFECT -> LED ROJO")

    else:
        print("ERROR: mensaje no reconocido")