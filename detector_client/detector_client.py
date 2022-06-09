#!/usr/bin/env python3

from simple_term_menu import TerminalMenu
import os
import uuid
import json

get_status = 'aws iotevents-data describe-detector --detector-model-name GateController --key-value 2 | jq .detector.state.stateName'
send_cmd   = 'aws iotevents-data batch-put-message --cli-input-json file://cmd.json > /dev/null'
templates  = [ 'inputs/all_sensors_clear.json', 'inputs/sensor1_blocked.json', 'inputs/sensor2_blocked.json' ]

def main():
    options = [\
    "[0] All sensors clear",\
    "[1] Sensor 1 blocked",\
    "[2] Sensor 2 blocked",\
    "[3] Get Status", \
    "[4] Quit", \
    ]

    while True:
        terminal_menu = TerminalMenu(options)
        sel = terminal_menu.show()
        os.system('clear')

        if sel == 4:
            break
    
        if sel < 3:
            file = templates[sel]
            with open(file,'r') as fp:
                s = json.load(fp)
                s['messages'][0]['messageId'] = str(uuid.uuid1())
                s['messages'][0]['payload']['uuid'] = str(uuid.uuid1())
                t = json.dumps(s['messages'][0]['payload'])
                t = t.replace('"','\"')
                s['messages'][0]['payload'] = t
            with open('cmd.json','w') as fp:
                fp.write(json.dumps(s))

            os.system(send_cmd)
        os.system(get_status)

if __name__ == "__main__":
    main()
