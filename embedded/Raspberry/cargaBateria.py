import json

class CargaBateria():
    def __init__(self, dispositivo, percentual):
        self.dispositivo = dispositivo
        self.percentual = int(100 * round(percentual/4095, 2))

    def toJson(self):
        return json.dumps(self.__dict__)

    def setDispositivo(self, dispositivo):
        self.dispositivo = dispositivo

    def setPercentual(self, percentual):
        self.percentual = int(100 * round(percentual/4095, 2))
        
def messageJsonDecoder(messageJson):
    if '__type__' in messageJson and messageJson['__type__'] == 'CargaBateria':
        obj = CargaBateria(messageJson['dispositivo'], messageJson['percentual'])
    return obj
    
