import boto3
import json
import requests
from requests_aws4auth import AWS4Auth


region = 'us-east-2' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

#s3 = boto3.resource('s3')
s3 = boto3.client('s3')

# Lambda execution starts here
def lambda_handler(event, context):
        bucket = event['queryStringParameters']['bucket']
        key = event['queryStringParameters']['key']
        extension = key.partition(".")[2]
        print(bucket)
        print(key)

        try:
            #print('test1')
            #fileObj = s3.get_object(Bucket=bucket, Key=key)
            #print('test2')
            #fileContent = fileObj["Body"].read()
            #print('test3')

            #return{
            #    "statusCode": 200,
            #    "headers": {
            #        "Content-Type": "application/"+extension,
            #        "Content-Disposition": "attachment; filename={}".format(key)
            #    },
            #    "body": base64.b64encode(fileContent),
            #    "isBase64Encoded": True
            #}
            #return url
            
            url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': bucket, 'Key': key},ExpiresIn=600)
            # Create the response and add some extra content to support CORS
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": '*',
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Methods': 'GET'
                },
                "body": json.dumps({"urlstring":url})
            }

        except Exception as e:
            print("Error")

