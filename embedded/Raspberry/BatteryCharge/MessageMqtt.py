import json
class Message():
    def __init__(self, dispositivo, comando):
        self.dispositivo = dispositivo
        self.comando = comando
    def toJson(self):
        return json.dumps(self.__dict__)

    def setDispositivo(self, dispositivo):
        self.dispositivo = dispositivo

    def setComando(self, comando):
        self.comando = comando
def messageJsonDecoder(messageJson):
    if '__type__' in messageJson and messageJson['__type__'] == 'Message':
        obj = Message(messageJson['dispositivo'], messageJson['comando'])
    return obj
