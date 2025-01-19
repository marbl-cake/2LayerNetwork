#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <SPI.h>
#include <MFRC522.h>
#include <RF24.h>
#include <RF24Network.h>

// Configurazione Wi-Fi
const char* ssid = "ESP_AP";
const char* password = "12345678";
WiFiUDP Udp;
unsigned int localPort = 8888;
const int buzzer = 5;

// Variabili per il modulo RFID
byte incomingPacket[10]; 
#define RST_PIN    2  
#define SS_PIN     16 
MFRC522 mfrc522(SS_PIN, RST_PIN); 

// Configurazione nRF24
#define CE_PIN  0
#define CSN_PIN 15
RF24 radio(CE_PIN, CSN_PIN);  // Pin CE (0) e CSN (15)
RF24Network network(radio);
const uint16_t raspberryPi_node = 0;  // Indirizzo Raspberry Pi (master)
const uint16_t thisNode = 01;
byte payload_out[32];  // dati da inviare

void setup() {
  pinMode(buzzer, OUTPUT);
 
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connessione in corso...");
  }
  Serial.println("Connesso alla rete Wi-Fi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  Udp.begin(localPort);

  
  SPI.begin();

  mfrc522.PCD_Init();
  

// Inizializzazione nRF24
  Serial.println("Inizializzazione modulo nRF24...");
  radio.begin();
  network.begin(90, thisNode);  // canale 90, nodo Raspberry Pi
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_250KBPS);
  radio.setChannel(100);  // Canale 100
  if (radio.isChipConnected()) {
    Serial.println("nRF24 connesso!");
  } else {
    Serial.println("nRF24 non connesso!");
  }
 
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    Serial.print("\n\n-------------------------------------------------------\nPacchetto UDP ricevuto! Dimensione: ");
    Serial.println(packetSize);

    int len = Udp.read(incomingPacket, 10);  // Leggi massimo 10 byte (lunghezza dell'UID)
    if (len > 0) {
      Serial.println("Invio UID al Raspberry Pi...");
      sendUIDToRaspberryPi(incomingPacket, len, false);  // Flag false per indicare che è stato ricevuto tramite UDP
      tone(buzzer, 1000);
      delay(100);
      noTone(buzzer);
    }
  }

  if (mfrc522.PICC_IsNewCardPresent()) {
    if (mfrc522.PICC_ReadCardSerial()) {
      byte uidToSend[10];
      int uidLength = mfrc522.uid.size;


      for (int i = 0; i < uidLength; i++) {
        uidToSend[i] = mfrc522.uid.uidByte[i];
      }

      Serial.println("\n\n----------------------------------------------------\nInvio UID letto dal RFID al Raspberry Pi...");
      sendUIDToRaspberryPi(uidToSend, uidLength, true);  // Flag true per indicare che è stato letto tramite RFID
    }

 
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
  }


  network.update(); 

  delay(100);
}


void sendUIDToRaspberryPi(byte* uid, int length, bool isRFID) {
  payload_out[0] = isRFID ? 1 : 0; 
  for (int i = 0; i < length; i++) {
    payload_out[i + 1] = uid[i]; 
  }

  // Se stai inviando tramite nRF24, gestisci l'accesso al bus SPI
  SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE0));  // Configura l'SPI per il nRF24
  RF24NetworkHeader header(raspberryPi_node);

  radio.flush_tx();
  radio.flush_rx();

  network.update();

  if (network.write(header, payload_out, length + 1)) {
    Serial.print("\n\nUID inviato al Raspberry Pi tramite nRF24: ");
    for (int i = 0; i < length; i++) {
      Serial.print(payload_out[i + 1] < 0x10 ? " 0" : " ");
      Serial.print(payload_out[i + 1], HEX);
    }
    Serial.println("\n----------------------------------------------------------");

    if(isRFID){
      tone(buzzer, 2000);
      delay(80);
      noTone(buzzer);
      delay(40);
      tone(buzzer, 2000);
      delay(80);
      noTone(buzzer);
    }
  } else {
    Serial.println("\n\nErrore\n-----------------------------------------------------");
  }

  SPI.endTransaction();  // Termina la comunicazione SPI con nrf24
}
