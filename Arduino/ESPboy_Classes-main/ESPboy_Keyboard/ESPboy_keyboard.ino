/*
ESPboy keyboard module class
for www.ESPboy.com project by RomanS
thanks to Plague for help with coding
*/

#include "ESPboy_keyboard.h"

keyboardModule keybModule(1,1,7000); //  keybModule([key sound on/off], [backlit on/off], [autoBacklitOff time in milliseconds or 0=OFF autoBacklitOff])

void setup(){
  Serial.begin(115200);
  if (keybModule.begin() == 0){  
    Serial.println(F("\nESPboy keyboard module NOT found!"));
    while (true) delay(100);}
}


void loop(){
  if (keybModule.getPressedKey()){
      Serial.println((char)keybModule.getLastPressedKey());
      while (keybModule.keysUnpressed());}
}
