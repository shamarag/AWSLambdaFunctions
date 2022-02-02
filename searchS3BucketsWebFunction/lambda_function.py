import json
import boto3
import time

s3 = boto3.resource('s3')
def lambda_handler(event, context):
    file_content_list = []
    for bucket in s3.buckets.all():
        for s3file in bucket.objects.all():
            print('{0}:{1}'.format(bucket.name, s3file.key))
            file_bytes = s3file.get()['Body'].read()
            file_content = ''
            if (s3file.key.endswith('txt')): #if .txt file
                file_content = file_bytes.decode('utf-8') #decode bytes to string
                #print('Content :'+file_content)
                file_content_list.append(file_content)
                
            if (s3file.key.endswith('pdf')): #if .pdf file
                jobId = startJob(bucket.name, s3file.key)
                print("Started job with id: {}".format(jobId))
                if(isJobComplete(jobId)):
                    response = getJobResults(jobId)
                    #print(response)
                    # Print detected text
                for resultPage in response:
                    for item in resultPage["Blocks"]:
                        if item["BlockType"] == "LINE":
                                #print ('\033[94m' + item["Text"] + '\033[0m')
                                file_content = item["Text"]
                                file_content_list.append(file_content)
        
            
    return {
        'statusCode': 200,
        'body': json.dumps(file_content_list)
    }



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

    while(status == "IN_PROGRESS"):
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
    if('NextToken' in response):
        nextToken = response['NextToken']

    while(nextToken):
        time.sleep(5)

        response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)

        pages.append(response)
        print("Resultset page recieved: {}".format(len(pages)))
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']

    return pages
