'''  MAPEAMENTO DOS BOTÕES JOYSTICK
* Pantilt: Analógico esquerdo, eixo X para controle servo 360 e Y para inclinação
* Rodas: Direcional UP/ Down para controlar velocidade dos motores e Left / Righ para 
fazer curvas. OBS.: Se botão central analógico esquerdo estiver pressionado, 
girar servo motores traseiros.
* Select: Desliga rover, pára todos os motores e retorna servo para posições iniciais.
* Start: ON/OFF cãmera
* Botões 0 a 3: Controle ARM:
 - 0 e 2 - PENDENTE: Movem ext1 e ext2 para frente / trás
    -- L1 ativa ext1 ou ext2 (Se True, ativa ext1, senão, ext2)
 - 1 e 3: Giram base horizontalmente
 - Botão central analógico direito OPEN / CLOSE garra
 Default: Garra fechada, L1 true
----------------------------------------------------------
Botão físico | Número botão 
Y(Triangulo) = 0
B(Bolinha) = 1
A(Quadrado) = 2
X(Triangulo) = 3
L1 = 4
R1 = 5
L2 = 6
R2 = 7
SELECT = 8
START = 9

UP: Dispara eventos do tipo JOYHATMOTION, uma tupla (0, 1)
DOWN: Dispara eventos do tipo JOYHATMOTION, uma tupla (0, -1)
LEFT: Dispara eventos do tipo JOYHATMOTION, uma tupla (-1, 0)
RIGHT: Dispara eventos do tipo JOYHATMOTION, uma tupla (1, 0)

Analogico esquerdo: Dispara uma série de eventos do tipo JOYAXISMOTION
Botão central analógico esquerdo  = 10

Analogico direito:
Botão central analógico direito  = 11
'''

# Ajuste incremento de angulos
FIT_PANTILT = 10
FIT_WHEEL_ANGLE = 10
FIT_WHEEL_SPEED = 5
FIT_BASE_ARM = 10
FIT_EXT_ARM = 5

#Valores para map_value Coppelia e Rover físico
ANGULO_BASE_MIN = 0
ANGULO_BASE_MAX = 165
ANGULO_BASE_DEFAULT = 90
ANGULO_BASE_COPPELIA_MIN = 15
ANGULO_BASE_COPPELIA_MAX = 180
ANGULO_BASE_COPPELIA_DEFAULT = 90

ANGULO_EXT1_MIN = 30
ANGULO_EXT1_MAX = 150
ANGULO_EXT1_DEFAULT = 30
ANGULO_EXT1_COPPELIA_MIN = -30
ANGULO_EXT1_COPPELIA_MAX = 90
ANGULO_EXT1_COPPELIA_DEFAULT = -30

ANGULO_EXT2_MIN = 30
ANGULO_EXT2_MAX = 100
ANGULO_EXT2_DEFAULT = 100
ANGULO_EXT2_COPPELIA_MIN = -100
ANGULO_EXT2_COPPELIA_MAX = 0
ANGULO_EXT2_COPPELIA_DEFAULT = 0

ANGULO_GRIPPER_MIN = 70
ANGULO_GRIPPER_MAX = 170
ANGULO_GRIPPER_DEFAULT = 170
ANGULO_GRIPPER_COPPELIA_MIN = 0
ANGULO_GRIPPER_COPPELIA_MAX = 70
ANGULO_GRIPPER_COPPELIA_DEFAULT = 0

ANGULO_INCLINACAO_MIN = 35
ANGULO_INCLINACAO_MAX = 140
ANGULO_INCLINACAO_DEFAULT = 90
ANGULO_INCLINACAO_COPPELIA_MIN = 35
ANGULO_INCLINACAO_COPPELIA_MAX = 140
ANGULO_INCLINACAO_COPPELIA_DEFAULT = 90

ANGULO_BRACKET_DEFAULT = 90
ANGULO_BRACKET_MIN = 45
ANGULO_BRACKET_MAX = 135
ANGULO_BRACKET_COPPELIA_DEFAULT = 0
ANGULO_BRACKET_COPPELIA_MIN = -45
ANGULO_BRACKET_COPPELIA_MAX = 45

topicoComum = {
    "publish": "/rover/comum",
    "listener": "/middle/comum",
    "qos": 0
}
topicoEmergencial = {
    "publish": "/rover/emergencia",
    "listener": "/middle/emergencia",
    "qos": 2
}

