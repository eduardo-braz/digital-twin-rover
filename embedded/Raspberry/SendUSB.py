import servoController as sc
import time
import subprocess
import serial
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

PORT_CAMERA = 6

COMMAND_ARDUINO = 'python -m serial.tools.list_ports VID:PID=1A86:7523 -q'
COMMAND_ESP32 = 'python -m serial.tools.list_ports VID:PID=10C4:EA60 -q'
VELOCIDADE_USB_ARDUINO = 9600
VELOCIDADE_USB_ESP32 = 9600
SERIAL_TIMESLEEP = 1.5
global USB_ARDUINO
global USB_ESP32

'''   Controle dos servos do pantilt  '''
servo_inclinacao = sc.Servo("INCLINACAO")
servo_base = sc.Servo("BASE")

def envia_comando_USB(name, usb_port, vel, comando):
    response = None
    try:
        serial_port = serial.Serial(usb_port, vel, timeout=1.5)
        time.sleep(0.5)
        if serial_port.isOpen():
            serial_port.write(comando.encode())
            response = ""
            while len(response) == 0:
                response = serial_port.readline()
            print(f'Response: {response.decode("utf-8")}')
            time.sleep(SERIAL_TIMESLEEP)
        else:
            print(f"Erro ao abrir comunicação com {name}")
    except serial.SerialException:
        print(f"Erro ao comunicar com {name}")

    serial_port.close()

def busca_porta_USB(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    terminal_response = output.decode().strip()
    return terminal_response


USB_ARDUINO = busca_porta_USB(COMMAND_ARDUINO)  # Retorna vazio se houver erro na comunicação
USB_ESP32 = busca_porta_USB(COMMAND_ESP32)  # Retorna vazio se houver erro na comunicação

if not USB_ARDUINO:
    print("Não foi possível iniciar comunicação com Arduino")
if not USB_ESP32:
    print("Não foi possível iniciar comunicação com ESP32")

def controle_de_comandos(message):
    global USB_ARDUINO
    global USB_ESP32
    
    if message.dispositivo == "Arduino":
        envia_comando_USB("Arduino", USB_ARDUINO, VELOCIDADE_USB_ARDUINO, message.comando)
    elif message.dispositivo == "ESP32":
        envia_comando_USB("ESP32", USB_ESP32, VELOCIDADE_USB_ESP32, message.comando)
    elif message.dispositivo == "Raspberry":
        comando = message.comando[0]
        value = int(message.comando[1:])
        if comando == "B":
            servo_base.base_turn(value)
        elif comando == "I":
            servo_inclinacao.inclinar(value)
    elif message.dispositivo == "Todos":
        if message.comando == "S":
            servo_inclinacao.shutdown()
            try:
                envia_comando_USB("Arduino", USB_ARDUINO, VELOCIDADE_USB_ARDUINO, message.comando)
                envia_comando_USB("ESP32", USB_ESP32, VELOCIDADE_USB_ESP32, message.comando)
            except:
                print(f"Erro ao comunicar com portas seriais")
            time.sleep(2)

    

    
