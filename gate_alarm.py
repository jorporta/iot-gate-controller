
import json
import boto3
import time

client = boto3.client('iot-data', region_name='us-east-1')


def lambda_handler(event, context):
    print("event: " + str(event))
    gateid = event['payload']['detector']['keyValue']
    print("gateid: " + str(gateid))

    uuid = event['payload']['state']['variables']['uuid']
    print("uuid: " + str(uuid))
    
    time.sleep(5)

    # Change topic, qos and payload
    response = client.publish(
        topic='gate/' + gateid + '/alarms',
        qos=1,
        payload=json.dumps({"uuid":uuid})
    )
    print("response: " + str(response))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Published to topic')
    }
