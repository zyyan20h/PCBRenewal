/*
ESPboy LED class
for www.ESPboy.com project by RomanS
*/


#include "ESPboyLED.h"
#include <Adafruit_MCP23017.h>

#define MCP23017address 0 // actually it's 0x20 but in <Adafruit_MCP23017.h> lib there is (x|0x20) :)

ESPboyLED myled;
Adafruit_MCP23017 mcp;

void setup(){
  Serial.begin(115200);
  mcp.begin(MCP23017address);
  myled.begin(&mcp);
  delay (1000);
}


void loop(){
  for (uint8_t j=0; j<3; j++){
    for (uint8_t i=0; i<100; i++){
      switch (j){
        case 0:
          myled.setRGB (i,0,0);
          break; 
        case 1:
          myled.setRGB (0,i,0);
          break;
        case 2:
          myled.setRGB (0,0,i);
          break;
      }
      delay(10);
    }
  }
myled.setRGB(0, 0, 0);
delay (2000);
}
