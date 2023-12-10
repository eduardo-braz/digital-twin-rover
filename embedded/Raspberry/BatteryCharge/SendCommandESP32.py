import time
import subprocess
import serial
import BatteryCharge.mqtt_baterryCharge as Mqtt
import threading
import BatteryCharge.MessageBatteryCharge as messageBattery

COMMAND_ESP32 = 'python -m serial.tools.list_ports VID:PID=10C4:EA60 -q'
VELOCIDADE_USB_ESP32 = 9600
SERIAL_TIMESLEEP = 1.5
global USB_ESP32

topicoComum = {
    "publish": "/middle/comum",
    "listener": "/rover/comum",
    "qos": 0
}

topicoEmergencial = {
    "publish": "/middle/emergencia",
    "listener": "/rover/emergencia",
    "qos": 2
}
def publica_carga_bateria(dispositivo, carga):
    mqtt = Mqtt.Mqtt()
    message = messageBattery.MessageBatteryCharge(dispositivo, carga)
    print(f"Mensagem messageBattery: {message.toJson()}")
    mqtt.publish(topicoComum['publish'], message, topicoComum['qos'])
    time.sleep(1)
    mqtt.disconnect_mqtt()

def envia_comando_USB(name, usb_port, vel, comando):
    try:
        serial_port = serial.Serial(usb_port, vel, timeout=1.5)
        time.sleep(0.5)
        if serial_port is not None:
            if serial_port.isOpen():
                serial_port.write(comando.encode())
                response = ""
                while len(response) == 0:
                    response = serial_port.readline()
                time.sleep(SERIAL_TIMESLEEP)
                response = response.decode("utf-8").strip()
                print(f"Comando {comando} -> response {response}")
                ''' Inserir thread para publicação '''
                threadPublish = (threading.Thread(target=publica_carga_bateria, args=(comando, response)))
                threadPublish.start()
                threadPublish.join()
            else:
                print(f"Erro ao abrir comunicação com {name}")
        else:
            print(f"USB de {name} desconectado")
    except serial.SerialException:
        print(f"Erro ao comunicar com {name}")
    serial_port.close()

def busca_porta_USB(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    terminal_response = output.decode().strip()
    return terminal_response


USB_ESP32 = busca_porta_USB(COMMAND_ESP32)  # Retorna vazio se houver erro na comunicação
print(f"Porta ESP32: {USB_ESP32}")  # Remover linha
if not USB_ESP32:
    print("Não foi possível iniciar comunicação com ESP32")


def controle_de_comandos(command):
    global USB_ESP32
    envia_comando_USB("ESP32", USB_ESP32, VELOCIDADE_USB_ESP32, command)
    time.sleep(2)

    

    
