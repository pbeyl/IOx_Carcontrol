#include <Arduino.h>
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



void setup() {
  Serial.begin(9600);

  // put your setup code here, to run once:

  pinMode(9, OUTPUT); //Back
  pinMode(10, OUTPUT); //Accellerate
  pinMode(11, OUTPUT); //Right
  pinMode(12, OUTPUT); //Left

  digitalWrite(9, LOW);
  digitalWrite(10, LOW);
  digitalWrite(11, LOW);
  digitalWrite(12, LOW);

  pinMode(2, OUTPUT); //Power the TTL to RS232 module
  pinMode(3, OUTPUT);
  digitalWrite(2, LOW);
  digitalWrite(3, HIGH);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available() > 0) {
    getIncomingChars();
  }

  //elapsed = (millis() - start);
  //Serial.println(elapsed);
  if ((millis() - start) > def_delay) {
    
    switch (currCommand) {
      case 'a':
        digitalWrite(11, LOW);    //ensure we do not get stuck in a left or right state
        digitalWrite(12, LOW);
        digitalWrite(10, LOW);    //stop accelerating after 500 miliseconds if no longer pressing button
        break;
      case 'b':
        digitalWrite(11, LOW);    //ensure we do not get stuck in a left or right state
        digitalWrite(12, LOW);
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
        digitalWrite(12, LOW);    //stop turning left
        break;     */
      default:
        digitalWrite(9, LOW);     //ensure we do not get stuck in a forward or back state
        digitalWrite(10, LOW);      
    } 
    
  }
  
  if ((millis() - rltimer) > def_delay) {
        digitalWrite(11, LOW);    //stop turning right
        digitalWrite(12, LOW);    //stop turning left      
  }
  
  if (commandComplete == true) {
    processCommand();
  }
}

void getIncomingChars() {
  char inChar = Serial.read();
  if(inChar == 59 || inChar == 10 || inChar == 13){ //Read until terminated by ;
    commandComplete = true;
  } else {
    command[i++] = inChar;
  }
}

void processCommand(){
  
  /*
   * Serial.print(command[0]);
    Serial.print(command[1]);
    Serial.print(command[2]);
    Serial.println(command[3]);
*/
  
  if(command[0] == 'F' || command[0] == 'f'){ // FWD
    //pinModeFunc();
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    Serial.println("FWD");
  }

  if(command[0] == 'B' || command[0] == 'b'){ // BCK
    //pinModeFunc();
    start = millis();

    digitalWrite(10, LOW); //first set forward relay low
    digitalWrite(9, HIGH);
    currCommand = 'b';
    Serial.println("BACK");
  }

  if(command[0] == 'A' || command[0] == 'a'){ // Accel
    //pinModeFunc();
    start = millis();

    digitalWrite(9, LOW); //first set backward relay low
    digitalWrite(10, HIGH);
    currCommand = 'a';
    Serial.println("Accel");
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
      
      digitalWrite(12, LOW); //first set left relay low
      digitalWrite(11, HIGH);
      currCommand = 'r';
      Serial.println("RIGHT");
    }
  }

  if(command[0] == 'L' || command[0] == 'l'){ // LFT
    //pinModeFunc();
    if((millis() - rltimer) > def_delay) {
      rltimer = millis();

      digitalWrite(11, LOW); //first set right relay low
      digitalWrite(12, HIGH);
      currCommand = 'l';
      Serial.println("LEFT");
    }    
  }

  memset(command,0,0);
  commandComplete = false;
  i=0;

}


