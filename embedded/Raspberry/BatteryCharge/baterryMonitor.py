import BatteryCharge.SendCommandESP32 as Esp32
import BatteryCharge.MessageBatteryCharge as messageBattery
import time

SLEEP_IN_MINUTES = 60 * 5  # Segundos * Minutos  - Usado no como tempo que deve aguardar entre leituras de carga
SLEEP_BETWEEN_CALLS = 2  # Segundos entre chamadas para leitura de cargas

MIN_VALUE = 0
MAX_VALUE = 4095

raspberry = messageBattery.MessageBatteryCharge("C1", MAX_VALUE)
wheels = messageBattery.MessageBatteryCharge("C2", MIN_VALUE)
arm = messageBattery.MessageBatteryCharge("C3", MIN_VALUE)
camera = messageBattery.MessageBatteryCharge("C4", MIN_VALUE)

dispositivos = [raspberry, wheels, arm, camera]

def monitoring():
    while (True):
        for dispositivo in dispositivos:
            print(f'Realizando leitura da bateria de {dispositivo.device}')
            try:
                Esp32.controle_de_comandos(dispositivo.device)
            except Exception as e:
                print(f"Erro ao realizar leitura de bateria em {dispositivo.device}")
            time.sleep(SLEEP_BETWEEN_CALLS)
        time.sleep(SLEEP_IN_MINUTES)
