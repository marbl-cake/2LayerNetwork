#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <SPI.h>
#include <MFRC522.h>

const char* ssid = "ESP_AP";
const char* password = "12345678";
WiFiUDP Udp;
unsigned int localPort = 8888;

const int buttonPin = 16; 
int buttonState = 0;
int currentState;
int c = 0;

int pinRosso = 15;  // GPIO D8
int pinGiallo = 2; // GPIO D4
int pinVerde = 0;  // GPIO D3

int semaforo(int color);
void button();



#define RST_PIN    5  
#define SS_PIN     4

MFRC522 mfrc522(SS_PIN, RST_PIN); 


void setup() {

  pinMode(buttonPin, INPUT_PULLUP); // La ESP8266 ha una resistenza di pull-up interna

  pinMode(pinRosso, OUTPUT);
  pinMode(pinGiallo, OUTPUT);
  pinMode(pinVerde, OUTPUT);
  
  Serial.begin(115200);

  WiFi.softAP(ssid, password);
  Serial.println("Access Point avviato");
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());

  Udp.begin(localPort);




  SPI.begin();

  mfrc522.PCD_Init();
  
  Serial.println("Sistema RFID pronto. Avvicina un tag.");
}

void loop() {

  button();

  semaforo(c);

  if (mfrc522.PICC_IsNewCardPresent()) {
    Serial.println("carta presente");

    if (mfrc522.PICC_ReadCardSerial()) {
      Serial.print("Tag ID: ");
      

      for (byte i = 0; i < mfrc522.uid.size; i++) {
        
        Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(mfrc522.uid.uidByte[i], HEX);
      }
      Serial.println();

      byte toSend[mfrc522.uid.size +1];

      for(byte i = 0; i < mfrc522.uid.size; i++){
        toSend[i] = mfrc522.uid.uidByte[i];
      }

      byte a = c;

      toSend[mfrc522.uid.size] = a;

      Serial.println(mfrc522.uid.size);

      for(byte i = 0; i < mfrc522.uid.size +2; i++){
        Serial.print(toSend[i]);
        Serial.print(" "); 
      }


      Udp.beginPacket("192.168.4.2", 8888);  // IP di ESP8266 #2 (station)
      Udp.write(toSend, sizeof(toSend)/sizeof(toSend[0]));
      Udp.endPacket();
      
      Serial.println("Messaggio inviato");


      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();
    }
  }
}

void button() {
  buttonState = digitalRead(buttonPin);
  
  if (buttonState == HIGH && buttonState != currentState) {
    delay(50); 
    
    c++;
    if (c > 3) {
      c = 1;
    }
    
    Serial.println(c);
  }
  
  currentState = buttonState;
}

int semaforo(int color){
  switch(color){
    case 1:
      digitalWrite(pinRosso, HIGH);
      digitalWrite(pinGiallo, LOW);
      digitalWrite(pinVerde, LOW);
      return 1;
      break;
    case 2:
      digitalWrite(pinRosso, LOW);
      digitalWrite(pinGiallo, HIGH);
      digitalWrite(pinVerde, LOW);
      return 1;
      break;
    case 3:
      digitalWrite(pinRosso, LOW);
      digitalWrite(pinGiallo, LOW);
      digitalWrite(pinVerde, HIGH);
      return 1;
      break;
    default:
      return 0;
      break; 
  }
}
