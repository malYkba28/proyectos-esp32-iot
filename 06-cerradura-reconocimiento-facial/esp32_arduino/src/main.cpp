#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// ====== CONFIGURACION ======
const char* WIFI_SSID = "NOMBRE_DE_LA_RED";
const char* WIFI_PASS = "CONTRASENA_DE_LA_RED";
const char* BROKER_IP = "192.168.1.50";   // IP de la laptop con Mosquitto
const int   BROKER_PORT = 1883;
const char* TOPIC_ROSTRO = "casa/rostro/estado";

const int LED_VERDE = 18;   // conocido
const int LED_ROJO  = 19;   // desconocido
// ===========================

WiFiClient wifi;
PubSubClient mqtt(wifi);

void alMensaje(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  msg.trim();

  Serial.print(topic);
  Serial.print(" = ");
  Serial.println(msg);

  if (msg == "conocido") {
    digitalWrite(LED_VERDE, HIGH);
    digitalWrite(LED_ROJO, LOW);
  } else if (msg == "desconocido") {
    digitalWrite(LED_VERDE, LOW);
    digitalWrite(LED_ROJO, HIGH);
  } else {
    Serial.println("Payload no reconocido");
  }
}

void conectarWifi() {
  Serial.print("Conectando a WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.print("\nWiFi OK, IP: ");
  Serial.println(WiFi.localIP());
}

void conectarMqtt() {
  while (!mqtt.connected()) {
    Serial.print("Conectando al broker...");
    if (mqtt.connect("esp32_rostro")) {
      Serial.println(" OK");
      mqtt.subscribe(TOPIC_ROSTRO);
    } else {
      Serial.print(" fallo, rc=");
      Serial.println(mqtt.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_ROJO, LOW);

  conectarWifi();
  mqtt.setServer(BROKER_IP, BROKER_PORT);
  mqtt.setCallback(alMensaje);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) conectarWifi();
  if (!mqtt.connected()) conectarMqtt();
  mqtt.loop();
}
