#include <Servo.h>
 
Servo myservo; 
 
void setup() {
  Serial.begin(9600); 
  myservo.attach(9); //Servo connected to D9
  myservo.write(90); 
}
 
void loop() {
  while (Serial.available() > 0) {
    myservo.write(0); 
    char n = Serial.read();
    delay(2); 
    if (n == '1') {
      myservo.write(0);
    } else {
      myservo.write(90);
    }
  }
}
