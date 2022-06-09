# iot-gate-controller
AWS IoT driven Gate Controller leveraging no-code approach with IoT Events detector

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

## Components
