#include <Arduino.h>
#include "SoftwareSerial.h"
//#include <WString.h>

#define maxLength 6
//uint8_t OUTPUT

char command[maxLength];
bool commandComplete = false;
bool fwd = false;
bool back = false;
bool stop = true;

char currCommand;

unsigned long start=0;
unsigned long rltimer=0;
//unsigned long elapsed;
unsigned int def_delay = 300;

uint8_t i = 0;

SoftwareSerial softSerial(12, 13); // RX, TX using software serial on pins 10, 11


void setup() {
  Serial.begin(115200);
  softSerial.begin(115200);

  // put your setup code here, to run once:

  pinMode(9, OUTPUT); //Back
  pinMode(10, OUTPUT); //Accellerate
  pinMode(11, OUTPUT); //Right
  pinMode(8, OUTPUT); //Left

  digitalWrite(9, LOW);
  digitalWrite(10, LOW);
  digitalWrite(11, LOW);
  digitalWrite(8, LOW);

  pinMode(2, OUTPUT); //Power the TTL to RS232 module
  pinMode(3, OUTPUT);
  digitalWrite(2, HIGH);
  digitalWrite(3, LOW);

  Serial.println(F("Cisco Car READY"));
  softSerial.println(F("Cisco Car READY"));
}

void loop() {
  // put your main code here, to run repeatedly:
  if(softSerial.available() > 0) {
    getIncomingChars();
  }

  //elapsed = (millis() - start);
  //Serial.println(elapsed);
  if ((millis() - start) > def_delay) {
    
    switch (currCommand) {
      case 'a':
        digitalWrite(11, LOW);    //ensure we do not get stuck in a left or right state
        digitalWrite(8, LOW);
        digitalWrite(10, LOW);    //stop accelerating after 500 miliseconds if no longer pressing button
        break;
      case 'b':
        digitalWrite(11, LOW);    //ensure we do not get stuck in a left or right state
        digitalWrite(8, LOW);
        digitalWrite(9, LOW);     //stop reversing after 500 miliseconds if no longer pressing button
        break;
/*      case 'r':
        digitalWrite(9, LOW);     //ensure we do not get stuck in a forward or back state
        digitalWrite(10, LOW);
        digitalWrite(11, LOW);    //stop turning right
        break;
      case 'l':
        digitalWrite(9, LOW);     //ensure we do not get stuck in a forward or back state
        digitalWrite(10, LOW);
        digitalWrite(8, LOW);    //stop turning left
        break;     */
      default:
        digitalWrite(9, LOW);     //ensure we do not get stuck in a forward or back state
        digitalWrite(10, LOW);      
    } 

  }
  
  if ((millis() - rltimer) > def_delay) {
        digitalWrite(11, LOW);    //stop turning right
        digitalWrite(8, LOW);    //stop turning left      
  }

/*
  if ((millis() % 500) == 1) {
        Serial.print(".");
        softSerial.print(".");     
  }
*/
  
  if (commandComplete == true) {
    processCommand();
  }
}

void getIncomingChars() {
  char inChar = softSerial.read();
  //Serial.print(inChar);
  
  if(inChar == 59 || inChar == 10 || inChar == 13){ //Read until terminated by ;
    commandComplete = true;
  } else {
    command[i++] = inChar;
  }
}

void processCommand(){

    /*  
    softSerial.print(command[0]);
    softSerial.print(command[1]);
    softSerial.print(command[2]);
    softSerial.println(command[3]);
    */
  
  if(command[0] == 'F' || command[0] == 'f'){ // FWD
    //pinModeFunc();
    digitalWrite(11, LOW);
    digitalWrite(8, LOW);
    Serial.println("FWD");
    softSerial.println("FWD");
  }

  if(command[0] == 'B' || command[0] == 'b'){ // BCK
    //pinModeFunc();
    start = millis();

    digitalWrite(10, LOW); //first set forward relay low
    digitalWrite(9, HIGH);
    currCommand = 'b';
    Serial.println("BACK");
    softSerial.println("BACK");
  }

  if(command[0] == 'A' || command[0] == 'a'){ // Accel
    //pinModeFunc();
    start = millis();

    digitalWrite(9, LOW); //first set backward relay low
    digitalWrite(10, HIGH);
    currCommand = 'a';
    Serial.println("FWD");
    softSerial.println("FWD");
  }

  if(command[0] == 'S' || command[0] == 's'){ // Switch to original control
    //pinModeFunc();

    digitalWrite(9, HIGH);
    Serial.println("Switch");
  }

  if(command[0] == 'R' || command[0] == 'r'){ // RGT
    //pinModeFunc();
    if((millis() - rltimer) > def_delay) {
      rltimer = millis();
      
      digitalWrite(8, LOW); //first set left relay low
      digitalWrite(11, HIGH);
      currCommand = 'r';
      Serial.println("RIGHT");
      softSerial.println("RIGHT");
    }
  }

  if(command[0] == 'L' || command[0] == 'l'){ // LFT
    //pinModeFunc();
    if((millis() - rltimer) > def_delay) {
      rltimer = millis();

      digitalWrite(11, LOW); //first set right relay low
      digitalWrite(8, HIGH);
      currCommand = 'l';
      Serial.println("LEFT");
      softSerial.println("LEFT");
    }    
  }

  memset(command,0,0);
  commandComplete = false;
  i=0;

}


