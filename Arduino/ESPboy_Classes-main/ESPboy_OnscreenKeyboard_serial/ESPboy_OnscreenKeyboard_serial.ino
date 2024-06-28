#include "ESPboy_OnscreenKeyboard_serial.h"

OnscrKeyb OSK(20,0,0);


char readKey(){
  if (Serial.available()) 
    return Serial.read();
  else return 0;
}


void waitKeyUnpressed(){
  Serial.read();
  Serial.read();
}


uint8_t checkButtons(char readKeyCommand){
  switch (readKeyCommand){
    case 'w':
      return (OSK.keybCommand (OSK.keybUp));
      break;
    case 'x':
      return (OSK.keybCommand (OSK.keybDown));
      break;
    case 'a':
      return (OSK.keybCommand (OSK.keybLeft));
      break;
    case 'd':
      return (OSK.keybCommand (OSK.keybRight));
      break;
    case 's':
      return (OSK.keybCommand (OSK.keybSelect));
      break;
    case 'q':
      return (OSK.keybCommand (OSK.keybDel));
      break;  
    case 'e':
      return (OSK.keybCommand (OSK.keybLayout));
      break;  
    case ' ':
      return (OSK.keybCommand (OSK.keybSpace));
      break;  
    case 'z':
      return (OSK.keybCommand (OSK.keybOk));
      break;  
  }
    return (OSK.keybComUnknown);
}


void setup(){
  Serial.begin(115200);
  Serial.println(); Serial.println(); Serial.println();
  OSK.drawAll();
}


void loop(){
 static char rdKey;
  rdKey = readKey();
  if (rdKey){
    Serial.println(); Serial.println(); Serial.println();
    Serial.print("Command:"); 
    Serial.println(rdKey);
    
    switch (checkButtons(rdKey)){
      case OSK.keybComUnknown:
        Serial.println("Command unknown");
        break;
      case OSK.keybComDone:
        Serial.println("Command done");
        break;
      case OSK.keybFinished:
        Serial.println(); Serial.println(); Serial.println();
        Serial.print("FINISHED! Typing: "); 
        Serial.println(OSK.getTyping());
        break; 
      }
    waitKeyUnpressed();
    OSK.drawAll();
  }
  delay(200);
}
