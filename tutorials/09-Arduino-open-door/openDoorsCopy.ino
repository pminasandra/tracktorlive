#include <AccelStepper.h>
#define HALFSTEP 8

// Motor pin definitions
#define motorPin1  2     // IN1 on the ULN2003 driver 1
#define motorPin2  3     // IN2 on the ULN2003 driver 1
#define motorPin3  4     // IN3 on the ULN2003 driver 1
#define motorPin4  5     // IN4 on the ULN2003 driver 1

// Initialize with pin sequence IN1-IN3-IN2-IN4 for using the AccelStepper with 28BYJ-48
AccelStepper stepper1(HALFSTEP, motorPin1, motorPin3, motorPin2, motorPin4);

const int stepsToRun = 500;
char c;

void setup() {
  Serial.begin(9600);
  stepper1.setMaxSpeed(500);       // maximum speed (steps/sec)
  stepper1.setAcceleration(200);   // acceleration (steps/sec^2)
}

void loop() {
  if (Serial.available() > 0) {
    c = Serial.read();
    if (c == 'm') {
      stepper1.moveTo(-stepsToRun*2);   // set a target position
      delay(500);
    }
    if (c == 'k') {
      stepper1.moveTo(0);   // go back to origin
      delay(500);
    }
  }
  stepper1.run();  // keeps moving to the target until it's reached
}
