#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "sai";
const char* password = "venkat7226";

// MQTT broker settings
const char* mqtt_server = "broker.hivemq.com"; // Public HiveMQ broker
const int mqtt_port = 1883; // Standard MQTT port
const char* mqtt_user = nullptr; // No username for public broker
const char* mqtt_pass = nullptr; // No password for public broker
const char* topic = "myhome/esp32/led"; // Must match backend topic

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  String command = "";
  for (unsigned int i = 0; i < length; i++) {
    command += (char)payload[i];
  }
  Serial.println(command);
  // Example: turn on/off LED based on command
  if (command == "on") {
    digitalWrite(2, HIGH); // Onboard LED
  } else if (command == "off") {
    digitalWrite(2, LOW);
  }
}

void reconnect() {
  // Loop until reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Use a unique client ID (add a random number)
    String clientId = "ESP32Client-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_pass)) {
      Serial.println("connected");
      client.subscribe(topic);
      Serial.print("Subscribed to topic: ");
      Serial.println(topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  pinMode(2, OUTPUT); // Onboard LED
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    Serial.println("MQTT not connected, calling reconnect()");
    reconnect();
  }
  client.loop();
  delay(100); // Add a small delay for stability
}
