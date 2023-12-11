#include "AFMotor.h"
#include <Servo.h>

// Motores Shield
AF_DCMotor motorFrontLeft(1);
AF_DCMotor motorFrontRight(3);
AF_DCMotor motorBackLeft(2);
AF_DCMotor motorBackRight(4);

// Servos
Servo servoBackLeft;
Servo servoBackRight;
Servo servoFrontLeft;
Servo servoFrontRight;

// Constantes
uint8_t SPEED_MAX = 255;
uint8_t SPEED_MIN = 120;

const short int ANGULO_MIN = 45;
const short int ANGULO_MAX = 135;
const short int ANGULO_INICIAL = 95;

const short int PINO_SERVO_BACK_LEFT = 13;
const short int PINO_SERVO_BACK_RIGHT = 2;
const short int PINO_SERVO_FRONT_LEFT = 9;
const short int PINO_SERVO_FRONT_RIGHT = 10;

const int DELAY_RAMPA = 30;

const int TIME_WAIT = 1000; 

void menu(char *op, unsigned int *value);
void forward(unsigned int speed);
void backward(unsigned int speed);
void stop(unsigned int speed);
void frontTurn(int angulo);
void backTurn(int angulo);
void turnLeft(int angulo, int currentAngleFront, char parte);
void turnRight(int angulo, int currentAngleFront, char parte);
void shutdown();

unsigned int value = 0;
int angulo = 0;
int speedGlobal = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial) { ; }
  // Motores conectados a shild
  motorBackLeft.run(RELEASE);
  motorBackRight.run(RELEASE);
  motorFrontLeft.run(RELEASE);
  motorFrontRight.run(RELEASE);

  servoBackLeft.attach(PINO_SERVO_BACK_LEFT);
  servoBackRight.attach(PINO_SERVO_BACK_RIGHT);
  servoFrontLeft.attach(PINO_SERVO_FRONT_LEFT);
  servoFrontRight.attach(PINO_SERVO_FRONT_RIGHT);

  servoBackLeft.write(ANGULO_INICIAL);
  servoBackRight.write(ANGULO_INICIAL);
  servoFrontLeft.write(ANGULO_INICIAL);
  servoFrontRight.write(ANGULO_INICIAL);
  delay(20);
}

void loop() {
  String command = "";
  
  while(Serial.available()>0){
    command = Serial.readString();
    command.trim();

    char op = command[0];
    if (op != 'S'){
      command.remove(0,1);
      value = command.toInt();
    }
    menu(&op, &value);
    Serial.println("OK\n");
    command = "";
  }
}

void menu(char *op, unsigned int *value){
  switch (*op) {
      case 'F': forward(*value); break; // Forward
      case 'B': backward(*value); break; // Backward
      case 'S': stop(*value); break; // Stop
      case 'A': frontTurn(*value); break; // Vira roda frontal
      case 'Z': backTurn(*value); break; // Vira roda traseira
      case 'D': shutdown(); break; // Desligar rodas e servos
    }
}

void stop(unsigned int speed){
  Serial.print("Stoping "); Serial.println(speed);
  for (speed; speed>0; speed--){
    motorBackLeft.setSpeed(speed);
    motorBackRight.setSpeed(speed);
    motorFrontLeft.setSpeed(speed);
    motorFrontRight.setSpeed(speed);
    delay(DELAY_RAMPA);
  }
  motorBackLeft.run(RELEASE);
  motorBackRight.run(RELEASE);
  motorFrontLeft.run(RELEASE);
  motorFrontRight.run(RELEASE);
  delay(DELAY_RAMPA);
	speedGlobal = 0;
}

void forward(unsigned int speed){
  motorBackLeft.run(BACKWARD);
  motorBackRight.run(FORWARD);
  motorFrontLeft.run(BACKWARD);
  motorFrontRight.run(FORWARD);
  delay(DELAY_RAMPA);

  for (unsigned int i=SPEED_MIN; (i<speed && i<SPEED_MAX); i++){
    motorBackLeft.setSpeed(i);
    motorBackRight.setSpeed(i);
    motorFrontLeft.setSpeed(i);
    motorFrontRight.setSpeed(i);
    delay(DELAY_RAMPA);
  }
	speedGlobal = speed;
}

void backward(unsigned int speed){
  motorBackLeft.run(FORWARD);
  motorBackRight.run(BACKWARD);
  motorFrontLeft.run(FORWARD);
  motorFrontRight.run(BACKWARD);
  delay(DELAY_RAMPA);

  for (unsigned int i=SPEED_MIN; (i<speed && i<SPEED_MAX); i++){
    motorBackLeft.setSpeed(i);
    motorBackRight.setSpeed(i);
    motorFrontLeft.setSpeed(i);
    motorFrontRight.setSpeed(i);
    delay(DELAY_RAMPA);
  }
	speedGlobal = speed;
}

void frontTurn(int angulo){
  int currentAngleFront = servoFrontLeft.read();
  if (speedGlobal > 0)
    stop(speedGlobal);

  if(angulo < ANGULO_INICIAL){
    if(currentAngleFront > angulo)
      turnLeft(angulo, currentAngleFront, 'F');
    else
      turnRight(angulo, currentAngleFront, 'F');
  } else { 
      if(currentAngleFront < angulo)
        turnRight(angulo, currentAngleFront, 'F');
      else
        turnLeft(angulo, currentAngleFront, 'F');
  }
}

void backTurn(int angulo){
  int currentAngleFront = servoBackLeft.read();
  if (speedGlobal > 0)
    stop(speedGlobal);

  if(angulo < ANGULO_INICIAL){
    if(currentAngleFront > angulo)
      turnLeft(angulo, currentAngleFront, 'B');
    else
      turnRight(angulo, currentAngleFront, 'B');
  } else { 
      if(currentAngleFront < angulo)
        turnRight(angulo, currentAngleFront, 'B');
      else
        turnLeft(angulo, currentAngleFront, 'B');
  }
}

void turnLeft(int angulo, int currentAngleFront, char parte){
  if (parte == 'F') {
    for (int pos = currentAngleFront; pos >= angulo; pos--) {  
      servoFrontLeft.write(pos);
      servoFrontRight.write(pos);
      delay(20);
    }
  } else {
    for (int pos = currentAngleFront; pos >= angulo; pos--) {  
      servoBackLeft.write(pos);
      servoBackRight.write(pos);
      delay(20);
    }
  }
}

void turnRight(int angulo, int currentAngleFront, char parte){
 if (parte == 'F') {
    for (int pos = currentAngleFront; pos <= angulo; pos++) {  
      servoFrontLeft.write(pos);
      servoFrontRight.write(pos);
      delay(20);
    }
  } else {
    for (int pos = currentAngleFront; pos <= angulo; pos++) {  
      servoBackLeft.write(pos);
      servoBackRight.write(pos);
      delay(20);
    }
  }
}

void shutdown(){
  Serial.println("Desligando");
  stop(speedGlobal);
  frontTurn(ANGULO_INICIAL);
  backTurn(ANGULO_INICIAL);
  delay(50);
}