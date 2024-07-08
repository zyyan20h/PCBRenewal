#include <Arduino.h>
#include "Button2.h" //  https://github.com/LennartHennigs/Button2

#ifdef ESP32
    #include <WiFi.h>
#else
    #include <ESP8266WiFi.h>
#endif
#include "AudioFileSourceICYStream.h"
#include "AudioFileSourceBuffer.h"
#include "AudioGeneratorMP3.h"
#include "AudioOutputI2SNoDAC.h"

#define BUTTON_PIN 12

// To run, set your ESP8266 build to 160MHz, update the SSID info, and upload.

// Enter your WiFi setup here:
const char *SSID = "Jiasheng iPhone";
const char *PASSWORD = "12345678";

//const char *URL = "https://npr-ice.streamguys1.com/live.mp3";
//const char *URL="http://ndr-edge-206c.fra-lg.cdn.addradio.net/ndr/njoy/live/mp3/128/stream.mp3";//NJOY (German)


const char *arrayURL[] = {
  "http://playerservices.streamtheworld.com/api/livestream-redirect/KNBAFM.mp3",
  "http://npr-ice.streamguys1.com/live.mp3",
  "http://playerservices.streamtheworld.com/api/livestream-redirect/WUAL_HD3.mp3"
};

int ch = 0;
int autorun = 0;

Button2 b;    // https://github.com/LennartHennigs/Button2

AudioGeneratorMP3 *mp3;
AudioFileSourceICYStream *file;
AudioFileSourceBuffer *buff;
AudioOutputI2SNoDAC *out;

// Called when a metadata event occurs (i.e. an ID3 tag, an ICY block, etc.
void MDCallback(void *cbData, const char *type, bool isUnicode, const char *string)
{
  const char *ptr = reinterpret_cast<const char *>(cbData);
  (void) isUnicode; // Punt this ball for now
  // Note that the type and string may be in PROGMEM, so copy them to RAM for printf
  char s1[32], s2[64];
  strncpy_P(s1, type, sizeof(s1));
  s1[sizeof(s1)-1]=0;
  strncpy_P(s2, string, sizeof(s2));
  s2[sizeof(s2)-1]=0;
  Serial.printf("METADATA(%s) '%s' = '%s'\n", ptr, s1, s2);
  Serial.flush();
}

// Called when there's a warning or error (like a buffer underflow or decode hiccup)
void StatusCallback(void *cbData, int code, const char *string)
{
  const char *ptr = reinterpret_cast<const char *>(cbData);
  // Note that the string may be in PROGMEM, so copy it to RAM for printf
  char s1[64];
  strncpy_P(s1, string, sizeof(s1));
  s1[sizeof(s1)-1]=0;
  Serial.printf("STATUS(%s) '%d' = '%s'\n", ptr, code, s1);
  Serial.flush();
}



void setup()
{
  Serial.begin(115200);
  delay(1000);
  Serial.println("Connecting to WiFi");

  b.begin(BUTTON_PIN);
  b.setTapHandler(ShorPress);

  // WiFi.disconnect();
  // WiFi.softAPdisconnect(true);
  // WiFi.mode(WIFI_STA);
  
  // WiFi.begin(SSID, PASSWORD);

  // // Try forever
  // while (WiFi.status() != WL_CONNECTED) {
  //   Serial.println("...Connecting to WiFi");
  //   delay(1000);
  // }
  // Serial.println("Connected");

  ConnectToWifi();

  // audioLogger = &Serial;
  // file = new AudioFileSourceICYStream(URL_1);
  // file->RegisterMetadataCB(MDCallback, (void*)"ICY");
  // buff = new AudioFileSourceBuffer(file, 8192); //Could change size in 2048, 4096 or 8192
  // buff->RegisterStatusCB(StatusCallback, (void*)"buffer");
  // out = new AudioOutputI2SNoDAC();
  // mp3 = new AudioGeneratorMP3();
  // mp3->RegisterStatusCB(StatusCallback, (void*)"mp3");
  // mp3->begin(buff, out);

  runPlaying();
}


void ConnectToWifi() {

  Serial.println("Connecting to WiFi");
  WiFi.disconnect();
  WiFi.softAPdisconnect(true);
  WiFi.mode(WIFI_STA);
  WiFi.setPhyMode(WIFI_PHY_MODE_11G); // <== IMPORTANT to get stable connections!!!!
  WiFi.begin(SSID, PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("...Connecting to WiFi");
    delay(1000);
  }

  Serial.println("Connected");
}


void runPlaying(){
  audioLogger = &Serial;
  for (int i = 0; i< 3; i++){
    if (ch == i){
      file = new AudioFileSourceICYStream(arrayURL[i]);
      Serial.print("Now playing channel: ");
      Serial.println(ch);
    }
  }
  // file = new AudioFileSourceICYStream(URL);
  file->RegisterMetadataCB(MDCallback, (void*)"ICY");
  buff = new AudioFileSourceBuffer(file, 4096); //Could change size in 2048, 4096 or 8192
  buff->RegisterStatusCB(StatusCallback, (void*)"buffer");
  out = new AudioOutputI2SNoDAC();
  mp3 = new AudioGeneratorMP3();
  mp3->RegisterStatusCB(StatusCallback, (void*)"mp3");
  mp3->begin(buff, out);
}

void stopPlaying(){
  if (mp3) {
    mp3->stop();
    delete mp3;
    mp3 = NULL;
  }
  if (out) {
    out->stop();
    delete out;
    out = NULL;
  }
  if (buff) {
    buff->close();
    delete buff;
    buff = NULL;
  }
  if (file) {
    file->close();
    delete file;
    file = NULL;
  }
}


void playHendler() {
  static int lastms = 0;
  if (mp3->isRunning()) {
    autorun = 1;
    if (millis() - lastms > 1000) {
      lastms = millis();
      Serial.printf("Running for %d ms...\n", lastms);
      Serial.flush();
    }
    if (!mp3->loop()) mp3->stop();
  }
  else {
    // digitalWrite(D3, LOW);
    Serial.printf("MP3 done\n");
    delay(1000);
    /// if wifi disconnected ///
    if (WiFi.status() != WL_CONNECTED) {
      stopPlaying();
      ConnectToWifi();
      runPlaying();
    }
    /// run if MP3 done by interrupts ///
    if (autorun == 1 ) {
      Serial.printf("Trying to replay\n");
      stopPlaying();
      runPlaying();
      autorun = 0;
    }
  }
}

void ShorPress(Button2& b) {
//  EepromWrite();
//  StopPlaying();
//  RunPlaying();
if (ch == 0 ) {
  ch = 1;
  Serial.println("Change to ch 1");
  mp3->stop();
  autorun = 1;
}else if (ch == 1 ){
  ch = 2;
  Serial.println("Change to ch 2");
  mp3->stop();
  autorun = 1;
}else if (ch == 2 ){
  ch = 0;
  Serial.println("Change to ch 0");
  mp3->stop();
  autorun = 1;
}else{
  ch = 0;
  mp3->stop();
  autorun = 1;
}

}

void loop()
{
  // static int lastms = 0;

  // if (mp3->isRunning()) {
  //   if (millis()-lastms > 1000) {
  //     lastms = millis();
  //     Serial.printf("Running for %d ms...\n", lastms);
  //     Serial.flush();
  //    }
  //   if (!mp3->loop()) mp3->stop();
  // } else {
  //   Serial.printf("MP3 done\n");
  //   delay(1000);
  // }
b.loop();
playHendler();

}