topicoCamera = {
    "publish": "/cam",
    "listener": "/cam",
    "qos": 0
}
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from mqtt import Mqtt
from RoverClass import Rover
import time
import pygame
from MessageMqtt import Message
import json
import MessageBatteryCharge as BatteryCharge
import CoppeliaIntegration.Rover_Coppelia_Integration as RoverCoppelia
import threading
import multiprocessing
from front import display

roverCoppelia = RoverCoppelia.RoverCoppelia()
rover = Rover()
mqtt = Mqtt()
pygame.joystick.init()
joystck = pygame.joystick.Joystick(0)  # Captura Joystick conectado na porta '/dev/input/js0'

batteryRaspberry = BatteryCharge.MessageBatteryCharge("Raspberry", -1)
batteryWheels = BatteryCharge.MessageBatteryCharge("Wheels", -1)
batteryArm = BatteryCharge.MessageBatteryCharge("Arm", -1)
batteryCamera = BatteryCharge.MessageBatteryCharge("Camera", -1)

backTurn = False
message = Message('', '')
criticalBattery = False

mqtt_thread = threading.Thread(target=mqtt.publish)

battery_queue = {
        "battery_cam": multiprocessing.Queue(),
        "battery_arm": multiprocessing.Queue(),
        "battery_movement": multiprocessing.Queue(),
        "battery_raspberry": multiprocessing.Queue()
    }

arm_queue = {
    "base_value": multiprocessing.Queue(),
    "ext1_value": multiprocessing.Queue(),
    "ext2_value": multiprocessing.Queue(),
    "gripper_close_value": multiprocessing.Queue()
}

arduino_queue = {
    "velocity_wheels": multiprocessing.Queue(),
    "angle_front": multiprocessing.Queue(),
    "angle_back": multiprocessing.Queue()
}

def triggerMqttThread(message):
    global mqtt_thread
    if not mqtt_thread.is_alive():
        mqtt_thread = threading.Thread(target=mqtt.publish, args=(topicoComum['publish'], message, topicoComum['qos'],))
    else:
        mqtt_thread.join()
        mqtt_thread = threading.Thread(target=mqtt.publish, args=(topicoComum['publish'], message, topicoComum['qos'],))
    mqtt_thread.start()

def armControl(button):
    global rover
    global roverCoppelia
    message = Message("ESP32", "")

    if rover.arm.ext1Active:
        if button == 0:  # Avança braço Ext1
            angulo = rover.arm.ext1 + FIT_EXT_ARM
            rover.arm.setAnguloExt1(angulo)
            message.comando = "E" + str(rover.arm.ext1)
        else: # Recua braço Ext1
            angulo = rover.arm.ext1 - FIT_EXT_ARM
            rover.arm.setAnguloExt1(angulo)
            message.comando = "E" + str(rover.arm.ext1)
        mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
        roverCoppelia.ext1Arm(
            map_value(angulo, ANGULO_EXT1_MIN, ANGULO_EXT1_MAX, ANGULO_EXT1_COPPELIA_MIN, ANGULO_EXT1_COPPELIA_MAX))
        arm_queue['ext1_value'].put_nowait(rover.arm.ext1)
    else:
        if button == 0:  # Avança braço Ext2
            angulo = rover.arm.ext2 + FIT_EXT_ARM
            rover.arm.setAnguloExt2(angulo)
            message.comando = "F" + str(rover.arm.ext2)
        else:  # Recua braço Ext2
            angulo = rover.arm.ext2 - FIT_EXT_ARM
            rover.arm.setAnguloExt2(angulo)
            message.comando = "F" + str(rover.arm.ext2)
        mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
        roverCoppelia.ext2Arm(
            map_value(angulo, ANGULO_EXT2_MIN, ANGULO_EXT2_MAX, ANGULO_EXT2_COPPELIA_MIN, ANGULO_EXT2_COPPELIA_MAX))
        arm_queue['ext2_value'].put_nowait(rover.arm.ext2)

    time.sleep(1)
def shutdownRover():
    global rover
    global roverCoppelia
    message = Message("Todos", "S")
    mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
    time.sleep(1)

    roverCoppelia.stopMove()
    roverCoppelia.posSequenceMove()

    rover = Rover()

def gripperClosed():
    global rover
    global roverCoppelia
    global mqtt_thread
    print(f"Log: CapturaJoystick. Gripper closed: {rover.arm.gripperClosed}")
    rover.arm.openCloseGripper()
    message = Message("ESP32", ("G" + str(rover.arm.gripper)))
    print(f"Log: CapturaJoystick. Gripper closed: {rover.arm.gripperClosed}")
    if rover.arm.gripperClosed:
        triggerMqttThread(message)
        roverCoppelia.open_gripper() if roverCoppelia.coppeliaConnected else None
    else:
        triggerMqttThread(message)
        roverCoppelia.close_gripper() if roverCoppelia.coppeliaConnected else None
    arm_queue['gripper_close_value'].put_nowait(rover.arm.gripperClosed)
    mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
    time.sleep(1)

