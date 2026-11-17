from machine import Pin
led = Pin(18, Pin.OUT)
led.value(0)

print("Sistema listo")
while True:
    mensaje = input("Comando [ALERT/NORMAL]:")
    mensaje = mensaje.strip().upper()
    
    if mensaje == "ALERT":
        led.value(1)
        print("LED ON")
    
    elif mensaje == "NORMAL":
        led.value(0)
        print("LED OFF")
    
    else:
        print("ERROR: comando no reconocido")