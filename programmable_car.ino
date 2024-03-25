#include <SoftwareSerial.h>
#include <Servo.h>

SoftwareSerial bluetoothSerial(0, 1); // RX | TX
#define MOTOR_LEFT_PWM_PIN 6
#define MOTOR_LEFT_DIR_PIN1 7
#define MOTOR_LEFT_DIR_PIN2 8
#define MOTOR_RIGHT_PWM_PIN 9
#define MOTOR_RIGHT_DIR_PIN1 10
#define MOTOR_RIGHT_DIR_PIN2 11

#define CMD_FORWARD 'F'
#define CMD_BACKWARD 'B'
#define CMD_TURN_RIGHT 'R'
#define CMD_TURN_LEFT 'L'
#define MOVE_SPEED 150
#define MOVE_TIME_INTERVAL 1000

enum State {
  IDLE,
  MOVING,
  TURNING
};

State currentState = IDLE;

void setup() {
  pinMode(MOTOR_LEFT_PWM_PIN, OUTPUT);
  pinMode(MOTOR_LEFT_DIR_PIN1, OUTPUT);
  pinMode(MOTOR_LEFT_DIR_PIN2, OUTPUT);
  pinMode(MOTOR_RIGHT_PWM_PIN, OUTPUT);
  pinMode(MOTOR_RIGHT_DIR_PIN1, OUTPUT);
  pinMode(MOTOR_RIGHT_DIR_PIN2, OUTPUT);

  bluetoothSerial.begin(9600);

  Serial.println("Bluetooth Control Car");
}

void loop()
{
  if (bluetoothSerial.available())
  {
    char command = bluetoothSerial.read();
    switch (command)
    {
      case CMD_FORWARD:
        move(MOVE_SPEED, MOVE_TIME_INTERVAL);
        break;
      case CMD_BACKWARD:
        move(-MOVE_SPEED, MOVE_TIME_INTERVAL);
        break;
      case CMD_TURN_RIGHT:
        turnRight();
        break;
      case CMD_TURN_LEFT:
        turnLeft();
        break;
    }
  }
}

void move(int speed, int duration)
{
  currentState = MOVING;
  unsigned long startTime = millis();
  while (millis() - startTime < duration) {
    driveMotors(speed);
    delay(100); // Adjust as needed
    if (currentState == IDLE) {
      stopMotors();
      return;
    }
  }
  stopMotors();
  currentState = IDLE;
}

void turnLeft()
{
  currentState = TURNING;
  analogWrite(MOTOR_LEFT_PWM_PIN, 20);
  analogWrite(MOTOR_RIGHT_PWM_PIN, MOVE_SPEED);
  handleDirection(MOVE_SPEED);
  delay(575);
  stopMotors();
  currentState = IDLE;
}

void turnRight()
{
  currentState = TURNING;
  analogWrite(MOTOR_RIGHT_PWM_PIN, 20);
  analogWrite(MOTOR_LEFT_PWM_PIN, MOVE_SPEED);
  handleDirection(MOVE_SPEED);
  delay(575);
  stopMotors();
  currentState = IDLE;
}

void stopMotors()
{
  digitalWrite(MOTOR_LEFT_PWM_PIN, LOW);
  digitalWrite(MOTOR_RIGHT_PWM_PIN, LOW);
}

void driveMotors(int speed)
{
  analogWrite(MOTOR_LEFT_PWM_PIN, abs(speed));
  analogWrite(MOTOR_RIGHT_PWM_PIN, abs(speed));
  handleDirection(speed);
}

void handleDirection(int speed)
{
  if (speed > 0) {
    digitalWrite(MOTOR_LEFT_DIR_PIN1, HIGH);
    digitalWrite(MOTOR_RIGHT_DIR_PIN1, HIGH);
    digitalWrite(MOTOR_LEFT_DIR_PIN2, LOW);
    digitalWrite(MOTOR_RIGHT_DIR_PIN2, LOW);
  } else {
    digitalWrite(MOTOR_LEFT_DIR_PIN1, LOW);
    digitalWrite(MOTOR_RIGHT_DIR_PIN1, LOW);
    digitalWrite(MOTOR_LEFT_DIR_PIN2, HIGH);
    digitalWrite(MOTOR_RIGHT_DIR_PIN2, HIGH);

  }
}