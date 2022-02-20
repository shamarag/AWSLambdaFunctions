import boto3
import re
import requests
from requests_aws4auth import AWS4Auth
import time
import json
import datetime

region = 'us-east-2' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-masterdocs-eoqkoj4s3xvpm5d43wjrpgdiue.us-east-2.es.amazonaws.com' # the OpenSearch Service domain, including https://
index = 's3-alldocsbucket-index'
type = '_doc'
url = host + '/' + index + '/' + type

headers = {"Content-Type": "application/json"}

s3 = boto3.resource('s3')

# Regular expressions used to parse some simple log lines but not used here
ip_pattern = re.compile('(\d+\.\d+\.\d+\.\d+)')
time_pattern = re.compile('\[(\d+\/\w\w\w\/\d\d\d\d:\d\d:\d\d:\d\d\s-\d\d\d\d)\]')
message_pattern = re.compile('\"(.+)\"')

# Lambda execution starts here
def lambda_handler(event, context):

    src_bucket = s3.Bucket('my-alldocs-bucket')
    
    for s3file in src_bucket.objects.all():

        # Get, read, and split the file into lines
        # obj = s3.get_object(Bucket=bucket, Key=key)
        body = s3file.get()['Body'].read()
        
        file_content = ''
        file_type = ''
        file_size = 0
        file_path = ''
        file_content_list = []
        # print key.name, key.size, key.last_modified
        if(s3file.key.endswith('txt')): # if .txt file
            file_type = 'TXT'
            file_content = body.decode('utf-8')  # decode bytes to string
            file_content_list.append(file_content)
        if (s3file.key.endswith('pdf')):  # if .pdf file
            file_type = 'PDF'
            jobId = startJob(src_bucket.name, s3file.key)
            print("Started job with id: {}".format(jobId))
            if (isJobComplete(jobId)):
                response = getJobResults(jobId)
                # print(response)
                # Print detected text
            for resultPage in response:
                for item in resultPage["Blocks"]:
                    if item["BlockType"] == "LINE":
                        # print ('\033[94m' + item["Text"] + '\033[0m')
                        file_content = item["Text"]
                        file_content_list.append(file_content)
            
        print(s3file.key)
        print('s3 file size = %.3f MB' % (s3file.size/1024/1024))
        file_size = round((s3file.size/1024.0/1024.0), 2)
        file_path= src_bucket.name+'/'+s3file.key
        tmpDate = datetime_handler(s3file.last_modified)
        print(tmpDate)
        
        
        
        document = {"name": s3file.key, "bucketname": src_bucket.name, "type":file_type, "filepath":file_path, "size": file_size, "lastmod": tmpDate, "content": file_content_list}
        #document = json.dumps(document, default = myconverter)
        #document = json.dumps(document) 
        
        try:
            #r = requests.post(url, auth=awsauth, json=document, headers=headers)
            r = requests.post(url, auth=awsauth, json=document, headers=headers)
            response = {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": '*'
                },
                "isBase64Encoded": False
            }
            
            # Add the search results to the response
            response['body'] = r.text
        
        except Exception as e:
            print(e)
            response['body'] = r.text
        
        print(response) 
      
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        print(x.isoformat())
        return x.isoformat()
    raise TypeError("Unknown type")

def startJob(s3BucketName, objectName):
    response = None
    client = boto3.client('textract')
    response = client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': s3BucketName,
                'Name': objectName
            }
        })

    return response["JobId"]


def isJobComplete(jobId):
    time.sleep(5)
    client = boto3.client('textract')
    response = client.get_document_text_detection(JobId=jobId)
    status = response["JobStatus"]
    print("Job status: {}".format(status))

    while (status == "IN_PROGRESS"):
        time.sleep(5)
        response = client.get_document_text_detection(JobId=jobId)
        status = response["JobStatus"]
        print("Job status: {}".format(status))

    return status


def getJobResults(jobId):
    pages = []

    time.sleep(5)

    client = boto3.client('textract')
    response = client.get_document_text_detection(JobId=jobId)

    pages.append(response)
    print("Resultset page recieved: {}".format(len(pages)))
    nextToken = None
    if ('NextToken' in response):
        nextToken = response['NextToken']

    while (nextToken):
        time.sleep(5)

        response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)

        pages.append(response)
        print("Resultset page recieved: {}".format(len(pages)))
        nextToken = None
        if ('NextToken' in response):
            nextToken = response['NextToken']

    return pages