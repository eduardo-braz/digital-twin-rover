import json
class MessageBatteryCharge():
    def __init__(self, device, value):
        self.device = device
        self.value = value

    def toJson(self):
        return json.dumps(self.__dict__)

    def setdevice(self, device):
        self.device = device

    def setValue(self, value):
        self.value = value
        
def messageJsonDecoder(messageJson):
    print(messageJson)
    if '__type__' in messageJson and messageJson['__type__'] == 'MessageBatteryCharge':
        obj = MessageBatteryCharge(messageJson['device'], messageJson['value'])
    return obj
    
