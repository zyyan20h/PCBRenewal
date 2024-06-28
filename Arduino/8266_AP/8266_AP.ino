// Import required libraries
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <Hash.h>


const char* ssid     = "ESP8266-Access-Point";
const char* password = "123456789";

// Create AsyncWebServer object on port 80

void setup(){
  // Serial port for debugging purposes
  Serial.begin(115200);
  
  Serial.print("Setting AP (Access Point)…");
  // Remove the password parameter, if you want the AP (Access Point) to be open
  WiFi.softAP(ssid, password);

  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  // Print ESP8266 Local IP Address
  Serial.println(WiFi.localIP());

  // Start server
}
 
void loop(){  
  
}