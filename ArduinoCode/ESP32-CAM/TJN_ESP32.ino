#include <Arduino.h>
#include "esp_camera.h"
#include <WiFi.h>
#include <FirebaseESP32.h>
#include "Base64.h"
#include <DHT.h>
#include <cmath>

// WiFi Credentials
const char* ssid = "VellsSpot";
const char* password = "876543210";

// Firebase Config
#define FIREBASE_HOST "egg-incubator-iot-discord-default-rtdb.asia-southeast1.firebasedatabase.app";
#define FIREBASE_AUTH "T8BkXTlVRYxFxCApirU9z6Pd7Gu4QVLLrv09KBQD";

FirebaseData fbdo;
FirebaseData stream_fbdo;
FirebaseData part1_fbdo;
FirebaseData part2_fbdo;
FirebaseData part3_fbdo;
FirebaseData part4_fbdo;
FirebaseData part5_fbdo;
FirebaseData dht_fbdo;
FirebaseData lamp_fbdo;
FirebaseData msg_fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// DHT22 Config
#define DHTPIN 13
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// Relay Config (controls lamp)
#define RELAY_PIN 14

// Camera Config (ESP32-CAM with AI Thinker)
#define PWDN_GPIO_NUM  32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM  0
#define SIOD_GPIO_NUM  26
#define SIOC_GPIO_NUM  27
#define Y9_GPIO_NUM    35
#define Y8_GPIO_NUM    34
#define Y7_GPIO_NUM    39
#define Y6_GPIO_NUM    36
#define Y5_GPIO_NUM    21
#define Y4_GPIO_NUM    19
#define Y3_GPIO_NUM    18
#define Y2_GPIO_NUM    5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM  23
#define PCLK_GPIO_NUM  22

const size_t MAX_JPEG_SIZE = 500 * 1024; // 500KB

// ESP Flashlight pin
#define LED_BUILTIN 4

// Failsafe
int failCount = 0;
const int MAX_FAIL_COUNT = 5;

void SetupCamera(int jpeg_quality) {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = jpeg_quality;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QQVGA;
    config.jpeg_quality = jpeg_quality;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err == ESP_OK) {
    Firebase.setString(msg_fbdo, "/device_message/camera/status", "Camera Init Success");
    Firebase.setFloat(msg_fbdo, "/device_message/camera/timestamp", millis());
    Serial.println("Camera Init Success");
  } else {
    Firebase.setString(msg_fbdo, "/device_message/camera/status", "Camera Init Failed");
    Firebase.setFloat(msg_fbdo, "/device_message/camera/timestamp", millis());
    Serial.printf("camera : failed with error 0x%x\n", err);
  }
}

