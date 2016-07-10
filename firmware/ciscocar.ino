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

unsigned long start;
//unsigned long elapsed;
unsigned int def_delay = 500;

uint8_t i = 0;



void setup() {
  Serial.begin(9600);

  // put your setup code here, to run once:

  pinMode(9, OUTPUT); //Control original or direct
  pinMode(10, OUTPUT); //Accellerate
  pinMode(11, OUTPUT); //Pin 12+13 both set direction of travel
  pinMode(12, OUTPUT); //

  digitalWrite(9, LOW);
  digitalWrite(10, LOW);
  digitalWrite(11, LOW);
  digitalWrite(12, LOW);
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
        digitalWrite(10, LOW);    //stop accelerating after 500 miliseconds if no longer pressing button
        break;
      case 'l':
        //digitalWrite(10, LOW); 
        break;
      case 'r':
        //digitalWrite(10, LOW); 
        break;     
      //default:
    }
    
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
    digitalWrite(11, HIGH);
    digitalWrite(12, HIGH);
    Serial.println("BACK");
  }

  if(command[0] == 'A' || command[0] == 'a'){ // Accel
    //pinModeFunc();
    start = millis();
    
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
    start = millis();
    Serial.println("RIGHT");
  }

  if(command[0] == 'L' || command[0] == 'l'){ // LFT
    //pinModeFunc();
    start = millis();
    Serial.println("LEFT");
  }

  memset(command,0,0);
  commandComplete = false;
  i=0;

}