def turnBaseArm(angulo):
    global rover
    global roverCoppelia
    angulo = rover.arm.base + (angulo * FIT_BASE_ARM)
    rover.arm.setBase(angulo)
    message = Message("ESP32", ("B" + str(rover.arm.base)))
    triggerMqttThread(message)
    roverCoppelia.turnArm(angulo) if roverCoppelia.coppeliaConnected else None
    arm_queue['base_value'].put_nowait(rover.arm.base)
    mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
    time.sleep(1)

def turnBasePantilt(sentido):
    global rover
    global roverCoppelia
    if (int(sentido) == 1):
        rover.camera.baseSentidoHorario()
    else:
        rover.camera.baseSentidoAntihorario()
    message = Message("Raspberry", ("B" + str(rover.camera.base)))
    roverCoppelia.turnCamera(rover.camera.base)
    mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
    time.sleep(1)

def inclinacaoPantilt(angulo):
    global rover
    global roverCoppelia
    angulo = rover.camera.inclinacao + int(angulo * FIT_PANTILT)
    rover.camera.setInclinacao(angulo)
    roverCoppelia.inclineCamera(angulo)
    message = Message("Raspberry", ("I" + str(rover.camera.inclinacao)))
    mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
    time.sleep(1)

def validaAnguloCoppelia(angulo, prefixo):
    global rover
    global roverCoppelia
    if prefixo == 'A':
        angulo = roverCoppelia.front_bracket_current_angle + (angulo * FIT_WHEEL_ANGLE)
    else:
        angulo = roverCoppelia.back_bracket_current_angle + (angulo * FIT_WHEEL_ANGLE)

    if angulo <= ANGULO_BRACKET_COPPELIA_MIN:
        return ANGULO_BRACKET_COPPELIA_MIN
    elif angulo >= ANGULO_BRACKET_COPPELIA_MAX:
        return ANGULO_BRACKET_COPPELIA_MAX
    else:
        return angulo

def validaAngulo(angulo, prefixo):
    global rover
    if prefixo == 'A':
        angulo = rover.wheels.frontAngle + (angulo * FIT_WHEEL_ANGLE)
    else:
        angulo = rover.wheels.backAngle + (angulo * FIT_WHEEL_ANGLE)

    if angulo <= ANGULO_BRACKET_MIN:
        return ANGULO_BRACKET_MIN
    elif angulo >= ANGULO_BRACKET_MAX:
        return ANGULO_BRACKET_MAX
    else:
        return angulo
def turnWheels(prefixo, angulo):
    global rover
    global roverCoppelia
    message = Message("Arduino", "")
    # Gira rodas
    if prefixo == 'A':
        current_angle = rover.wheels.frontAngle
        anguloCoppelia = validaAnguloCoppelia(angulo, prefixo)
        angulo = validaAngulo(angulo, prefixo)
        if current_angle != angulo:
            rover.wheels.setFrontAngle(angulo)
            message.comando = (prefixo + str(rover.wheels.frontAngle))
            if roverCoppelia.wheel_vel > 0:
                roverCoppelia.stopMove()
            mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
            roverCoppelia.frontTurn(anguloCoppelia)
            rover.wheels.frontAngle = angulo
            arduino_queue["angle_front"].put_nowait(rover.wheels.frontAngle)
    elif prefixo == 'Z':
        current_angle = rover.wheels.backAngle
        print(f'Log: CapturaJoystick. current_angle traseiro {current_angle}')
        angulo = validaAngulo(angulo, prefixo)
        anguloCoppelia = validaAnguloCoppelia(angulo, prefixo)
        print(f'Log: CapturaJoystick. Angulo traseiro {angulo}')
        if current_angle != angulo:
            rover.wheels.setBackAngle(angulo)
            message.comando = (prefixo + str(rover.wheels.backAngle))
            if roverCoppelia.wheel_vel > 0:
                roverCoppelia.stopMove()
            mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
            roverCoppelia.backTurn(anguloCoppelia)
            rover.wheels.backAngle = angulo
            arduino_queue["angle_back"].put_nowait(rover.wheels.backAngle)
    time.sleep(3)

