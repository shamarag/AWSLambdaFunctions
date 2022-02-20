import boto3
import json
import requests
from requests_aws4auth import AWS4Auth

region = 'us-east-2'  # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-masterdocs-eoqkoj4s3xvpm5d43wjrpgdiue.us-east-2.es.amazonaws.com'  # the OpenSearch Service domain, including https://
index = 's3-alldocsbucket-index'
type = '_search'
url = host + '/' + index + '/' + type

headers = {"Content-Type": "application/json"}

s3 = boto3.resource('s3')

# Lambda execution starts here
def lambda_handler(event, context):
    searchInput = event['queryStringParameters']['q']
    searchDocType = event['queryStringParameters']['type']
    
    #print(searchInput)
    #print(searchDocType)
    
    
    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    
    if searchDocType.lower() != "all":
        query = {
            
          "size": 25,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": searchInput,
                            "fields": ["name^4", "content^2"]
                        }
                    },
                    "filter": {
                        "term": {
                            "type": searchDocType
                        }
                    }
                }
            }  
            
     
        }
    
    else:
    
        query = {
            "size": 25,
            "query": {
                "multi_match": {
                    "query": event['queryStringParameters']['q'],
                    "fields": ["name^4", "content^2"]
                }
            }
        }
    
    # Make the signed HTTP request
    try:
        #r = requests.get(host + '/' + index + '/' + '_search', auth=awsauth, headers=headers, data=json.dumps(query))
        r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
        
        # Create the response and add some extra content to support CORS
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": '*',
                'Content-Type': 'application/json',
                'Access-Control-Allow-Methods': 'GET'
            },
            "isBase64Encoded": False
        }
        print(r.text)
        # Add the search results to the response
        response['body'] = r.text
    except Exception as e:
        print("Error")
        response['body'] = r.text
        
    
    return response