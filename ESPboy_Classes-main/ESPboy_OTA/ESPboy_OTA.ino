/*
ESPboyOTA class -- ESPboy App Store client core v0.13
for www.ESPboy.com project
https://hackaday.io/project/164830-espboy-games-iot-stem-for-education-fun
thanks to DmitryL (Plague) for coding help,
Corax, AlRado, Torabora, MLXXXP for tests and advices.


ESPboy OTA keys:
1. Keep pressed A or B during reset to connect ESPboy App Store
  - A for attemp to connect last known WiFi
  - B to scan available WiFi's
2. There are two modes in OTA: keyboard and console
3. To switch modes use RGT+LGT or A+B
4. In keyboard mode
  - LEFT+UP - switch on caps lock
  - RGT or LFT scroll console window up/down
  - UP/DOWN/LEFT/RIGHT to chose char
  - short press A - enter char to typing string
  - long press A - finish entering, finish typing
  - short press B - delete last char in typing string
  - long press B - delete typing string
5. In console mode
  - UP/DOWN, RGT/LFT, LEFT/RIGHT - scroll console window
  - B - switch to keyboard mode

Check "ESPboyGUI.h" for defines:
  - #define U8g2 - if defined then using font 4x6, if commented using font 6x8
  - #define buttonclicks - if defined - button are clicking but it takes more than 1kb RAM, if commented - no clicks and more free RAM

 2Do
 - add Type menu
 - add Genre menu
*/


#include <ESP8266httpUpdate.h>
#include "lib/ESPboyOTA.h"
#include "lib/ESPboyOTA.cpp"
#include "lib/ESPboyInit.h"
#include "lib/ESPboyInit.cpp"
#include "lib/ESPboyTerminalGUI.h"
#include "lib/ESPboyTerminalGUI.cpp"

ESPboyInit myESPboy;
ESPboyTerminalGUI *terminalGUIobj = NULL;
ESPboyOTA *OTAobj = NULL;


void setup() {
 
  // Init ESPboy
  myESPboy.begin("AppStore (OTA)");
  
  //Check OTA
  if (myESPboy.getKeys()&PAD_ACT || myESPboy.getKeys()&PAD_ESC) { 
     terminalGUIobj = new ESPboyTerminalGUI(&myESPboy.tft, &myESPboy.mcp);
     OTAobj = new ESPboyOTA(terminalGUIobj);
  }
}

void loop() {
    myESPboy.tft.fillScreen(TFT_BLACK);
    myESPboy.tft.setTextColor(TFT_MAGENTA, TFT_BLACK);
    myESPboy.tft.setCursor(0, random(70));
    myESPboy.tft.print("Keep A or B pressed\nduring reset to start\nESPboy App store\n\nA-connect last WiFi\nB-scan networks");
    while (!myESPboy.getKeys()) delay(200);
    myESPboy.playTone(100, 100);
    delay(200);
}
