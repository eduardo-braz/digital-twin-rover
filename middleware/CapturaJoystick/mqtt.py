import time
import random
import json
import paho.mqtt as mqtt_connection
import paho.mqtt.client
import MessageMqtt as mq
import MessageBatteryCharge as batteryCharge

client_id = f'python-mqtt-{random.randint(0, 10)}'

mqtt_dados = {
    "broker": "127.0.0.1",
    "port": 1883,
    "user": "rover",
    "password": "password1234"
}

topicoComum = {
    "publish": "/rover/comum",
    "listener": "/middle/comum",
    "qos": 0
}
class Mqtt:
    payload = None
    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker")
            else:
                print("Failed to connect with code %d", rc)

        client = mqtt_connection.client.Client(client_id)#, clean_session=False)
        client.username_pw_set(mqtt_dados['user'], mqtt_dados['password'])
        client.on_connect = on_connect
        client.connect(mqtt_dados['broker'], mqtt_dados['port'])
        return client

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)

    def publish(self, topic, message, qos):
        status = self.client.publish(topic, message.toJson(), qos)[0]#, retain=True)[0]
        time.sleep(0.5)
        print(message.toJson())
        if status == 0:
            print(f"Send message to topic `{topic}`")
        else:
            print(f"Failed to send message \'{message}\' to topic \'{topic}\' with QoS {qos}")

    def publishCamera(self, topic, message, qos):
        status = self.client.publish(topic, message, qos)[0]#, retain=True)[0]
        time.sleep(0.5)
        if status == 0:
            print(f"Send message \'{message}\' to topic `{topic}`")
        else:
            print(f"Failed to send message \'{message}\' to topic \'{topic}\' with QoS {qos}")

    def subscribe(self, topic, qos):
        def on_message(client, userdata, msg):
            self.payload = msg.payload.decode()
            try:
                self.payload = json.loads(self.payload.replace('{', '{\"__type__\": \"Message\", '), object_hook=mq.messageJsonDecoder)
            except:
                try:
                    self.payload = json.loads(self.payload.replace('{', '{\"__type__\": \"MessageBatteryCharge\", '),
                                              object_hook=batteryCharge.messageJsonDecoder)
                except:
                    print("\nInvalid JSON format\n")
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic and QoS '{msg.qos}'")

        self.client.subscribe(topic, qos)
        self.client.on_message = on_message

    def __init__(self):
        self.client = self.connect_mqtt()
        self.client.loop_start()

