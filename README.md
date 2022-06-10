# iot-gate-controller
AWS IoT driven Gate Controller leveraging no-code approach with IoT Events detector

<img src="https://github.com/jorporta/iot-gate-controller/blob/main/images/intro.png" width="400" />

## Introduction

This project is meant to get familiarized with the following constructs:
- AWS IoT Events detectors
- AWS IoT Core topics
- AWS IoT Core rules
- AWS IoT Greengrass

The project consists of a samll scale gate that detects car's presence and lets them through.
The decision making and issuing if commands is done entirely from the cloud, with a no-code approach.
The artifacts running on the device are limited to capture sensory data and execute actuator commands.

## Design Principles

**Device**
- Leverage Greengrass to locally develop and debug applications
- Lightweight processes to interface with sensors and actuators
- data pushed to, commands received from IoT Core

**Cloud**
- No-Code decision making leveraging IoT Events
- Changes take effect immediately (no deployment required)
- Each gate is controlled by an independent detector
- Notification system in case of anomalies

On the device side, there are three Greengrass components with the following intents:
- _com.example.sensors_: in charge of polling IR sensory data every second and publish it to the ***/gate/{gateid}/sensors*** mqtt topic
- _com.example.leds_: in charge of reading messages from ***/gate/{gateid}/leds*** mqtt topic and switching a green and red leds on/off
- _com.example.motor_: in charge of reading messages from ***/gate/{gateid}/motor*** mqtt topic and opening/closing the gate

<img src="https://github.com/jorporta/iot-gate-controller/blob/main/images/gate.png" width="400" />

## Architecture

Messages received from the sensors is pushed to the Gate Controller detector via the ***gate_sensors*** AWS IoT Rule.
Commands sent by the Gate Controller detector are pushed as messages to the respective leds and motor topics.
Whenver an alarm is triggered (eg. a car has obstructed the gate for more than 5 seconds), an notification is pushed to a dedicated Amazon SNS topic, resulting into an SMS being sent by the subscriber(s) (eg. gate personnel).

<img src="https://github.com/jorporta/iot-gate-controller/blob/main/images/arch.png" width="800" />

## Gate Controller detector

The detector is a state machine that transitions through its different states according to the sensory inputs and actions.
The **Init** state is resonsible of initializing the topic names which will be used to receive and send messages from/to the device.
Notice how the topic name is build up dynamically, interpolating the _gateid_ as part of the name. 
There is an independent detector created for each gate; which is achieved by specifying 'gateid' as the *key* in the detector definition.

<img src="https://github.com/jorporta/iot-gate-controller/blob/main/images/detector.png" width="800" />

AWS IoT Events detectors offer the abilty to set timers. The granularity of these is down to the minute, which was inconvenient in for our use case.
To have timers to the second, from the **OpenBlocked** state we trigger a lambda function whose sole purpose is to act as a countdown.

Once the timer is off, the lambda will post a message to the gate ***topic/{gateid}/alarm*** which will be passed to the gate controller detector via the ***gate_timeout*** rule.
A timeout message is received 5 seconds after a car has activated the IR sensor situated next to the gate.
To prevent side effects from triggering alarms when we are not supposed to, we'll keep track of which car is under the gate and match alarms with cars.
Any message (ie. car) entering the state machine (**OpenClear** state) is assigned a uuid, and the **OpenBlocked** state will only transition to the **Alarm** state if the _alarm_ message received has a uuid that matches that of the current car.

## Prerequisites ##

- An AWS account
- A device with Greengrass v2 installed (I used a [Raspberry Pi Zero](https://www.raspberrypi.com/products/raspberry-pi-zero/))

This [article](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html) guides you through the whole process.

<img src="https://github.com/jorporta/iot-gate-controller/blob/main/images/pi_zero.png" width="400" />

## Deployment ##

**Note:** Make sure you replace the XXXXXXXXXX placeholders in _gate_controller.json_ and _gate_alarm.py_ with your own account id.

- Create a new AWS IoT Events detector by importing this [model](https://github.com/jorporta/iot-gate-controller/blob/main/gate_controller.json)
- Create the gate_sensors topic rule importing this [model](https://github.com/jorporta/iot-gate-controller/blob/main/gate_sensors.json)
- Create the gate_alarm topic rule importing this [model](https://github.com/jorporta/iot-gate-controller/blob/main/gate_alarm.py)
- Deploy the sensors, leds and motor [components](https://github.com/jorporta/iot-gate-controller/tree/main/components) on the device
```
sudo /greengrass/v2/bin/greengrass-cli deployment create --recipeDir ~/dev/components/recipe/ --artifactDir ~/dev/components/artifacts/ --merge "com.example.sensors=1.0.0"
sudo /greengrass/v2/bin/greengrass-cli deployment create --recipeDir ~/dev/components/recipe/ --artifactDir ~/dev/components/artifacts/ --merge "com.example.leds=1.0.0"
sudo /greengrass/v2/bin/greengrass-cli deployment create --recipeDir ~/dev/components/recipe/ --artifactDir ~/dev/components/artifacts/ --merge "com.example.motor=1.0.0"
```
- Make sure all components are up and running properly:

```
sudo tail -f /greengrass/v2/logs/greengrass.log
sudo /greengrass/v2/bin/greengrass-cli component list
```

- Verify that com.example.sensors is properly posting messages to /gate/{gateid}/sensors by subscribing to this topic in AWS IoT Core Console

```
{
    "sensor1": true,
    "sensor2": false 
}
```

- Verify that com.example.leds sets green and red leds on an off by publishing messages to gate/{leds}/sensors topic in AWS IoT Core Console
```
{
    "green": true,
    "red: true 
}
```
- Verify that com.example.motor open and closes the gate by publishing messages to gate/{leds}/motor topic in AWS IoT Core Console
```
{
    "open": true
}
```
- Deploy the [alarm]()https://github.com/jorporta/iot-gate-controller/blob/main/gate_alarm.py lambda function and verify via CloudWatch that the Gate Controller detector successfully calls it when reaching **OpenBlocked** state

**Tip:** you can use this [client](https://github.com/jorporta/iot-gate-controller/tree/main/detector_client) to send messages directly to the detector's inputs

## Electronics ##

- **IR Sensors** are expected to be connected to pins **40** and **38** of the Raspberry Pi. Adapt the code if need be.
- Green and red **leds** are expected to be connected to pins **23** and **25** of the Raspberry Pi. Adapt the code if need be (both leds pulled down by a **330 ohm** resistor).
- The **servo motor** to control the gate is expected to be connected to pins **12** of the Raspberry Pi. Adapt the code if need be.