def speed(sentido):
    global rover
    global roverCoppelia
    print(f"Log: CapturaJoystick. Velocidade inicial: {rover.wheels.speed}")
    speed = 0
    message = Message("Arduino", "")
    if sentido == 1: #Aumenta velocidade
        if rover.wheels.speed == ( -1 * rover.wheels.speedMin ):
            message.comando = "S"
            rover.wheels.speed = 0
            rover.wheels.sentido = ""
            roverCoppelia.stopMove()
            mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
            time.sleep(1)
            return
        elif (rover.wheels.speed == 0):
            rover.wheels.sentido = "F"
            speed = rover.wheels.speedMin
            roverCoppelia.wheel_vel = speed
            roverCoppelia.moveForward()

        elif rover.wheels.speed >= rover.wheels.speedMin and rover.wheels.speed < rover.wheels.speedMax:
            rover.wheels.sentido = "F"
            speed = rover.wheels.speed + (sentido * FIT_WHEEL_SPEED)
            roverCoppelia.wheel_vel = abs(speed)
            roverCoppelia.moveForward()

        elif (rover.wheels.speed >= (-1*rover.wheels.speedMax) and rover.wheels.speed < 0):
            rover.wheels.sentido = "B"
            speed = rover.wheels.speed + (sentido * FIT_WHEEL_SPEED)
            roverCoppelia.wheel_vel = abs(speed)
            roverCoppelia.moveBackward()

    else: #Diminui velocidade
        if rover.wheels.speed == rover.wheels.speedMin:
            message.comando = "S"
            rover.wheels.speed = 0
            rover.wheels.sentido = ""
            mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
            roverCoppelia.stopMove()
            time.sleep(1)
            return

        elif (rover.wheels.speed == 0):
            rover.wheels.sentido = "B"
            speed = -1 * rover.wheels.speedMin
            roverCoppelia.wheel_vel = abs(speed)
            roverCoppelia.moveBackward()

        elif (rover.wheels.speed <= (-1 * rover.wheels.speedMin) and rover.wheels.speed > (-1 * rover.wheels.speedMax) ):
            rover.wheels.sentido = "B"
            speed = rover.wheels.speed + (sentido * FIT_WHEEL_SPEED)
            roverCoppelia.wheel_vel = abs(speed)
            roverCoppelia.moveBackward()

        elif (rover.wheels.speed <= rover.wheels.speedMax and rover.wheels.speed > 0):
            rover.wheels.sentido = "F"
            speed = rover.wheels.speed + (sentido * FIT_WHEEL_SPEED)
            roverCoppelia.wheel_vel = abs(speed)
            roverCoppelia.moveForward()
    rover.wheels.setSpeed(speed)
    message.comando = rover.wheels.sentido + str(abs(rover.wheels.speed))
    mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
    arduino_queue["velocity_wheels"].put_nowait(rover.wheels.speed)
    print(f"Log: CapturaJoystick. Velocidade final: {rover.wheels.speed}")
    time.sleep(1)

def cameraOnOff():
    global rover
    global roverCoppelia
    print(f"Log: CapturaJoystick. Camera: {rover.camera.cam_on}")
    rover.camera.onOff()
    message = ""
    if rover.camera.cam_on:
        message = json.dumps("L")
    else:
        message = json.dumps("D")

    mqtt.publishCamera(topicoCamera['publish'], message[1], topicoCamera['qos'])
    time.sleep(1)

def start_display(battery_queue, arm_queue, arduino_queue):
    display.main_window(battery_queue, arm_queue, arduino_queue)

