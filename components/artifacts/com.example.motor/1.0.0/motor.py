import time
import traceback
import json
import RPi.GPIO as GPIO
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    SubscribeToIoTCoreRequest
)

# Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

# Set pin 12 as an output, and define as servo1 as PWM pin
GPIO.setup(12,GPIO.OUT)
servo1 = GPIO.PWM(12,50) # pin 12 for servo1, pulse 50Hz

# Start PWM running, with value of 0 (pulse off)
servo1.start(0)

# Bootstrap
servo1.ChangeDutyCycle(12)
time.sleep(0.5)
servo1.ChangeDutyCycle(0)
servo1.ChangeDutyCycle(7)
time.sleep(0.5)
servo1.ChangeDutyCycle(0)

#servo1.stop()
#GPIO.cleanup()

###

subscribetopic = "gate/2/motor"

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

            if 'open' in cmd:
                if cmd["open"]:
                    print("gate up")
                    servo1.ChangeDutyCycle(12)
                    time.sleep(0.5)
                    servo1.ChangeDutyCycle(0)
                else: 
                    print("gate down")
                    servo1.ChangeDutyCycle(7)
                    time.sleep(0.5)
                    servo1.ChangeDutyCycle(0)
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

