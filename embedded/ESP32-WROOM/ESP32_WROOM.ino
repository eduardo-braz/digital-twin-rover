#include <ESP32Servo.h>

Servo servoBase;
Servo servoExt1;
Servo servoExt2;
Servo servoGripper;

#define SERVO_PIN_BASE 2
#define SERVO_PIN_EXT1 5
#define SERVO_PIN_EXT2 18
#define SERVO_PIN_GRIPPER 4

#define BAT_ARM 35
#define BAT_RASPBERRY 15
#define BAT_WHEELS 32
#define BAT_CAMERA 33

#define ANGULO_BASE_MIN 0
#define ANGULO_BASE_MAX 165
#define ANGULO_BASE_DEFAULT 90

#define ANGULO_EXT1_MIN 30
#define ANGULO_EXT1_MAX 150
#define ANGULO_EXT1_DEFAULT 30

#define ANGULO_EXT2_MIN 30
#define ANGULO_EXT2_MAX 100
#define ANGULO_EXT2_DEFAULT 100

#define ANGULO_GRIPPER_MIN 70
#define ANGULO_GRIPPER_MAX 170
#define ANGULO_GRIPPER_DEFAULT 170

#define DELAY_SERVO 20

int currentAngleBase = 0;
int currentAngleExt1 = 0;
int currentAngleExt2 = 0;
int currentAngleGripper = 0;
unsigned int value = 0;

void menu(char *op, unsigned int *value);
void gripper(int angulo);
void ext1Turn(int angulo);
void ext2Turn(int angulo);
void baseTurn(int angulo);
void turnLeft(int angulo, int currentAngle, char parte);
void turnRight(int angulo, int currentAngle, char parte);
void shutdown();
void checkBaterry(int bat);

void setup() {
  Serial.begin(9600);
  while (!Serial) { ; }
  delay(2000);
  servoBase.attach(SERVO_PIN_BASE); 
  servoExt1.attach(SERVO_PIN_EXT1);
  servoExt2.attach(SERVO_PIN_EXT2);
  servoGripper.attach(SERVO_PIN_GRIPPER);

  servoBase.write(ANGULO_BASE_DEFAULT); 
  servoExt1.write(ANGULO_EXT1_DEFAULT);
  servoExt2.write(ANGULO_EXT2_DEFAULT);
  servoGripper.write(ANGULO_GRIPPER_DEFAULT);
  delay(DELAY_SERVO);
}

void loop() {
  String command = "";
  while(Serial.available()>0){
    command = Serial.readString();
    command.trim();

    char op = command[0];
    command.remove(0,1);
    value = command.toInt();
    
    menu(&op, &value);
    if (op != 'C')
      Serial.println("OK");
    command = "";
  }
}

void menu(char *op, unsigned int *value){
  switch (*op) {
      case 'B': baseTurn(*value); break; // Movimento base
      case 'E': ext1Turn(*value); break; // Movimento ext1
      case 'F': ext2Turn(*value); break; // Movimento ext2
      case 'G': gripper(*value); break; // Gripper
      case 'S': shutdown(); break; // Desligar servos
      case 'C': checkBaterry(*value); break; // Verifica carga de bateria
    }
}
void checkBaterry(int bat){
  int load = 0;
  delay(300);
  if (bat == 1){
    load = analogRead(BAT_RASPBERRY);
  } else if (bat == 2) {
    load = analogRead(BAT_WHEELS);
  } else if (bat == 3) {
    load = analogRead(BAT_ARM);

  } else if (bat == 4) {
    load = analogRead(BAT_CAMERA);
  }
  Serial.println(load);
}

void baseTurn(int angulo){
  int currentAngle = (servoBase.read() + 1);
  if (angulo < ANGULO_BASE_MIN)
    angulo = ANGULO_BASE_MIN;
  if (angulo > ANGULO_BASE_MAX)
    angulo = ANGULO_BASE_MAX;

  if(angulo < ANGULO_BASE_DEFAULT){
    if(currentAngle > angulo)
      turnLeft(angulo, currentAngle, 'B');
    else
      turnRight(angulo, currentAngle, 'B');
  } else { 
      if(currentAngle < angulo)
        turnRight(angulo, currentAngle, 'B');
      else
        turnLeft(angulo, currentAngle, 'B');
  }
}

