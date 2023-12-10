SPEED_MAX = 255
SPEED_MIN = 115
WHEELS_ANGULO_MIN = 45
WHEELS_ANGULO_MAX = 135
WHEELS_ANGULO_DEFAULT = 90
ARM_ANGULO_BASE_MIN = 15
ARM_ANGULO_BASE_MAX = 180
ARM_ANGULO_BASE_DEFAULT = 90
ARM_ANGULO_EXT1_MIN = 30
ARM_ANGULO_EXT1_MAX = 150
ARM_ANGULO_EXT1_DEFAULT = 90
ARM_ANGULO_EXT2_MIN = 30
ARM_ANGULO_EXT2_MAX = 150
ARM_ANGULO_EXT2_DEFAULT = 90
ARM_ANGULO_GRIPPER_OPEN = 70
ARM_ANGULO_GRIPPER_CLOSE = 170
ARM_ANGULO_GRIPPER_DEFAULT = 170
PANTILT_INCLINACAO_DEFAULT = 90
PANTILT_INCLINACAO_MIN = 35
PANTILT_INCLINACAO_MAX = 180
# Rotação base pantilt
PANTILT_BASE = 0
PANTILT_BASE_DIRECAO_HORARIA = 44
PANTILT_BASE_DIRECAO_ANTIHORARIA = 67

import threading

class Rover():
    def __init__(self):
        self.wheels = Wheels()
        self.arm = Arm()
        self.camera = Pantilt()

class Wheels():
    def __init__(self):
        self.lock = threading.Lock()
        self.speed = 0
        self.frontAngle = WHEELS_ANGULO_DEFAULT
        self.backAngle = WHEELS_ANGULO_DEFAULT
        self.speedMin = SPEED_MIN
        self.speedMax = SPEED_MAX
        self.sentido = ""

    def setSpeed(self, vel):
        with self.lock:
            self.speed = vel
            if abs(self.speed) < SPEED_MIN:
                if vel < 0:
                    self.speed = -1 * SPEED_MIN
                else:
                    self.speed = SPEED_MIN
            elif abs(self.speed) > SPEED_MAX:
                if vel < 0:
                    self.speed = -1 * SPEED_MAX
                else:
                    self.speed = SPEED_MAX

    def setFrontAngle(self, angulo):
        with self.lock:
            self.frontAngle = angulo
            if self.frontAngle < WHEELS_ANGULO_MIN:
                self.frontAngle = WHEELS_ANGULO_MIN
            elif self.frontAngle > WHEELS_ANGULO_MAX:
                self.frontAngle = WHEELS_ANGULO_MAX

    def setBackAngle(self, angulo):
        with self.lock:
            self.backAngle = angulo
            if self.backAngle < WHEELS_ANGULO_MIN:
                self.backAngle = WHEELS_ANGULO_MIN
            elif self.backAngle > WHEELS_ANGULO_MAX:
                self.backAngle = WHEELS_ANGULO_MAX

class Arm():
    def __init__(self):
        self.lock = threading.Lock()
        self.base = ARM_ANGULO_BASE_DEFAULT
        self.ext1 = ARM_ANGULO_EXT1_DEFAULT
        self.ext2 = ARM_ANGULO_EXT2_DEFAULT
        self.gripper = ARM_ANGULO_GRIPPER_DEFAULT
        self.gripperClosed = True

        self.ext1Min = ARM_ANGULO_EXT1_MIN
        self.ext1Max = ARM_ANGULO_EXT1_MAX
        self.ext2Min = ARM_ANGULO_EXT2_MIN
        self.ext2Max = ARM_ANGULO_EXT2_MAX
        self.ext1Active = True

    def openCloseGripper(self):
        with self.lock:
            self.gripperClosed = (not self.gripperClosed)
            if self.gripperClosed:
                self.gripper = ARM_ANGULO_GRIPPER_OPEN
            else:
                self.gripper = ARM_ANGULO_GRIPPER_CLOSE

    def setAnguloExt1(self, angulo):
        with self.lock:
            self.ext1 = angulo
            if self.ext1 < ARM_ANGULO_EXT1_MIN:
                self.ext1 = ARM_ANGULO_EXT1_MIN
            elif self.ext1 > ARM_ANGULO_EXT1_MAX:
                self.ext1 = ARM_ANGULO_EXT1_MAX

    def setAnguloExt2(self, angulo):
        with self.lock:
            self.ext2 = angulo
            if self.ext2 < ARM_ANGULO_EXT2_MIN:
                self.ext2 = ARM_ANGULO_EXT2_MIN
            elif self.ext2 > ARM_ANGULO_EXT2_MAX:
                self.ext2 = ARM_ANGULO_EXT2_MAX

    def setBase(self, angulo):
        with self.lock:
            self.base = angulo
            if self.base < ARM_ANGULO_BASE_MIN:
                self.base = ARM_ANGULO_BASE_MIN
            elif self.base > ARM_ANGULO_BASE_MAX:
                self.base = ARM_ANGULO_BASE_MAX


class Pantilt():
    def __init__(self):
        self.lock = threading.Lock()
        self.base = PANTILT_BASE
        self.inclinacao = PANTILT_INCLINACAO_DEFAULT
        self.cam_on = False

    def onOff(self):
        with self.lock:
            self.cam_on = not self.cam_on

    def setInclinacao(self, angulo):
        with self.lock:
            self.inclinacao = angulo
            if self.inclinacao < PANTILT_INCLINACAO_MIN:
                self.inclinacao = PANTILT_INCLINACAO_MIN
            elif self.inclinacao > PANTILT_INCLINACAO_MAX:
                self.inclinacao = PANTILT_INCLINACAO_MAX

    def getInclinacao(self):
        with self.lock:
            return self.inclinacao

    def getBase(self):
        with self.lock:
            return self.base

    def baseSentidoHorario(self):
        with self.lock:
            self.base = PANTILT_BASE_DIRECAO_HORARIA

    def baseSentidoAntihorario(self):
        with self.lock:
            self.base = PANTILT_BASE_DIRECAO_ANTIHORARIA
