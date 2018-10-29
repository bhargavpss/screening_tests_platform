import json
import boto3
import sys
from decimal import *

def lambda_handler(event, context):
    
    s3 = boto3.resource('s3')
   
    EmployeeId = event["EmployeeId"]
    CertificationId = event["CertificationId"]
    UUID = event["UUID"]
    solutions = event["solutions"]
    
    object_key = '{}/{}/ak_{}.json'.format(CertificationId, EmployeeId, UUID)
    
    s3.meta.client.download_file('q-internal-screening-evaluation', object_key, '/tmp/answer_key.json')
    
    with open('/tmp/answer_key.json', 'r') as json_file:
        answer_key=json.load(json_file)
    
    score = 0
    
    if len(solutions) == len(answer_key["answer_key"]):
    
        answers = ['X']*len(answer_key["answer_key"])
        for i in answer_key["answer_key"]:
            q_no=int(i["q_no"][1:])
            answers.insert(q_no-1, i["answer"] )
            answers.pop(q_no)
        
        claims = ['X']*len(solutions)
        for i in solutions:
            q_no=int(i["q_no"][1:])
            claims.insert(q_no-1, i["answer"] )
            claims.pop(q_no)
        
        for i in range(len(claims)):
            if sorted(claims[i]) == sorted(answers[i]):
                score=score+1
        
        pass_percentage=70
        
        if float(score*100/len(answer_key["answer_key"])) >= 70:
            result = 'Passed'
        else:
            result = 'Failed'
        
        marks_per_question=20
        score = score*marks_per_question
        
    else:
        return {
            "body" : {
                "score" : "Unable to evaluate scores as the number of answers is not equal to the number of questions",
                "statusCode" : 300,
                "result" : "Cannot say. "
            }
        }
        
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('records_q_internal_screening')
    
    item = table.get_item(
            Key = {
                'EmployeeId' : EmployeeId,
                'CertificationId' : CertificationId
            }
        )
        
    attempts=item["Item"]["attempts"]
    
    for i in attempts:
        successful_attempts=0
        if i["result_if_cleared"]:
            successful_attempts+=1

    number_of_attempts=len(attempts)+1 
    
    if result == 'Failed':
        result_if_cleared=False
        number_of_successful_attempts=successful_attempts
    elif result == 'Passed':
        result_if_cleared=True
        number_of_successful_attempts=successful_attempts+1
        
    
	new_attempt={u'date': u'1996-08-25', u'score': Decimal(score), u'max_score': Decimal('100'), u'result_if_cleared':result_if_cleared , u'attempt_number': Decimal(number_of_attempts)}
	#new_attempt={"date": "1996-08-25", "score": score, "max_score": 100, "result_if_cleared": result_if_cleared, "attempt_number": number_of_attempts}
	
    attempts.append(new_attempt.copy())
    print attempts

    response=table.put_item(
            Item= {
                "EmployeeId": EmployeeId,
                "CertificationId": CertificationId,
                "EmployeeName": item["Item"]["EmployeeName"],
                "number of attempts": number_of_attempts,
                "number of successful attempts": number_of_successful_attempts,
                "attempts": attempts
            }
        )
    print response
    
    return {
        "body" : {
                "score" : score,
                "statusCode" : 200,
                "result" : result
            }
    }
