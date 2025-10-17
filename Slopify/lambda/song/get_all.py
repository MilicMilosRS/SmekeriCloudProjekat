import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
table_name = os.environ["TABLE_NAME"]
table = dynamodb.Table(table_name)

def get_all(event, context):
    response = table.scan()
    items = response.get("Items", [])

    res = ({})

    return {'statusCode': 200, 'body': json.dumps({'items': items})}