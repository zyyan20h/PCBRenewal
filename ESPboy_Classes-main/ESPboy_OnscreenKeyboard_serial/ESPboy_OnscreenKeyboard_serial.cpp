#include "ESPboy_OnscreenKeyboard_serial.h"

constexpr char onscreenKeyb [keybLayouts][keybLines][keybMaxCharsInLine + 1] PROGMEM = {
  {"1234567890_=", "qwertyuiop+-", "asdfghjkl?*/", "<>zxcvbnm.,:", "ABC Space Del OK"},
  {"@#$%&()^�~_=", "QWERTYUIOP+-", "ASDFGHJKL!*/", "[]ZXCVBNM.,;", "abc Space Del OK"}
};


OnscrKeyb::OnscrKeyb (uint8_t keybTypingLength, uint16_t keybCharsCol, uint16_t keybSelectCol){
  keybMaxTyping = keybTypingLength;
  if (keybMaxTyping > maxTypingSymbols) keybMaxTyping = maxTypingSymbols;
  keybCharsColor = keybCharsCol;
  keybSelectColor = keybSelectCol;
  
  typing[0] = 0;
  currentKeybLayout = keybLayoutLower;
  currentRow = 0;
  currentCol = 0;
}


void OnscrKeyb::drawKeyb (){
  Serial.println();
  for (int i = 0; i < keybLines; i++){
      strcpy_P(&strbuff[0], (char*)&(onscreenKeyb[currentKeybLayout][i]));
    Serial.println(strbuff);
  }
  Serial.println();
}


void OnscrKeyb::drawSelectedKey(){
  Serial.print("Selected char: ");
  if (currentRow != keybSpecLine)
    Serial.println((char)pgm_read_byte(&onscreenKeyb[currentKeybLayout][currentRow][currentCol]));
  else{
    switch (currentCol){
      case keybSpecAbcCol:
        if (currentKeybLayout == keybLayoutLower) Serial.println("ABC");
        else Serial.println("abc");
        break;
      case keybSpecSpaceCol:
        Serial.println("Space");
        break;
      case keybSpecDelCol:
        Serial.println("Del");
        break;
      case keybSpecOkCol:
        Serial.println("OK");
        break;
    }
  }
}


void OnscrKeyb::drawTyping(){
  Serial.print("Typing: ");
  Serial.print(typing);
  if (strlen(typing) < keybMaxTyping) Serial.println("_");
}


void OnscrKeyb::addTyping(char typingchar){
  if (strlen(typing) < keybMaxTyping){
     typing[strlen(typing)+1] = 0;
     typing[strlen(typing)] = typingchar;
  }
}

	
void OnscrKeyb::delTyping(){
  if (strlen(typing) > 0 ) 
    typing[strlen(typing) - 1] = 0;
}


void OnscrKeyb::changeKeybLayout(){
  currentKeybLayout =! currentKeybLayout;
}


void OnscrKeyb::drawAll(){
  drawKeyb ();
  drawSelectedKey();
  drawTyping();
}


uint8_t OnscrKeyb::keybCommand (uint8_t keybCommand){
  switch (keybCommand){
    case keybLeft:
      if (currentRow != keybSpecLine){ 
        if (currentCol > 0) currentCol--;
      }
      else{
        if (currentCol == keybSpecSpaceCol) currentCol = keybSpecAbcCol;
        if (currentCol == keybSpecDelCol) currentCol = keybSpecSpaceCol;
        if (currentCol == keybSpecOkCol) currentCol = keybSpecDelCol;
      }
      return (keybComDone);
      break;
    case keybRight:
      if (currentRow != keybSpecLine){
        if (currentCol < strlen_P((char *)&onscreenKeyb[currentKeybLayout][currentRow]) - 1) {
          currentCol++;}
      } 
      else{ 
        switch (currentCol){
          case keybSpecAbcCol:
            currentCol = keybSpecSpaceCol;
            break;
          case keybSpecSpaceCol:
            currentCol = keybSpecDelCol;
            break;
          case keybSpecDelCol:
            currentCol = keybSpecOkCol;
            break;
          }
      }
      return (keybComDone);
      break;
    case keybUp:
      if (currentRow > 0){
        currentRow--;
        if (currentCol > strlen_P((char *)&onscreenKeyb[currentKeybLayout][currentRow]))
          currentCol = strlen_P((char *)&onscreenKeyb[currentKeybLayout][currentRow]) - 1;
      }
      return (keybComDone);
      break;
    case keybDown:
      if (currentRow < keybLines-1){
        currentRow++;
        if (currentCol > strlen_P((char *)&onscreenKeyb[currentKeybLayout][currentRow]))
          currentCol = strlen_P((char *)&onscreenKeyb[currentKeybLayout][currentRow]) - 1;
        if (currentRow == keybSpecLine){
          if (currentCol < keybSpecSpaceCol) currentCol = keybSpecAbcCol; 
          if (currentCol > keybSpecSpaceCol-1 && currentCol < keybSpecDelCol) currentCol = keybSpecSpaceCol;
          if (currentCol > keybSpecDelCol-1 && currentCol < keybSpecOkCol) currentCol = keybSpecDelCol;
          if (currentCol > keybSpecOkCol-1) currentCol = keybSpecOkCol;
        }
      }
      return (keybComDone);
      break;
    case keybSelect:
      if (currentRow != keybSpecLine){ 
        addTyping (pgm_read_byte(&onscreenKeyb [currentKeybLayout][currentRow][currentCol]));}   
      else {
        switch (currentCol){
        case keybSpecAbcCol:
          changeKeybLayout();
          break;
        case keybSpecSpaceCol:
          addTyping(' ');
          break;
        case keybSpecDelCol:
          delTyping();
          break;
        case keybSpecOkCol:
          memcpy (typingStore, typing, sizeof(typing));
          typing[0] = 0;
          return (keybFinished);
          break;
        } 
      }
      return (keybComDone);
      break;
    case keybDel:
      if (strlen_P((char *)&onscreenKeyb[currentKeybLayout][currentRow]) > 0){
        delTyping();}
      else {
        memcpy (typingStore, typing, sizeof(typing));
        typing[0] = 0;
        return (keybFinished);
      }
      return (keybComDone);
      break;
    case keybLayout:
      changeKeybLayout();
      return (keybComDone);
      break;
    case keybSpace:
      addTyping(' ');
      return (keybComDone);
      break;
    case keybOk:
      memcpy (typingStore, typing, sizeof(typing));
      typing[0] = 0;
      return (keybFinished);
      break;
  }
  return (keybComUnknown);
}

char* OnscrKeyb::getTyping (){
  return (typingStore);
}
