// MorseFromPhone_USB.ino
// Reads newline-terminated ASCII lines from Serial (USB) and blinks LED in Morse.

const int LED_PIN = 13; // onboard LED, or change to external pin

// Timing (ms) - adjust if you want slower/faster
const unsigned long DOT = 200;
const unsigned long DASH = 600;
const unsigned long INTRA_GAP = 200;  // between parts of same letter
const unsigned long LETTER_GAP = 600; // between letters
const unsigned long WORD_GAP = 1400;  // between words

struct MorseMap { char ch; const char *pat; };
MorseMap table[] = {
  {'A', ".-"},{'B', "-..."},{'C', "-.-."},{'D', "-.."},{'E', "."},
  {'F', "..-."},{'G', "--."},{'H', "...."},{'I', ".."},{'J', ".---"},
  {'K', "-.-"},{'L', ".-.."},{'M', "--"},{'N', "-."},{'O', "---"},
  {'P', ".--."},{'Q', "--.-"},{'R', ".-."},{'S', "..."},{'T', "-"},
  {'U', "..-"},{'V', "...-"},{'W', ".--"},{'X', "-..-"},{'Y', "-.--"},
  {'Z', "--.."},{'0', "-----"},{'1', ".----"},{'2', "..---"},{'3', "...--"},
  {'4', "....-"},{'5', "....."},{'6', "-...."},{'7', "--..."},{'8', "---.."},
  {'9', "----."}
};
const int TABLE_SIZE = sizeof(table) / sizeof(table[0]);

String lookupMorse(char c){
  c = toupper(c);
  for (int i=0; i<TABLE_SIZE; ++i){
    if (table[i].ch == c) return String(table[i].pat);
  }
  return String("");
}

void blinkOn(unsigned long ms){
  digitalWrite(LED_PIN, HIGH);
  delay(ms);
  digitalWrite(LED_PIN, LOW);
}

void blinkPattern(const String &pat){
  for (unsigned int i=0;i<pat.length();++i){
    if (pat[i] == '.') blinkOn(DOT);
    else blinkOn(DASH);
    if (i < pat.length()-1) delay(INTRA_GAP);
  }
}

void sendTextAsMorse(const String &txt){
  for (unsigned int i=0; i<txt.length(); ++i){
    char c = txt[i];
    if (c == ' '){
      delay(WORD_GAP);
      continue;
    }
    String pat = lookupMorse(c);
    if (pat.length() == 0) continue; // skip unknown chars
    blinkPattern(pat);
    delay(LETTER_GAP);
  }
}

void setup(){
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.begin(115200);
  Serial.println("MorseFromPhone_USB ready. Send a line (newline-terminated).");
}

void loop(){
  // Read line (non-blocking style)
  if (Serial.available()){
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length()){
      Serial.print("RX: ");
      Serial.println(line);
      sendTextAsMorse(line);
      Serial.println("DONE");
    }
  }
}