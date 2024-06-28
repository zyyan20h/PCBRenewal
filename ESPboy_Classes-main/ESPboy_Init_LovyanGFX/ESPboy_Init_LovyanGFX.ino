#include "lib/ESPboyInit.h"
#include "lib/ESPboyInit.cpp"

ESPboyInit myESPboy;

void setup(){
  myESPboy.begin("ESPboy Init");
}


void loop(){
  static uint32_t timeCount;
  
   myESPboy.tft.drawString("Testing ESPboy Init", 0, random(120));
   
   timeCount = millis();
   while (millis()-timeCount < 1000){
     delay(100);
     if (myESPboy.getKeys()) {
       myESPboy.playTone(100,100);
       break;}
     }
     
   myESPboy.tft.fillScreen(TFT_BLACK);
}
