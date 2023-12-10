import time
import BatteryCharge.baterryMonitor as batMonitor
import listener_mqtt as Mqtt
import MessageMqtt as mq
import threading
import servoController

servo = servoController.Servo()
mqtt = Mqtt.Mqtt()

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


if __name__ == "__main__":
    status = -1
    while status != 0:
        messagem = mq.Message("Raspberry", "OK")
        status = mqtt.publish(topicoComum['publish'], messagem, topicoComum['qos'])
        time.sleep(1)
    
    time.sleep(1)
    ''' Abre thread para executar monitoramento de bateria '''
    try:
        (threading.Thread(target=batMonitor.monitoring)).start()
    except Exception as e:
        print(f"Erro ao realizar leitura de baterias.")
    
    '''  Execucao do programa   '''
    while (True):
        print(".", end="")
        mqtt.subscribe(topicoComum['listener'], topicoComum['qos'])

