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
)

sensor1 = 40 
sensor2 = 38 

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor1,GPIO.IN)
GPIO.setup(sensor2,GPIO.IN)

publishtopic = "gate/2/sensors"

TIMEOUT = 10
qos = QOS.AT_LEAST_ONCE
subqos = QOS.AT_MOST_ONCE

ipc_client = awsiot.greengrasscoreipc.connect()

message = {}
while True:

    message['sensor1'] = not GPIO.input(sensor1)
    message['sensor2'] = not GPIO.input(sensor2)

    msgstring = json.dumps(message)
    print("msg: " + msgstring)

    pubrequest = PublishToIoTCoreRequest()
    pubrequest.topic_name = publishtopic
    pubrequest.payload = bytes(msgstring, "utf-8")
    pubrequest.qos = qos
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(pubrequest)
    future = operation.get_response()
    future.result(TIMEOUT)

    time.sleep(1)
