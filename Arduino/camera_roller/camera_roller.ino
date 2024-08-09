/* 
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/esp8266-nodemcu-web-server-websocket-sliders/
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.
  
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
*/

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "LittleFS.h"
#include <Arduino_JSON.h>

// Replace with your network credentials
const char* ssid = "esp8266_ap";
const char* password = "esp8266_ap";

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);
// Create a WebSocket object

AsyncWebSocket ws("/ws");
// Set LED GPIO
const int ledPin0 = 16;
const int ledPin1 = 14;
const int ledPin2 = 12;
const int ledPin3 = 13;

String message = "";
String sliderValue1 = "0";
//String sliderValue2 = "0";
//String sliderValue3 = "0";

int dutyCycle1;
//int dutyCycle2;
//int dutyCycle3;

//Json Variable to Hold Slider Values
JSONVar sliderValues;

//Get Slider Values
String getSliderValues(){
  sliderValues["sliderValue1"] = String(sliderValue1);
//  sliderValues["sliderValue2"] = String(sliderValue2);
//  sliderValues["sliderValue3"] = String(sliderValue3);

  String jsonString = JSON.stringify(sliderValues);
  return jsonString;
}

// Initialize LittleFS
void initFS() {
  if (!LittleFS.begin()) {
    Serial.println("An error has occurred while mounting LittleFS");
  }
  else{
   Serial.println("LittleFS mounted successfully");
  }
}

// Initialize WiFi
void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi ..");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(1000);
  }
  Serial.println(WiFi.localIP());
}

void notifyClients(String sliderValues) {
  ws.textAll(sliderValues);
}

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    data[len] = 0;
    message = (char*)data;
    Serial.println(message);
    if (message.indexOf("1s") >= 0) {
      sliderValue1 = message.substring(2);
      dutyCycle1 = map(sliderValue1.toInt(), 0, 100, 0, 255);
      Serial.println(dutyCycle1);
      Serial.println(getSliderValues());
      notifyClients(getSliderValues());
    }
    if (message.indexOf("left") >= 0 && message.indexOf("ON") >= 0) {
      Serial.println("left on");
      digitalWrite(ledPin2, HIGH);
    }
    if (message.indexOf("right") >= 0 && message.indexOf("ON") >= 0) {
      Serial.println("right on");
      digitalWrite(ledPin3, HIGH);
    }
    if (message.indexOf("left") >= 0 && message.indexOf("OFF") >= 0) {
      Serial.println("left off");
      digitalWrite(ledPin2, LOW);
    }
    if (message.indexOf("right") >= 0 && message.indexOf("OFF") >= 0) {
      Serial.println("right off");
      digitalWrite(ledPin3, LOW);
    }
    if (message.indexOf("forward") >= 0 && message.indexOf("ON") >= 0) {
      Serial.print("forward: ");
      Serial.println(dutyCycle1);
      analogWrite(ledPin1, dutyCycle1);
//      digitalWrite(ledPin3, LOW);
    }
    if (message.indexOf("forward") >= 0 && message.indexOf("OFF") >= 0) {
      Serial.print("forward: ");
      Serial.println(dutyCycle1);
//      analogWrite(ledPin1, dutyCycle1);
      digitalWrite(ledPin1, LOW);
    }
    if (message.indexOf("backward") >= 0 && message.indexOf("ON") >= 0) {
      Serial.print("backward: ");
      Serial.println(dutyCycle1);
      analogWrite(ledPin0, dutyCycle1);
//      digitalWrite(ledPin3, LOW);
    }
    if (message.indexOf("backward") >= 0 && message.indexOf("OFF") >= 0) {
      Serial.print("backward: ");
      Serial.println(dutyCycle1);
//      analogWrite(ledPin1, dutyCycle1);
      digitalWrite(ledPin0, LOW);
    }
//    if (message.indexOf("2s") >= 0) {
//      sliderValue2 = message.substring(2);
//      dutyCycle2 = map(sliderValue2.toInt(), 0, 100, 0, 1023);
//      Serial.println(dutyCycle2);
//      Serial.print(getSliderValues());
//      notifyClients(getSliderValues());
//    }    
//    if (message.indexOf("3s") >= 0) {
//      sliderValue3 = message.substring(2);
//      dutyCycle3 = map(sliderValue3.toInt(), 0, 100, 0, 1023);
//      Serial.println(dutyCycle3);
//      Serial.print(getSliderValues());
//      notifyClients(getSliderValues());
//    }
    if (strcmp((char*)data, "getValues") == 0) {
      notifyClients(getSliderValues());
    }
  }
}
void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

void initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin0, OUTPUT);
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
  initFS();
  initWiFi();

  initWebSocket();
  
  // Web Server Root URL
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(LittleFS, "/index.html", "text/html");
  });
  
  server.serveStatic("/", LittleFS, "/");

  // Start server
  server.begin();
}

void loop() {
  
//  analogWrite(ledPin2, dutyCycle2);
//  analogWrite(ledPin3, dutyCycle3);

  ws.cleanupClients();
}
