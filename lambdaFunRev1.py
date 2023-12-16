import boto3
import json

# Getting the service resource and defining the table.
dynamodb = boto3.resource('dynamodb')
tableName = 'icecreamTruckDataDB'
sns = boto3.client('sns')

def lambda_handler(event, context):

    # Get the data from the IoT message
    payload = event

    # Connect to DynamoDB
    dynamodb_client = boto3.client('dynamodb')

    # Extracting the data and creating a DynamoDB item
    item = {
        'time_local': {'S': payload['time_local']},
        'temp_C': {'N': str(payload['temp_C'])},
        'humidity_pc': {'N': str(payload['humidity_pc'])},
        'pressure_hPa': {'N': str(payload['pressure_hPa'])},
        'ambTemp_C': {'N': str(payload['ambTemp_C'])},
        'ambHumidity_pc': {'N': str(payload['ambHumidity_pc'])},
        'ambPressure_hPa': {'N': str(payload['ambPressure_hPa'])},
        'seriousness': {'N': str(payload['seriousness'])},
        'truck_lat': {'N': str(payload['truck_lat'])},
        'truck_lon': {'N': str(payload['truck_lon'])}
        }

    # Inserting the item into DynamoDB
    dynamodb_client.put_item(TableName = tableName, Item = item)
    temperature = float(payload['temp_C'])
    if temperature > 35:
        # Send SNS notification
        sns.publish(
            TopicArn='arn:aws:sns:ap-southeast-2:556410964474:topicForTemperatureThd',  # Replace with your SNS topic ARN
            Subject='Temperature Alert',
            Message=f'Temperature is greater than 35. Current temperature is {temperature}°C.'
        )

    return {
        'statusCode': 200,
        'body': 'Item inserted successfully into DynamoDB'
    }