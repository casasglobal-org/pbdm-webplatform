import boto3
import os
import base64
import botocore
import datetime
import zipfile
import json
import time
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
 

##BOTO##
s3 = boto3.resource("s3")
s3Client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')
queue_url = 'https://sqs.eu-west-1.amazonaws.com/662713783319/dev-pbdm-ti-workflow'

sf = boto3.client('stepfunctions')
table_wfs = dynamodb.Table(os.environ['workflow_table'])

#ECS##
ecs = boto3.client('ecs')
cluster_name = os.environ['cluster_name']

BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_PATH = '{}/wf/{}/'

##_ECMWF WF_##
def index(event, context):
    # Check params
    wf = event['pathParameters']['wf']
    dataset = event['pathParameters']['id']
    query_params = event['queryStringParameters']
    requestId = event['requestContext']['requestId']
    try:
        response = table_wfs.scan(
            FilterExpression = Attr('id').eq(wf)&Attr('datasets').contains(dataset)
        )
        items = response['Items']
        if len(items) is 0:
            raise Exception('Workflow not found!')

        sdate = query_params.get('sdate')
        edate = query_params.get('edate')
        country = query_params.get('country')
        model = query_params.get('model')
        out_time_int = query_params.get('output_time_interval')
        resolution = query_params.get('resolution')
        print(sdate)
        values = items[0]
        print(values)
        err_message = pbdm_var_check(sdate, edate, country, dataset, model, out_time_int, values, resolution)

        
        if 'no_error' in err_message:
            returnVal = {
                'requestId': requestId,
                'country':  country,
                'start_date': sdate,
                'end_date': edate,
                'model': model,
                'dataset': dataset,
                'output_time_interval': out_time_int,
                'wf': wf,
                'resolution': resolution
            }

            response = check_if_task_already_exists(requestId, sdate, edate, country, dataset, model, out_time_int, wf)
            response = {
                'state': 'not found'
            }
            if response['state'] == 'error':
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        "error": response['error']
                        }),
                    'headers': {
                        'Access-Control-Allow-Origin': '*'
                    }
                }

            #if response['state'] == 'not found':
            sf_response=""
            try:
                # Trigger step function
                # sf_response = sf.start_execution(
                #     stateMachineArn=os.environ['sf_arn'],
                #     name=requestId,
                #     input= json.dumps(returnVal)
                # )
                #queue = sqs.get_queue_by_name(QueueName='test')
                sf_response = sqs.send_message(QueueUrl=queue_url,MessageBody=json.dumps(returnVal))

            except ClientError as e:
                print(e)
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        "StepFunctions_Response": sf_response,
                        "error": e
                        }),
                    'headers': {
                        'Access-Control-Allow-Origin': '*'
                    }
                }
            # else:
            #     requestId = response['requestId']
            
            
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'Error': err_message}),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }
    except ClientError as e:
        print(e)
        return {
            'statusCode': 422,
            'body': json.dumps({"Message":"Invalid request"}),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'RequestId': requestId}),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }



def check_if_task_already_exists(requestId, sdate, edate, country, dataset, model, out_time_int, wf):
    # CHECK ON S3 FILE.TXT
    BUCKET_NAME = os.environ['BUCKET_NAME']
    # json_file_name = '{}json/{}_{}_{}_{}_{}.json'.format(BUCKET_PATH, dataset, model, sdate.replace('/', '-'), edate.replace('/', '-'), country)
    json_file_name = '{}json/{}.json'.format(BUCKET_PATH.format(dataset, id), requestId)
    zip_file_name = '{}{}_{}_{}_{}_{}.zip'.format(BUCKET_PATH, dataset, model, sdate.replace('/', '-'), edate.replace('/', '-'), country)
    print(zip_file_name)
    try:
        json_file = json.loads(s3Client.get_object(
            Bucket=BUCKET_NAME,
            ResponseContentType='application/json',
            Key=json_file_name
            )['Body'].read().decode('utf-8'))
        print("Finded json: " + BUCKET_NAME + "/" + json_file_name)

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # IS NOT HERE :(
            #RETURN PARAM REQUESTID AND STATE "NOT FOUND"
            return {
                'state': "not found"
            }
        else:
            return {
                'state': 'error',
                'error': e
            }
    else:
    # IS HERE
        print("Json state:" + json_file['state'])
        if json_file['state'] == 'done':
            try:
                s3Client.get_object(Bucket=BUCKET_NAME, Key=zip_file_name)
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchKey':
                    #TODO
                    #Delete json file
                    return {
                        'state': "not found"
                    }
                else:
                    return {
                        'state': 'error',
                        'error': e
                    }
        else:
            if json_file['state'] == 'failed':
                return {
                        'state': "not found"
                    }
            else:
                return {
                    'state': json_file['state'],
                    'requestId': json_file['requestId']
            }
        return {
            'state': json_file['state'],
            'requestId': requestId
        }


def pbdm_var_check(sdate, edate, country, dataset, model, out_time_int, values, resolution):
    sdate = sdate.split('/')
    edate = edate.split('/')

    if int(sdate[0]) < int(values[dataset][country]['sdate']):
        return 'sdate value not valid'

    if int(edate[0]) > int(values[dataset][country]['edate']):
        return 'edate value not valid'

    try:
        datetime.date(int(sdate[0]), int(sdate[1]), int(sdate[2]))
        datetime.date(int(edate[0]), int(edate[1]), int(edate[2]))
    except IndexError:
        return 'Invalid date! Correct date format is YYYY/MM/DD'


    if model not in values[dataset][country]['model']:
        return 'model value not valid'

    if country not in values[dataset]['country']:
        return 'country value not valid!'

    if out_time_int not in values[dataset][country]['output_time_interval']:
        return 'output_time_interval value not valid!'
    
    if len(values[dataset][country]['resolution']) != 0:
        if resolution not in values[dataset][country]['resolution']:
            return 'resolution value not valid!'

    return 'no_error'