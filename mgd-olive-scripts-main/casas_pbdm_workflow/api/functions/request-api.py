import boto3
import os
import json
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr


#DYNAMO##
dynamodb = boto3.resource('dynamodb')
#table = dynamodb.Table(os.environ['requests_table'])

##STEPFUNCTIONS##
sf = boto3.client('stepfunctions')
sf_partialArn = os.environ['sf_partialArn']
#ECS##
ecs = boto3.client('ecs')
cluster_name = os.environ['cluster_name']

#S3 ##
s3 = boto3.resource(
  "s3"
  )
s3Client = boto3.client(
  's3'
  )
BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_PATH = '{}/wf/{}/'
partial_url = os.environ["partial_url"]

def state(event, context):
    wf = event['pathParameters']['wf']
    requestId = event['queryStringParameters']['id']
    
    if wf != "pbdm":
       return {
        'statusCode': 400,
        'body': json.dumps({"Error": "Wrong request, only \"pbdm\" is accepted"}),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
       }
    
    try:
        # CHECK ON SF IF EXISTS AN EXECUTION WITH ID == REQUESTID
        response_sf = sf.describe_execution(
            executionArn= sf_partialArn + requestId
        )

    except ClientError as e:
        return {
        'statusCode': 404,
        'body': json.dumps({
            "State": "not found",
            "Error": e.response['Error']['Message']}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
    if response_sf['status'] == "SUCCEEDED":
        output = json.loads(response_sf['output'])
        input = json.loads(response_sf['input'])
        if output['LastStatus'] == "STOPPED" and output['Containers'][0]['ExitCode'] != 0:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "Error": "Container Task into ECS failed",
                    "ExitCode": response_sf['output']['Containers']['ExitCode']
                }),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
        country = input["country"]
        sdate = input["start_date"]
        edate = input["end_date"]
        model = input["model"]
        dataset = input["dataset"]
        wf = input["wf"]

        file_name = '{}{}_{}_{}_{}_{}.zip'.format(BUCKET_PATH.format(dataset, wf), dataset, model, sdate.replace('/', '-'), edate.replace('/', '-'), country)
        return {
            'statusCode': 200,
            'body': json.dumps({
                    "State": response_sf['status'],
                    "url": '{}/{}/{}'.format(partial_url, BUCKET_NAME, file_name)}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }    
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({
                    "State": response_sf['status']
            }),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }