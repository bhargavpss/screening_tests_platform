import json
import sys
import boto3

def lambda_handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('q_internal_screening')
    
    questions = event
    out = []
    for question in questions:
        response = table.put_item(
                    Item = question
            )
        if response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
            return {
				"body": response,
				"statusCode": response.get("ResponseMetadata").get("HTTPStatusCode"))
            break;
        else:
            #print '{},{} Inserted. HTTPStatusCode {} ok'.format(question.get("set"),question.get("q_no"),response.get("ResponseMetadata").get("HTTPStatusCode"))
            out.append('{},{} Inserted. HTTPStatusCode {} ok'.format(question.get("set"),question.get("q_no"),response.get("ResponseMetadata").get("HTTPStatusCode")))
    
    return {
        "body": json.dumps(out, indent=4),
        "statusCode": 200,
    }
