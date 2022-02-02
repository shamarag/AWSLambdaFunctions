Loading streaming data from Amazon S3
-----------------------------------------
src: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/integrations.html

1. Create a s3 bucket and create a folder called logs in it.

2. Create a new domain in open search.

3. Create a lambda deployment package with the python source code to create "documents"(send POST request) with log file details in the specific s3 bucket->logs folder.
	-- Used the code in https://docs.aws.amazon.com/opensearch-service/latest/developerguide/integrations.html -> Loading streaming data from Amazon S3
	-- Update the "host" in the code 
		host = 'https://search-masterdocs-eoqkoj4s3xvpm5d43wjrpgdiue.us-east-2.es.amazonaws.com'
	-- Update the "index" in the code
		index = 'lambda-s3-log-index' //name of index you want to create
	-- Create a new dir for the deployment package (deployment_package), copy the .py file to the folder and run the pip commands to package the external libraries.
		cd lambda_deployment
		pip install --target ./ requests
		pip install --target ./ requests_aws4auth
	-- Now create a lambda function in AWS Lambda and set a new IAM role with permission to ElasticSearch execution and S3 execution.
	-- Upload the zip folder (deployment package)
	-- Make sure you change the Runtime settings->handler name according to the name of the file in your deployment package where the Lambda function is located.


4. Create a s3 trigger to be triggered when a new file arrive in the s3 bucket logs folder.
- After you create the function, you must add a trigger. For this example, we want the code to run whenever a log file arrives in an S3 bucket:
	- Choose Add trigger and select S3.
	- Choose your bucket.
	- For Event type, choose PUT.
	- For Prefix, type logs/.
	- For Suffix, type .log.
	- Acknowledge the recursive invocation warning and choose Add.

5. If you want to see the data rows(documents) of the index you are creating as part of the lambda function in OpenSearch dashboard -> Create a new index pattern with name of the index you have specified in the lambda function
	
6. Set up permissions in open search to allow the lambda to write to the index.
Easy solution(but not secure):
-----------------------------
	- Go to open search dashboard using the url and login using master user. 
	Then go to security-> explore existing roles -> select "all_access" role ->mapped users -> manage mapping -> set the Lambda IAM role's ARN in the Backend roles and mapped

Better solution
----------------
** Ideally need to create a new role and give specific index permission to the new role and then map the lambda function backend role to it.
	- Go to open search dashboard using the url and login using master user. 
	- Then go to security-> create a new role "lambda-s3-log-index-role" ->For Cluster permissions, add the cluster_composite_ops action group -> For Index Permissions, add an index pattern "lambda-s3-log-index*" -> For index permissions, add the "write" action group.
	- Choose Create.

Ref: https://opensearch.org/docs/latest/security-plugin/access-control/users-roles/

7. Now upload a log file sample.log with the following entries to the logs folder in the specific s3 bucket.
12.345.678.90 - [10/Oct/2000:13:55:36 -0700] "PUT /some-file.jpg"
12.345.678.91 - [10/Oct/2000:14:56:14 -0700] "GET /some-file.jpg"

8. Now to check if the documents are added, run the following rest api cmd on open search.
GET lambda-s3-log-index/_search
{
    "query": {
        "match_all": {}
    }
}
-------------OR------------------------
GET /lambda-s3-log-index/_search?pretty

It should show all rows(documents) added to the index.