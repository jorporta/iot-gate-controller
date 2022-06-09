import time
import traceback
import json
import RPi.GPIO as GPIO
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    PublishToIoTCoreRequest,
    SubscribeToIoTCoreRequest
)

#Setup the LED GPIO
RED = 23
GREEN = 25
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RED,GPIO.OUT)
GPIO.setup(GREEN,GPIO.OUT)

subscribetopic = "gate/2/leds"

TIMEOUT = 10
qos = QOS.AT_LEAST_ONCE
subqos = QOS.AT_MOST_ONCE

ipc_client = awsiot.greengrasscoreipc.connect()

#Code to subscribe to topic from 
class SubHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        try:
            message = str(event.message.payload, "utf-8")
            print("message: " + str(message))
            topic_name = event.message.topic_name
            # Handle message.
            cmd = json.loads(message)

            if 'green' in cmd:
                if cmd["green"]:
                    print("green on")
                    GPIO.output(GREEN,GPIO.HIGH)
                else:
                    print("green off")
                    GPIO.output(GREEN,GPIO.LOW)

            if 'red' in cmd:
                if cmd["red"]:
                    print("red on")
                    GPIO.output(RED,GPIO.HIGH)
                else:
                    print("red off")
                    GPIO.output(RED,GPIO.LOW)

        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass

subrequest = SubscribeToIoTCoreRequest()
subrequest.topic_name = subscribetopic
subrequest.qos = subqos
handler = SubHandler()

operation = ipc_client.new_subscribe_to_iot_core(handler)
future = operation.activate(subrequest)
future.result(TIMEOUT)

# Keep the main thread alive, or the process will exit.
while True:
    time.sleep(10)
    pass

