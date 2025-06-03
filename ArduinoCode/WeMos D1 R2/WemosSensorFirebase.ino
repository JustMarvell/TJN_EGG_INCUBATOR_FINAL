// wemos_d1_firebase_sensor_control.ino
#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>
#include <DHT22.h>

// Wi-Fi Credentials
const char* ssid = "VellsSpot";
const char* password = "876543210";

// Firebase Config
#define FIREBASE_HOST "egg-incubator-iot-discord-default-rtdb.asia-southeast1.firebasedatabase.app"
#define FIREBASE_AUTH "T8BkXTlVRYxFxCApirU9z6Pd7Gu4QVLLrv09KBQD"

FirebaseData fbdo;
FirebaseData stream_fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// DHT22 Config
#define DHT_PIN D5
DHT22 dht22(DHT_PIN);

// Relay Config
#define RELAY_PIN D6

// Pending command buffer
String pendingCommand = "";

void connectWiFi() {
  Serial.print("Connecting to Wi-Fi");
  WiFi.begin(ssid, password);
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retries++;
    if (retries > 40) {
      Serial.print("\nWiFi status code: ");
      Serial.println(WiFi.status());  // debug info
      Serial.println("Wi-Fi connection failed. Retrying...");
      WiFi.disconnect();
      delay(2000);
      WiFi.begin(ssid, password);
      retries = 0;
    }
  }
  Serial.println("\nWi-Fi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void connectFirebase() {
  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  Serial.println("Connecting to Firebase...");

  int retries = 0;
  while (!Firebase.ready()) {
    delay(500);
    Serial.print(".");
    retries++;
    if (retries > 40) {
      Serial.println("\nFirebase connection failed. Retrying...");
      delay(2000);
      Firebase.begin(&config, &auth);
      retries = 0;
    }
  }
  Firebase.setBool(fbdo, "/device_status/online", true);
  Serial.println("\nFirebase connected");
}

void ToggleLamp(bool state) {
  Firebase.setString(fbdo, "/device_responses/lamp/status", "waiting");
  digitalWrite(RELAY_PIN, state);
  Firebase.setBool(fbdo, "/device_responses/lamp/state", state);
  const char* msg = state ? "Lamp state ON" : "Lamp state OFF";
  Firebase.setString(fbdo, "/device_message/lamp/status", msg);
  Firebase.setString(fbdo, "/device_responses/lamp/status", "done");
  Serial.println(msg);
}

void ReadTemperature() {
  Firebase.setString(fbdo, "/device_responses/dht/status", "waiting");
  float temp = dht22.getTemperature();
  
  if (isnan(temp)) {
    Firebase.setString(fbdo, "/device_message/dht/status", "Temperature read NAN. Using previous value");
  } else {
    Firebase.setFloat(fbdo, "/device_responses/dht/temperature", temp);
    Firebase.setString(fbdo, "/device_message/dht/status", "Temperature Reading Success");
  }
  Firebase.setString(fbdo, "/device_responses/dht/status", "done");
}

void ReadHumidity() {
  Firebase.setString(fbdo, "/device_responses/dht/status", "waiting");
  float hum = dht22.getHumidity();
  
  if (isnan(hum)) {
    Firebase.setString(fbdo, "/device_message/dht/status", "Humidity read NAN. Using previous value");
  } else {
    Firebase.setFloat(fbdo, "/device_responses/dht/humidity", hum);
    Firebase.setString(fbdo, "/device_message/dht/status", "Humidity Reading Success");
  }
  Firebase.setString(fbdo, "/device_responses/dht/status", "done");
}

// Handle Firebase Commands
void streamCallback(StreamData data) {
 Serial.printf("Firebase : Stream path %s\n", data.streamPath().c_str());
  if (data.dataType() == "string") {
    pendingCommand = data.stringData();
    Firebase.setString(fbdo, "/device_commands/command", "idle");
  }
}

void streamTimeoutCallback(bool timeout) {
  if (timeout) {
    Firebase.setBool(fbdo, "/device_status/online", false);
    Firebase.setString(fbdo, "/device_message/firebase/status", "Stream callback timeout! Trying to reconnect");
    Serial.println("Stream timeout, resuming...");
    delay(100);
    Firebase.beginStream(stream_fbdo, "/device_commands/command");
    Firebase.setString(fbdo, "/device_message/firebase/status", "Stream reconnected");
    Firebase.setString(fbdo, "/device_message/firebase/firebase_error_message", "none");
    Firebase.setBool(fbdo, "/device_status/online", true);
  }
}

void setup() {
  Serial.begin(115200);
  connectWiFi();
  connectFirebase();
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);
  Firebase.setBool(fbdo, "/device_responses/lamp/state", true);
  Firebase.setStreamCallback(stream_fbdo, streamCallback, streamTimeoutCallback);
  if (!Firebase.beginStream(stream_fbdo, "/device_commands/command")) {
    Serial.printf("Stream error: %s\n", fbdo.errorReason().c_str());
  }
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    connectWiFi();
  }
  if (!Firebase.ready()) {
    Serial.println("Firebase not ready. Reconnecting...");
    connectFirebase();
  }
  if (pendingCommand.length() > 0) {
    if (pendingCommand == "read_temperature") {
      ReadTemperature();
    } else if (pendingCommand == "read_humidity") {
      ReadHumidity();
    } else if (pendingCommand == "lamp_on") {
      ToggleLamp(true);
    } else if (pendingCommand == "lamp_off") {
      ToggleLamp(false);
    }
    pendingCommand = "";
  }
  delay(2000);
}
