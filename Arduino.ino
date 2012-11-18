
/******************
 * This program reads serial data containing helicopter joystick values
 * from a laptop and controls servos mounted to the helicopter remote.
 ******************/

#include <Servo.h>

#define INTERRUPT 97 // 'a'
#define LIGHTS 98    // 'b'
const int servoPins[] = {9, 10, 11};

int numOfInterrupts = 0;
int numOfLightSignals = 0;
int c, d;
int readNumber = 99;

boolean ledOn = false;

Servo servo[3];

// Setup routine.
void setup() {
  // initialize serial communication at 115200 bits per second:
  Serial.begin(115200);
  
  // Initialize servos.
  servo[0].attach(servoPins[0]);
  for(int i=1;i<3;i++) {
    (servo[i]).attach(servoPins[i]);
  }
  servo[0].write(135);
  servo[1].write(90);
  servo[2].write(90);
  
  // Setup debug LEDs
  pinMode(8,OUTPUT);
  pinMode(12,OUTPUT);
  pinMode(13,OUTPUT);
  pinMode(A0,OUTPUT);
}


// the loop routine runs over and over again forever:
void loop() {
}

// Called when there is serial data available.
void serialEvent() {
  while(Serial.available() > 0) {
    d = c = Serial.read();
    
    if(numOfInterrupts==3)readNumber = 0;
    
    // Count interrupt signals to know when to expect data.
    if(c==INTERRUPT)numOfInterrupts++;
    else numOfInterrupts = 0;
    if(c==LIGHTS)numOfLightSignals++;
    else numOfLightSignals = 0;
    
    // If this byte is a servo position
    if(readNumber < 3) {
      switch(readNumber) {
        case 0:
          c = 135-c*135/255;
          break;
        case 1:
          c = 64+c/2;
          break;
        case 2:
          c = 192-c/2;
          break;
        default:break;
      }
      
      // Set the position of one of the servos.
      servo[readNumber].write(c);
      
      // Set indicator LEDs for debuging.
      ledOn = d>80;
      int pin = 2;
      switch(readNumber){
        case 0:pin=8;break;
        case 1:pin=12;break;
        case 2:pin=13;break;
        default:break;
      }
      digitalWrite(pin,ledOn?HIGH:LOW);
      
      numOfInterrupts = 0;
      numOfLightSignals = 0;
      readNumber++;
    }
    
    if(numOfLightSignals == 3) {
      /////Toggle lights.
      
      ledOn = !ledOn;
      digitalWrite(A0,ledOn?HIGH:LOW);
      
      numOfLightSignals = 0;
    }
  }
}
