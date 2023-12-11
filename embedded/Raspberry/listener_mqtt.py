import time
import random
import json
import paho.mqtt as mqtt_connection
import paho.mqtt.client
import MessageMqtt as mq
from SendUSB import controle_de_comandos

client_id = f'python-mqtt-{random.randint(0, 10)}'

mqtt_dados = {
    "broker": "192.168.2.142",
    "port": 1883,
    "user": "rover",
    "password": "password1234"
}
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

class Mqtt:
    payload = None
    def disconnect_mqtt(self):
        if self.client:
            self.client.disconnect()
            print("Disconnected from MQTT Broker")
    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker")
            else:
                print("Failed to connect with code %d", rc)

        client = mqtt_connection.client.Client(client_id)
        client.username_pw_set(mqtt_dados['user'], mqtt_dados['password'])
        client.on_connect = on_connect
        client.connect(mqtt_dados['broker'], mqtt_dados['port'])
        return client

    def publish(self, topic, message, qos):
        status = self.client.publish(topic, message.toJson(), qos)[0]
        time.sleep(0.5)
        print(message.toJson())
        if status == 0:
            print(f"Send message to topic `{topic}`")
        else:
            print(f"Failed to send message \'{message}\' to topic \'{topic}\' with QoS {qos}")
        return status

    def subscribe(self, topic, qos):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}`")
            try:
                self.payload = json.loads(msg.payload.decode().replace('{', '{\"__type__\": \"Message\", '),
                                          object_hook=mq.messageJsonDecoder)
                controle_de_comandos(self.payload)
            except json.JSONDecodeError:
                print("Invalid JSON format")
            except Exception as e:
                print(f"Error in on_message: {e}")
        self.client.subscribe(topic, qos)
        self.client.on_message = on_message
        print(f"Listening topic: {topic}")
        self.client.loop_forever(max_packets=1)

    def __init__(self):
        self.client = self.connect_mqtt()
        time.sleep(1)
