import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
import sim
import msgpack
import math
import time
import random

rover_port = 19997
address = '127.0.0.1'

clientID = -1
clientId_executed = 'no data to read'  # Nome inicial do sinal
Handler = 'base_link_respondable'  # Nome do objeto no coppelia
Signal_name = 'base_link_Executado'
object_handle = None

SPEED_MAX = 255
SPEED_MAX_COPPELIA = 180

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

def waitExecutionMoves(signal_to_wait):
    global clientId_executed
    global Signal_name

    print(f"Log: CoppeliaIntegration. Aguardando execução de comando {signal_to_wait} ", end='')
    while clientId_executed != signal_to_wait:
        time.sleep(0.5)
        print(".", end='')
        retCode, s = sim.simxGetStringSignal(clientID, Signal_name, sim.simx_opmode_buffer)
        if retCode == sim.simx_return_ok:
            if type(s) == bytearray:
                s = s.decode('ascii')
            clientId_executed = s
    print("")

class RoverCoppelia:
    def __init__(self):
        self.distance = 0
        self.global_position = [0.0, 0.0, 0.0]
        self.wheel_vel = 0
        self.front_bracket_current_angle = ANGULO_BRACKET_COPPELIA_DEFAULT
        self.back_bracket_current_angle = ANGULO_BRACKET_COPPELIA_DEFAULT
        self.incline_pantilt = ANGULO_INCLINACAO_DEFAULT
        self.rotation_pantilt = 0
        self.rotation_arm = ANGULO_BASE_COPPELIA_DEFAULT
        self.ext1_arm = 30
        self.ext2_arm = 100
        self.gripper_close = True
        self.coppeliaConnected = False

        global clientID
        sim.simxFinish(-1)  # Fecha todas as conexões
        clientID = sim.simxStart(address, rover_port, True,
                                 True, 5000, 5)  # Conecta ao CoppeliaSim
        time.sleep(1)
        if clientID != -1:
            # Inscreve o sinal recebido do servidor
            sim.simxGetStringSignal(clientID, Signal_name, sim.simx_opmode_streaming)
            sim.simxStartSimulation(clientID, sim.simx_opmode_blocking)
            waitExecutionMoves('signal_rover')
            self.coppeliaConnected = True

    def posSequenceMove(self):
        global Signal_name
        global clientID
        sim.simxStopSimulation(clientID, sim.simx_opmode_blocking)
        sim.simxGetStringSignal(clientID, Signal_name, sim.simx_opmode_discontinue)
        sim.simxGetPingTime(clientID)
        sim.simxFinish(clientID)

    def moveForward(self):
        if clientID != -1:
            self.wheel_vel = self.map_value(self.wheel_vel, 0, SPEED_MAX, 0, SPEED_MAX_COPPELIA)
            if self.front_bracket_current_angle != ANGULO_BRACKET_COPPELIA_DEFAULT:
                Data = [self.wheel_vel,  # Roda esquerda frontal
                          -self.wheel_vel,  # Roda direita frontal
                          self.wheel_vel,  # Roda esquerda meio
                          -self.wheel_vel,  # Roda direita meio
                          self.wheel_vel/2,  # Roda esquerda traseira
                          -self.wheel_vel/2]  # Roda direita traseira
            else:
                Data = [self.wheel_vel,  # Roda esquerda frontal
                        -self.wheel_vel,  # Roda direita frontal
                        self.wheel_vel,  # Roda esquerda meio
                        -self.wheel_vel,  # Roda direita meio
                        self.wheel_vel,  # Roda esquerda traseira
                        -self.wheel_vel]  # Roda direita traseira

            self.move(Data)
        else:
            print(f'Log: CoppeliaIntegration. Falha ao conectar-se ao Coppelia!!!')

    def getDistanceAndPosition(self):
        global distance
        result, object_handle = sim.simxGetObjectHandle(clientID, Handler, sim.simx_opmode_blocking)
        if result == 0:
            result, current_position = sim.simxGetObjectPosition(clientID, object_handle, -1, sim.simx_opmode_blocking)
            if result == 0:
                # Calcule a diferença entre a posição atual e a posição inicial
                x_diff = current_position[0] - self.global_position[0]
                y_diff = current_position[1] - self.global_position[1]
                self.global_position[0] = x_diff
                self.global_position[1] = y_diff
                self.distance = self.distance + math.sqrt(x_diff ** 2 + y_diff ** 2)
                print(f"Log: CoppeliaIntegration. Distancia: {self.distance:.3f}m")

    def moveBackward(self):
        if clientID != -1:
            self.wheel_vel = self.map_value(self.wheel_vel, 0, SPEED_MAX, 0, SPEED_MAX_COPPELIA)
            if self.front_bracket_current_angle != ANGULO_BRACKET_COPPELIA_DEFAULT:
                Data = [self.wheel_vel/2,  # Roda esquerda frontal
                          self.wheel_vel/2,  # Roda direita frontal
                          -self.wheel_vel,  # Roda esquerda meio
                          self.wheel_vel,  # Roda direita meio
                          -self.wheel_vel,  # Roda esquerda traseira
                          self.wheel_vel]  # Roda direita traseira
            else:
                Data = [self.wheel_vel,  # Roda esquerda frontal
                          self.wheel_vel,  # Roda direita frontal
                          -self.wheel_vel,  # Roda esquerda meio
                          self.wheel_vel,  # Roda direita meio
                          -self.wheel_vel,  # Roda esquerda traseira
                          self.wheel_vel]  # Roda direita traseira

            self.move(Data)
        else:
            print(f'Log: CoppeliaIntegration. Fail to connect!!!')

    def move(self, Data):
        id = "Move" + str(random.randint(0, 30))
        data_pack = msgpack.packb({"id": id, "type": "move", "Data": Data})
        inicio = time.time()
        sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'data_to_moviment',
                                   [], [], [], data_pack, sim.simx_opmode_oneshot)
        sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'execute_moviment',
                                   [], [], [], id, sim.simx_opmode_oneshot)
        # Aguarda até que a sequência de movimento acima termine a execução
        waitExecutionMoves(id)
        fim = time.time()
        print(f"Log: CoppeliaIntegration. Tempo de execução de {id}: {(fim - inicio):.2f} segundos")

    def frontTurn(self, angle):
        if clientID != -1:
            #print(f'Log: CoppeliaIntegration. Angulo antes do mapeamento: {angle}')
            #angle = self.map_value(angle, ANGULO_BRACKET_MIN, ANGULO_BRACKET_MAX, ANGULO_BRACKET_COPPELIA_MIN, ANGULO_BRACKET_COPPELIA_MAX)
            print(f'Log: CoppeliaIntegration. Angulo enviado: {angle}')
            self.front_bracket_current_angle = angle
            Data = [angle,  # Direita frontal
                    angle, # Esquerda frontal
                      0, 0]
            data_pack = msgpack.packb({"id": "Turn", "type": "turn", "Data": Data})
            self.turn(data_pack)
        else:
            print(f'Log: CoppeliaIntegration. Fail to connect!!!')

    def backTurn(self, angle):
        if clientID != -1:
            self.back_bracket_current_angle = angle
            Data = [0, 0,
                    angle,  # Direita frontal
                    angle] # Esquerda frontal
            data_pack = msgpack.packb({"id": "Turn", "type": "turn", "Data": Data})
            self.turn(data_pack)
        else:
            print(f'Log: CoppeliaIntegration. Fail to connect!!!')
    def turn(self, data_pack):
        sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'data_to_moviment', [],
                                   [], [], data_pack, sim.simx_opmode_oneshot)
        sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'execute_moviment',
                                   [], [], [], 'Turn', sim.simx_opmode_oneshot)
        waitExecutionMoves('Turn')

    def stopMove(self):
        if clientID != -1:
            id = "stop_move"
            data_pack = msgpack.packb({"id": id, "type": "stop_move"})
            inicio = time.time()
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'data_to_moviment',
                                       [], [], [], data_pack, sim.simx_opmode_oneshot)
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'execute_moviment',
                                       [], [], [], id, sim.simx_opmode_oneshot)
            # Aguarda até que a sequência de movimento acima termine a execução
            waitExecutionMoves(id)
            fim = time.time()
            print(f"Log: CoppeliaIntegration. Tempo de execução de {id}: {(fim - inicio):.2f} segundos")
        else:
            print(f'Log: CoppeliaIntegration. Fail to connect!!!')

    def turnCamera(self, sentido):
        if clientID != -1:
            if sentido == 44:
                angleRad = self.rotation_pantilt+30 #math.radians(self.rotation_pantilt+30)
                self.rotation_pantilt += 30
            else:
                angleRad = self.rotation_pantilt-30 #math.radians(self.rotation_pantilt-30)
                self.rotation_pantilt -= 30
            id = "rotation_pantilt" + str(random.randint(0, 10))
            data_pack = msgpack.packb({"id": id, "type": "rotation_pantilt", "Data": angleRad})
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'data_to_moviment',
                                       [], [], [], data_pack, sim.simx_opmode_oneshot)
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'execute_moviment',
                                       [], [], [], id, sim.simx_opmode_oneshot)
            waitExecutionMoves(id)
        else:
            print(f'Log: CoppeliaIntegration. Fail to connect!!!')

    def inclineCamera(self, angle):
        if clientID != -1:
            angle = self.map_value(angle, ANGULO_INCLINACAO_MIN, ANGULO_INCLINACAO_MAX, ANGULO_INCLINACAO_COPPELIA_MIN, ANGULO_INCLINACAO_COPPELIA_MAX)
            self.rotation_pantilt = angle
            id = "incline_pantilt" + str(random.randint(0, 10))
            data_pack = msgpack.packb({"id": id, "type": "incline_pantilt", "Data": angle})
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'data_to_moviment',
                                       [], [], [], data_pack, sim.simx_opmode_oneshot)
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'execute_moviment',
                                       [], [], [], id, sim.simx_opmode_oneshot)
            waitExecutionMoves(id)
        else:
            print(f'Log: CoppeliaIntegration. Fail to connect!!!')

    def armFunctions(self, angle, type):
        if clientID != -1:
            print(f"Log: CoppeliaIntegration. Angulo enviado: {angle}")
            id = type + str(random.randint(0, 10))
            data_pack = msgpack.packb({"id": id, "type": type, "Data": angle})
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'data_to_moviment',
                                       [], [], [], data_pack, sim.simx_opmode_oneshot)
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'execute_moviment',
                                       [], [], [], id, sim.simx_opmode_oneshot)
        else:
            print(f'Log: CoppeliaIntegration. Fail to connect!!!')
    def turnArm(self, angle):
        angle = self.map_value(angle, ANGULO_BASE_MIN, ANGULO_BASE_MAX, ANGULO_BASE_COPPELIA_MIN, ANGULO_BASE_COPPELIA_MAX)
        self.armFunctions(angle, "rotation_arm")
        self.rotation_arm = angle

    def ext1Arm(self, angle):
        if angle < ANGULO_EXT1_COPPELIA_MIN:
            angle = ANGULO_EXT1_COPPELIA_MIN
        elif angle > ANGULO_EXT1_COPPELIA_MAX:
            angle = ANGULO_EXT1_COPPELIA_MAX
        angle = self.map_value(angle, ANGULO_EXT1_MIN, ANGULO_EXT1_MAX, ANGULO_EXT1_COPPELIA_MIN, ANGULO_EXT1_COPPELIA_MAX)
        self.armFunctions(angle, "incline_ext1")
        self.ext1_arm = angle

    def ext2Arm(self, angle):
        angle = self.map_value(abs(angle), ANGULO_EXT2_MIN, ANGULO_EXT2_MAX, ANGULO_EXT2_COPPELIA_MIN, ANGULO_EXT2_COPPELIA_MAX)
        if angle < ANGULO_EXT2_COPPELIA_MIN:
            angle = ANGULO_EXT2_COPPELIA_MIN
        elif angle > ANGULO_EXT2_COPPELIA_MAX:
            angle = ANGULO_EXT2_COPPELIA_MAX
        self.armFunctions(angle, "incline_ext2")
        self.ext2_arm = angle

    def close_gripper(self):
        if not self.gripper_close:
            angleRad = ANGULO_GRIPPER_COPPELIA_MIN #math.radians(0)
            id = "gripper" + str(random.randint(0, 10))
            data_pack = msgpack.packb({"id": id, "type": "gripper", "Data": angleRad})
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'data_to_moviment',
                                       [], [], [], data_pack, sim.simx_opmode_oneshot)
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'execute_moviment',
                                       [], [], [], id, sim.simx_opmode_oneshot)
            waitExecutionMoves(id)
            self.gripper_close = True

    def open_gripper(self):
        if self.gripper_close:
            angleRad = ANGULO_GRIPPER_COPPELIA_MAX #math.radians(70)
            id = "gripper" + str(random.randint(0, 10))
            data_pack = msgpack.packb({"id": id, "type": "gripper", "Data": angleRad})
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'data_to_moviment',
                                       [], [], [], data_pack, sim.simx_opmode_oneshot)
            sim.simxCallScriptFunction(clientID, Handler, sim.sim_scripttype_childscript, 'execute_moviment',
                                       [], [], [], id, sim.simx_opmode_oneshot)
            waitExecutionMoves(id)
            self.gripper_close = False

    def map_value(self, value, from_min, from_max, to_min, to_max):
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min
