#include "lib/ESPboyInit.h"
#include "lib/ESPboyInit.cpp"
#include "ESPboyTerminalGUI.h"

ESPboyInit myESPboy;
ESPboyTerminalGUI terminalGUI(&myESPboy.tft, &myESPboy.mcp);


void setup(){
  myESPboy.begin("ESPboy Terminal GUI");
  terminalGUI.printConsole("Testing terminal GUI", TFT_MAGENTA, 1, 0);
}


void loop(){
 
  terminalGUI.printConsole("Testing scroll", TFT_YELLOW, 1, 0);
  delay(2000);
  for (uint8_t i=50; i>0; i--){
    String toPrint = (String) i + " ";
    toPrint += "to start";
    if (i>10) terminalGUI.printConsole(toPrint, TFT_WHITE, 1, 0); 
    else terminalGUI.printConsole(toPrint, TFT_RED, 1, 0);
    delay(10);  
  }
  
  terminalGUI.getUserInput();

  terminalGUI.printConsole("Testing one line", TFT_YELLOW, 1, 0);
  delay(2000);
  for (uint8_t i=100; i>0; i--){
    String toPrint = (String) i + "%";
    if (i>10) terminalGUI.printConsole(toPrint, TFT_WHITE, 1, 1); 
    else terminalGUI.printConsole(toPrint, TFT_RED, 1, 1);
    delay(10);  
  }
  
  terminalGUI.getUserInput();

  terminalGUI.printConsole("Testing info", TFT_YELLOW, 1, 0);
  delay(2000);
  terminalGUI.drawOwnTypingLine(F("Testing print..."), TFT_GREEN);
  delay(2000);
  terminalGUI.drawOwnTypingLine("", TFT_BLACK);

  terminalGUI.getUserInput();
}
