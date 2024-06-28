#include "lib/ESPboyInit.h"
#include "lib/ESPboyInit.cpp"

ESPboyInit myESPboy;
ESPboyMenuGUI menuGUI(&myESPboy);

const char *menulist1[] PROGMEM = {
  "Item one",
  "-Item two",  //if first symbol "-" then this line can't be selected in menu
  "Item three",
  "Item four",
  "Item five",
  "Item six",
  "Item seven",
  "Item eight",
  "Item nine",
  "Item ten",
  "-Item eleven",
  "Item 12",
  "Item 13",
  "Item 14",
  "Item 15",
  "-Item 16",
  "Item 17",
  "Item 18",
  "Item 19",
  "Item 20",
  "Item 21",
  NULL, // the last element of every menu list should be NULL
};


void setup(){
  myESPboy.begin("First test");
}


void loop(){
 uint16_t menuItem;
   menuItem = menuGUI.menuInit(menulist1, TFT_YELLOW, TFT_BLUE, TFT_BLUE);  
   myESPboy.tft.setTextColor(TFT_GREEN);
   myESPboy.tft.drawString("Menu No:", 42, 55);
   myESPboy.tft.drawString((String)(menuItem), 62, 68);
   delay(1000);
}