void ConnectWifi() {
  Serial.print("Connecting to Wi-Fi");
  WiFi.begin(ssid, password);
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retries++;
    if (retries > 40) {
      Serial.println("\nWi-Fi connection failed. Retrying...");
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

void ConnectFirebase() {
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
  Firebase.setBool(msg_fbdo, "/device_status/online", true);
  Serial.println("\nFirebase connected");
}

void SplitAndUploadBase64(const String& base64Str) {
  // Split to 5 parts
  size_t stringLength = base64Str.length();
  size_t partLength = stringLength / 5;

  String part1 = base64Str.substring(0, partLength);
  String part2 = base64Str.substring(partLength, 2 * partLength);
  String part3 = base64Str.substring(2 * partLength, 3 * partLength);
  String part4 = base64Str.substring(3 * partLength, 4 * partLength);
  String part5 = base64Str.substring(4 * partLength);

  // upload to Firebase
  Firebase.setString(part1_fbdo, "/device_responses/take_picture/part1", part1);
  Firebase.setString(part2_fbdo, "/device_responses/take_picture/part2", part2);
  Firebase.setString(part3_fbdo, "/device_responses/take_picture/part3", part3);
  Firebase.setString(part4_fbdo, "/device_responses/take_picture/part4", part4);
  Firebase.setString(part5_fbdo, "/device_responses/take_picture/part5", part5);

  // msg
  Serial.println("Firebase : Image Uploaded!");
  Firebase.setString(msg_fbdo, "/device_message/camera/status", "done");
  Firebase.setFloat(msg_fbdo, "/device_message/camera/timestamp", millis());
  Firebase.setString(fbdo, "/device_responses/take_picture/status", "done");
  Firebase.setFloat(fbdo, "/device_responses/take_picture/timestamp", millis());
}

void CaptureImage() {
  // msg
  Firebase.setString(fbdo, "/device_responses/take_picture/status", "waiting");
  Firebase.setFloat(fbdo, "/device_responses/take_picture/current_timestamp", millis());
  Firebase.setString(msg_fbdo, "/device_message/camera/status", "capturing image");
  Firebase.setFloat(msg_fbdo, "/device_message/camera/timestamp", millis());
  Serial.println("ESP : Taking picture...");

  // setup camera stuff
  int jpeg_quality = 10;
  camera_fb_t* fb = nullptr;

  // Flash LED
  digitalWrite(LED_BUILTIN, HIGH);

  // Flush stale frame & buffer
  for (int i = 0; i < 2; i++) {
    fb = esp_camera_fb_get();
    if (fb) esp_camera_fb_return(fb);
    delay(150); // give sensor time
  }

  // Take picture (quality <= 15)
  while (jpeg_quality <= 15) {
    digitalWrite(LED_BUILTIN, HIGH);
    fb = esp_camera_fb_get();

    // check stuff
    if (!fb) {
      digitalWrite(LED_BUILTIN, LOW);
      return;
    }

    // if less than max size then break (hehe)
    if (fb->len <= MAX_JPEG_SIZE) {
      Firebase.setString(msg_fbdo, "/device_message/camera/status", String("Image Captured"));
      Firebase.setFloat(msg_fbdo, "/device_message/camera/timestamp", millis());
      break;
    }

    // retry capturing with other quality
    esp_camera_fb_return(fb);
    digitalWrite(LED_BUILTIN, LOW);
    jpeg_quality += 2;
    esp_camera_deinit();
    SetupCamera(jpeg_quality);
  }

  // encode and upload
  String base64Str = base64::encode((uint8_t*)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  digitalWrite(LED_BUILTIN, LOW);
  SplitAndUploadBase64(base64Str);
}

// void ReadTemperature() {
//   Firebase.setString(fbdo, "/device_responses/dht/status", "waiting");
//   float temp = dht.readTemperature();

//   if (isnan(temp)) {
//     Firebase.setString(msg_fbdo, "/device_message/dht/status", "Temperature read NAN. Using previous value");
//   } else {
//     Firebase.setFloat(dht_fbdo, "/device_responses/dht/temperature", temp);
//     Firebase.setString(msg_fbdo, "/device_message/dht/status", "Temperature Reading Success");
//   }

//   Firebase.setString(fbdo, "/device_responses/dht/status", "done");
// }

// void ReadHumidity() {
//   Firebase.setString(fbdo, "/device_responses/dht/status", "waiting");
//   float hum = dht.readHumidity();

//   if (isnan(hum)) {
//     Firebase.setString(msg_fbdo, "/device_message/dht/status", "Humidity read NAN. Using previous value");
//   } else {
//     Firebase.setFloat(dht_fbdo, "/device_responses/dht/humidity", hum);
//     Firebase.setString(msg_fbdo, "/device_message/dht/status", "Humidity Reading Success");
//   }

//   Firebase.setString(fbdo, "/device_responses/dht/status", "done");
// }

// void ToggleLamp(bool state) {
//   Firebase.setString(fbdo, "/device_responses/lamp/status", "waiting");

//   digitalWrite(RELAY_PIN, state);
//   Firebase.setBool(lamp_fbdo, "/device_responses/lamp/state", state);
//   String msg = "Lamp state " + state ? "ON" : "OFF";
//   Firebase.setString(msg_fbdo, "/device_message/lamp/status", msg);

//   Firebase.setString(fbdo, "/device_responses/lamp/status", "done");
// }

void StreamTimeoutCallback(bool timeout) {
  if (timeout) {
    Firebase.setBool(fbdo, "/device_status/online", false);
    Firebase.setString(msg_fbdo, "/device_message/firebase/status", "Stream callback timeout! Trying to reconnect");
    Firebase.setBool(msg_fbdo, "/device_message/firebase/timestamp", millis());
    Serial.println("Stream timeout, resuming...");

    delay(100);

    Firebase.beginStream(stream_fbdo, "/device_commands/command");
    Firebase.setString(msg_fbdo, "/device_message/firebase/status", "Stream reconnected");
    Firebase.setBool(msg_fbdo, "/device_message/firebase/timestamp", millis());
    Serial.println("Stream resumed");
    Firebase.setString(msg_fbdo, "/device_message/firebase/firebase_error_message", "none");
    Firebase.setBool(fbdo, "/device_status/online", true);
  }
}

void StreamCallback(StreamData data) {
  Serial.printf("Firebase : Stream path %s\n", data.streamPath().c_str());

  if (data.dataType() == "string") {
    String cmd = data.stringData();

    if (cmd == "take_picture") {
      CaptureImage();
    }
    // } else if (cmd == "read_temperature") {
    //   ReadTemperature();
    // } else if (cmd == "read_humidity") {
    //   ReadHumidity();
    // } else if (cmd == "lamp_on") {
    //   ToggleLamp(true);
    // } else if (cmd == "lamp_off") {
    //   ToggleLamp(false);
    // }

    Firebase.setString(fbdo, "/device_commands/command", "idle");
  }
}

void setup() {
  // setup serial monitor
  Serial.begin(115200);

  // setup connections
  ConnectWifi();
  ConnectFirebase();
  delay(1000);        // delay for stability
  Firebase.setStreamCallback(stream_fbdo, StreamCallback, StreamTimeoutCallback);
  if (!Firebase.beginStream(stream_fbdo, "/device_commands/command")) {
    String errMsg = stream_fbdo.errorReason().c_str();
    Firebase.setString(msg_fbdo, "/device_message/firebase/firebase_error_message", errMsg);
  } else {
    Firebase.setString(msg_fbdo, "/device_message/firebase/firebase_error_message", "none");
  }
  
  // setup pin, sensor, and lamp
  // pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  // digitalWrite(RELAY_PIN, HIGH);
  // Firebase.setBool(lamp_fbdo, "/device_responses/lamp/state", true);
  // dht.begin();
  SetupCamera(10);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    ConnectWifi();
  }
  delay(1000);
}