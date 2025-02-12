#include <Arduino.h>

#ifndef ESPboy_OnscreenKeyboard
#define ESPboy_OnscreenKeyboard

#define maxTypingSymbols 42
#define keybLines         5 //counting from 1
#define keybMaxCharsInLine 16
#define keybLayouts       2 //counting from 1
#define keybSpecLine      4 //meaning the line "ABC Space Del OK" counting 0 as the first line
#define keybSpecAbcCol    0
#define keybSpecSpaceCol  4
#define keybSpecDelCol    10
#define keybSpecOkCol     14


class OnscrKeyb{
private:
  enum keybLayout {keybLayoutLower = 0, keybLayoutCaps};

  uint16_t keybCharsColor;
  uint16_t keybSelectColor;
	uint8_t keybMaxTyping;
  
	uint8_t currentKeybLayout;
	uint8_t currentRow, currentCol;
	
	char typing[maxTypingSymbols+1], typingStore[maxTypingSymbols+1];
  char strbuff[keybMaxCharsInLine + 1];

	void drawKeyb ();
	void drawSelectedKey();
	void drawTyping();
	void addTyping(char typingchar);
	void delTyping();
	void changeKeybLayout();

public: 
  OnscrKeyb(uint8_t keybTypingLength, uint16_t keybCharsCol, uint16_t keybSelectCol);
  
  enum keybErrors {keybComUnknown = 0, keybComDone, keybFinished};
  enum keybCommands {keybUp = 0, keybDown, keybLeft, keybRight, keybSelect, keybDel, keybLayout, keybSpace, keybOk};

	void drawAll();
	uint8_t keybCommand (uint8_t keybCommand);
	char *getTyping ();
}; 

#endif
