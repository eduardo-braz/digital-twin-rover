import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

SERVO_BASE_PORT = 26
SERVO_INCLINACAO_PORT = 19

SERVO_INCLINACAO_DEFAULT = 90
SERVO_INCLINACAO_MIN = 35
SERVO_INCLINACAO_MAX = 140

SERVO_BASE_DIR_HORARIA = 6.73
SERVO_BASE_DIR_ANTIHORARIA = 7.41

DELAY_SERVO = 0.15
DELAY_TIME = 0.005  # 5ms delay

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_BASE_PORT, GPIO.OUT)
GPIO.setup(SERVO_INCLINACAO_PORT, GPIO.OUT)

pwm_base = GPIO.PWM(SERVO_BASE_PORT, 50)
pwm_inclinacao = GPIO.PWM(SERVO_INCLINACAO_PORT, 50)
pwm_base.start(0)
pwm_inclinacao.start(0)

def calc_angle_180(angle):
    return  (2 + (angle / 18))

def calc_pulse_width(speed):
    return (5.5 + (speed / 180.0) * 5)

class Servo():
    def __init__(self, name):
        self.name = name
        if name == "BASE":
            pass

        elif name == "INCLINACAO":
            self.currentAngle = SERVO_INCLINACAO_DEFAULT
            duty_cycle = calc_angle_180(SERVO_INCLINACAO_DEFAULT)
            GPIO.output(SERVO_INCLINACAO_PORT, True)
            pwm_inclinacao.ChangeDutyCycle(duty_cycle)
            time.sleep(DELAY_SERVO)
            GPIO.output(SERVO_INCLINACAO_PORT, False)
            pwm_inclinacao.ChangeDutyCycle(0)
            time.sleep(2)

    # Desligando o PWM e os pinos GPIO
    def shutdown(self):
        if self.name == "INCLINACAO":
            self.inclinar(SERVO_INCLINACAO_DEFAULT)
            pwm_inclinacao.stop()
        else:
            pwm_base.stop()
        GPIO.cleanup()

    def inclinar(self, angle):
        if (angle < SERVO_INCLINACAO_DEFAULT):
            if (self.currentAngle > angle):
                self.set_angle(angle, -1, -5)
            else:
                self.set_angle(angle, 1, 5)
        else:
            if (self.currentAngle < angle):
                self.set_angle(angle, 1, 5)
            else:
                self.set_angle(angle, -1, -5)
        self.currentAngle = angle

    def set_angle(self, angle, dif, passo):
        if self.name == "INCLINACAO":
            for i in range(self.currentAngle, angle + dif, passo):
                duty_cycle = calc_angle_180(i)
                GPIO.output(SERVO_INCLINACAO_PORT, True)
                pwm_inclinacao.ChangeDutyCycle(duty_cycle)
                time.sleep(DELAY_SERVO)
                GPIO.output(SERVO_INCLINACAO_PORT, False)
                pwm_inclinacao.ChangeDutyCycle(0)
            mod = angle % 5
            if (mod != 0):
                duty_cycle = calc_angle_180(i)
                GPIO.output(SERVO_INCLINACAO_PORT, True)
                pwm_inclinacao.ChangeDutyCycle(duty_cycle)
                time.sleep(DELAY_SERVO)
                GPIO.output(SERVO_INCLINACAO_PORT, False)
                pwm_inclinacao.ChangeDutyCycle(0)

    def get_angle(self):
        if self.name == "INCLINACAO":
            return self.currentAngle

    def base_turn(self, speed):
        if self.name == "BASE":
            if speed == 44:
                pulse_width = SERVO_BASE_DIR_HORARIA
            else:
                pulse_width = SERVO_BASE_DIR_ANTIHORARIA
            GPIO.output(SERVO_BASE_PORT, True)
            pwm_base.ChangeDutyCycle(pulse_width)
            time.sleep(DELAY_SERVO)
            GPIO.output(SERVO_BASE_PORT, False)
            pwm_base.ChangeDutyCycle(0)