def start():
    global criticalBattery
    global roverCoppelia
    pygame.init()
    '''  Ouve mensagem MQTT sinalizando a inicialização do Raspberry   '''
    print(f'Log: CapturaJoystick. Aguardando comunicação com Raspberry ', end='')
    while True:
        print(f'.', end='')
        mqtt.subscribe(topicoComum['listener'], topicoComum['qos'])
        time.sleep(1)
        if ((mqtt.payload != None) and (mqtt.payload.comando == "OK")):
            print("Log: CapturaJoystick. Conectado ao Raspberry")
            mqtt.payload = None
            mqtt.unsubscribe(topicoComum['listener'])
            break
    print(f'Log: CapturaJoystick. Leitura de baterias ', end='')
    while True:
        print(f'.', end='')
        mqtt.subscribe(topicoComum['listener'], topicoComum['qos'])
        time.sleep(1)
        if ((mqtt.payload != None) and (mqtt.payload.device != None)):
            setBaterry(mqtt.payload)
            while -1 in [batteryRaspberry.value, batteryWheels.value, batteryArm.value, batteryCamera.value]:
                if ((mqtt.payload != None) and (mqtt.payload.device != None)):
                    setBaterry(mqtt.payload)
            else:
                mqtt.unsubscribe(topicoComum['listener'])
                break
            break

    print(f'Log: CapturaJoystick. Bateria Raspberry {batteryRaspberry.value}%')
    print(f'Log: CapturaJoystick. Bateria Arduino {batteryWheels.value}%')
    print(f'Log: CapturaJoystick. Bateria Arm {batteryArm.value}%')
    print(f'Log: CapturaJoystick. Bateria Camera {batteryCamera.value}%')

    cameraOnOff()
    verifyCriticalBattery()
    if criticalBattery:
        sys.exit(1)

    # Verifica se existe comunicação com Coppelia
    if not roverCoppelia.coppeliaConnected:
        sys.exit(1)

    display_process = multiprocessing.Process(target=start_display, args=(battery_queue, arm_queue, arduino_queue,))
    display_process.start()


def setBaterry(payload):
    if payload.device == 'C1':
        batteryRaspberry.setValue(payload.value)
        battery_queue['battery_raspberry'].put_nowait(batteryRaspberry.value)
    elif payload.device == 'C2':
        batteryWheels.setValue(payload.value)
        battery_queue['battery_movement'].put_nowait(batteryWheels.value)
    elif payload.device == 'C3':
        batteryArm.setValue(payload.value)
        battery_queue['battery_arm'].put_nowait(batteryArm.value)
    elif payload.device == 'C4':
        batteryCamera.setValue(payload.value)
        battery_queue['battery_cam'].put_nowait(batteryCamera.value)

def verifyCriticalBattery():
    global criticalBattery
    baterias = [batteryRaspberry, batteryWheels, batteryArm, batteryCamera]
    for bateria in baterias:
        if bateria.value <= 5:
            criticalBattery = True
            print(f"Log: CapturaJoystick. Bateria de {bateria.device} em nível crítico.")

def map_value(currentValue, from_min, from_max, to_min, to_max):
    return (currentValue - from_min) * (to_max - to_min) / (from_max - from_min) + to_min
def captureEvents():
    global rover
    global message
    global backTurn

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break
        if event.type == pygame.JOYBUTTONDOWN:  #Captura os botões presionados do joystick
            if event.button == 0: # Avança Ext1 ou Ext2
                armControl(event.button)
            elif event.button == 1: # Girar base ARM horizontalmente
                turnBaseArm(1)
            elif event.button == 2: # Recua Ext1 ou Ext2
                armControl(event.button)
            elif event.button == 3: # Girar base ARM horizontalmente
                turnBaseArm(-1)
            elif event.button == 4: # Ativa movimentos ext1
                rover.arm.ext1Active = not rover.arm.ext1Active
            elif event.button == 8: # Select: Desliga rover, pára todos os motores e retorna servo para posições iniciais.
                shutdownRover()
            elif event.button == 9: # Start: ON/OFF câmera
                cameraOnOff()
            elif event.button == 10: # Botão central analógico esquerdo
                backTurn = not backTurn
            elif event.button == 11: # Botão central analógico direito | Abre/fecha garra gripper
                gripperClosed()

        if (event.type == pygame.JOYHATMOTION and event.dict.get('value') != (0, 0)):
            ''' Rodas: Direcional UP/ Down para controlar velocidade dos motores e Left / Righ para fazer curvas. 
            OBS.: Se botão central analógico esquerdo for pressionado, girar servo motores traseiros. '''

            if ((event.dict.get('value')[0] == -1) or (event.dict.get('value')[0] == 1)): # Left or Right
                if backTurn is False:
                    turnWheels('A', event.dict.get('value')[0]) # Gira para esquerda com rodas frontais
                else:
                    turnWheels('Z', event.dict.get('value')[0]) # Gira para esquerda com rodas traseiras
            elif ((event.dict.get('value')[1] == 1) or (event.dict.get('value')[1] == -1)): # Up
                speed(event.dict.get('value')[1])    # Aumenta ou Dimimui velocidade rodas

        if event.type == pygame.JOYAXISMOTION:
            if abs(event.value) >= 1.0:
                if event.axis == 0: # Analogico esquerdo, eixo X
                    turnBasePantilt(event.value) # Pantilt base
                elif event.axis == 1:  # Analogico esquerdo, eixo Y
                    inclinacaoPantilt(event.value) # Pantilt inclinação
