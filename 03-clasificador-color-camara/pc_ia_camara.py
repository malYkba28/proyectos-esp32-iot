import cv2
import serial
import time
import numpy as np

PUERTO = "COM3"      
BAUDIOS = 115200
UMBRAL = 0.15        

ser = serial.Serial(PUERTO, BAUDIOS, timeout=1)
time.sleep(2)

cap = cv2.VideoCapture(0)
ultimo = None

while True:
    ok, frame = cap.read()
    if not ok:
        break

    h, w = frame.shape[:2]
    y1, y2, x1, x2 = h // 3, 2 * h // 3, w // 3, 2 * w // 3
    roi = frame[y1:y2, x1:x2]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    verde = cv2.inRange(hsv, (40, 80, 50), (85, 255, 255))
    rojo = cv2.inRange(hsv, (0, 120, 70), (10, 255, 255)) | \
           cv2.inRange(hsv, (170, 120, 70), (180, 255, 255))

    total = roi.shape[0] * roi.shape[1]
    p_verde = np.count_nonzero(verde) / total
    p_rojo = np.count_nonzero(rojo) / total

    mensaje = None
    if p_verde > UMBRAL and p_verde > p_rojo:
        mensaje = "CLASS:OK"
    elif p_rojo > UMBRAL and p_rojo > p_verde:
        mensaje = "CLASS:DEFECT"

    if mensaje and mensaje != ultimo:
        ser.write((mensaje + "\n").encode())
        print("Enviado:", mensaje)
        ultimo = mensaje

    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
    cv2.putText(frame, str(mensaje), (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imshow("IA externa", frame)

    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('i'):              
        ser.write(b"CLASS:XYZ\n")
        print("Enviado: CLASS:XYZ (inválido)")
    elif tecla == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()