void gripper(int angulo){
  int currentAngle = (servoGripper.read() + 1);
  if (angulo < ANGULO_GRIPPER_MIN)
    angulo = ANGULO_GRIPPER_MIN;
  if (angulo > ANGULO_GRIPPER_MAX)
    angulo = ANGULO_GRIPPER_MAX;

  if(angulo < ANGULO_GRIPPER_DEFAULT){
    if(currentAngle > angulo)
      turnLeft(angulo, currentAngle, 'G');
    else
      turnRight(angulo, currentAngle, 'G');
  } else { 
      if(currentAngle < angulo)
        turnRight(angulo, currentAngle, 'G');
      else
        turnLeft(angulo, currentAngle, 'G');
  }
}

void ext1Turn(int angulo){ 
  int currentAngle = (servoExt1.read() + 1);
  if (angulo < ANGULO_EXT1_MIN)
    angulo = ANGULO_EXT1_MIN;
  if (angulo > ANGULO_EXT1_MAX)
    angulo = ANGULO_EXT1_MAX;

  if(angulo < ANGULO_EXT1_DEFAULT){
    if(currentAngle > angulo)
      turnLeft(angulo, currentAngle, 'E');
    else
      turnRight(angulo, currentAngle, 'E');
  } else { 
      if(currentAngle < angulo)
        turnRight(angulo, currentAngle, 'E');
      else
        turnLeft(angulo, currentAngle, 'E');
  }
}

void ext2Turn(int angulo){ 
  int currentAngle = (servoExt2.read() + 1);
  if (angulo < ANGULO_EXT2_MIN)
    angulo = ANGULO_EXT2_MIN;
  if (angulo > ANGULO_EXT2_MAX)
    angulo = ANGULO_EXT2_MAX;

  if(angulo < ANGULO_EXT2_DEFAULT){
    if(currentAngle > angulo)
      turnLeft(angulo, currentAngle, 'F');
    else
      turnRight(angulo, currentAngle, 'F');
  } else { 
      if(currentAngle < angulo)
        turnRight(angulo, currentAngle, 'F');
      else
        turnLeft(angulo, currentAngle, 'F');
  }
}

/* Legenda de variável "parte":
B: Base
E: Ext1
F: Ext2
G: Gripper
*/
void turnLeft(int angulo, int currentAngle, char parte){
   switch (parte) {
      case 'B':  // Movimento base
                for (int pos = currentAngle; pos >= angulo; pos--) {  
                  servoBase.write(pos);
                  delay(DELAY_SERVO);
                } break;
      case 'E': // Movimento ext1
                for (int pos = currentAngle; pos >= angulo; pos--) {  
                  servoExt1.write(pos);
                  delay(DELAY_SERVO);
                } break;
      case 'F': // Movimento ext2
                for (int pos = currentAngle; pos >= angulo; pos--) {  
                  servoExt2.write(pos);
                  delay(DELAY_SERVO);
                } break;
      case 'G': // Movimento gripper
                for (int pos = currentAngle; pos >= angulo; pos--) {  
                  servoGripper.write(pos);
                  delay(DELAY_SERVO);
                } break;
  } 
}

void turnRight(int angulo, int currentAngle, char parte){
  switch (parte) {
      case 'B':  // Movimento base
                for (int pos = currentAngle; pos <= angulo; pos++) {  
                  servoBase.write(pos);
                  delay(DELAY_SERVO);
                } break;
      case 'E': // Movimento ext1
                for (int pos = currentAngle; pos <= angulo; pos++) {  
                  servoExt1.write(pos);
                  delay(DELAY_SERVO);
                } break;
      case 'F': // Movimento ext2
                for (int pos = currentAngle; pos <= angulo; pos++) {  
                  servoExt2.write(pos);
                  delay(DELAY_SERVO);
                } break;
      case 'G': // Movimento gripper
                for (int pos = currentAngle; pos <= angulo; pos++) {  
                  servoGripper.write(pos);
                  delay(DELAY_SERVO);
                } break;
  }
}

void shutdown(){
  gripper(ANGULO_GRIPPER_DEFAULT);
  ext2Turn(ANGULO_EXT2_DEFAULT);
  ext1Turn(ANGULO_EXT1_DEFAULT);
  baseTurn(ANGULO_BASE_DEFAULT);
  delay(50);
}