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

<img src="https://github.com/jorporta/iot-gate-controller/blob/main/images/gate.png" width="400" />

## Architecture

On the device side, there are three components with the following intents:
- sensors: in charge of polling IR sensory data every second and publish it to the ***/gate/{gateid}/sensors*** mqtt topic
- leds: in charge of reading messages from ***/gate/{gateid}/leds*** mqtt topic and switching a green and red leds on/off
- motor: in charge of reading messages from ***/gate/{gateid}/motor*** mqtt topic and opening/closing the gate

Messages received from the sensors is pushed to the Gate Controller detector via the ***gate_sensors*** AWS IoT Rule.
Commands pushed by teh Gate Controller detector are pushed as messages to the respective leds and motor topics.

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
