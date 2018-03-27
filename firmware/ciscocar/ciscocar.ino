/* 
 *  This is a simple sketch to activate relays based on commands recieved via serial.
 */

#include <Arduino.h>
#include "SoftwareSerial.h"


#define maxLength 6


char command[maxLength];
bool commandComplete = false;

char currCommand;

unsigned long start=0;
unsigned long rltimer=0;
//unsigned long elapsed;
unsigned int def_delay = 150;
unsigned int def_delay_fb = 500;

uint8_t i = 0;
int fwd = 8;
int back = 9;
int left = 10;
int right = 11;

SoftwareSerial softSerial(12, 13); // RX, TX using software serial on pins 12, 13


void setup() {
  Serial.begin(115200);
  softSerial.begin(115200);

  // put your setup code here, to run once:

  pinMode(back, OUTPUT); 
  pinMode(left, OUTPUT); 
  pinMode(right, OUTPUT); 
  pinMode(fwd, OUTPUT); 

  digitalWrite(back, LOW);
  digitalWrite(left, LOW);
  digitalWrite(right, LOW);
  digitalWrite(fwd, LOW);

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
  if ((millis() - start) > def_delay_fb) {
    
    switch (currCommand) {
      case 'a':
        digitalWrite(right, LOW);    //ensure we do not get stuck in a left or right state
        digitalWrite(left, LOW);
        digitalWrite(fwd, LOW);    //stop accelerating after 500 miliseconds if no longer pressing button
        break;
      case 'b':
        digitalWrite(right, LOW);    //ensure we do not get stuck in a left or right state
        digitalWrite(left, LOW);
        digitalWrite(back, LOW);     //stop reversing after 500 miliseconds if no longer pressing button
        break;
/*      case 'r':
        digitalWrite(back, LOW);     //ensure we do not get stuck in a forward or back state
        digitalWrite(left, LOW);
        digitalWrite(right, LOW);    //stop turning right
        break;
      case 'l':
        digitalWrite(back, LOW);     //ensure we do not get stuck in a forward or back state
        digitalWrite(left, LOW);
        digitalWrite(fwd, LOW);    //stop turning left
        break;     */
      default:
        digitalWrite(back, LOW);     //ensure we do not get stuck in a forward or back state
        digitalWrite(fwd, LOW);      
    } 

  }
  
  if ((millis() - rltimer) > def_delay) {
        digitalWrite(right, LOW);    //stop turning right
        digitalWrite(left, LOW);    //stop turning left      
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
    start = millis();

    digitalWrite(back, LOW); //first set backward relay low
    digitalWrite(fwd, HIGH);
    currCommand = 'a';
    Serial.println("FWD");
    softSerial.println("FWD");
  }

  if(command[0] == 'B' || command[0] == 'b'){ // BCK
    //pinModeFunc();
    start = millis();

    digitalWrite(fwd, LOW); //first set forward relay low
    digitalWrite(back, HIGH);
    currCommand = 'b';
    Serial.println("BACK");
    softSerial.println("BACK");
  }

  if(command[0] == 'A' || command[0] == 'a'){ // Accel
    //pinModeFunc();
    start = millis();

    digitalWrite(back, LOW); //first set backward relay low
    digitalWrite(fwd, HIGH);
    currCommand = 'a';
    Serial.println("FWD");
    softSerial.println("FWD");
  }

  if(command[0] == 'S' || command[0] == 's'){ // Switch to original control
    //pinModeFunc();

    digitalWrite(back, HIGH);
    Serial.println("Switch");
  }

  if(command[0] == 'R' || command[0] == 'r'){ // RGT
    //pinModeFunc();
    if((millis() - rltimer) > def_delay) {
      rltimer = millis();
      
      digitalWrite(left, LOW); //first set left relay low
      digitalWrite(right, HIGH);
      currCommand = 'r';
      Serial.println("RIGHT");
      softSerial.println("RIGHT");
    }
  }

  if(command[0] == 'L' || command[0] == 'l'){ // LFT
    //pinModeFunc();
    if((millis() - rltimer) > def_delay) {
      rltimer = millis();

      digitalWrite(right, LOW); //first set right relay low
      digitalWrite(left, HIGH);
      currCommand = 'l';
      Serial.println("LEFT");
      softSerial.println("LEFT");
    }    
  }

  memset(command,0,0);
  commandComplete = false;
  i=0;

}


