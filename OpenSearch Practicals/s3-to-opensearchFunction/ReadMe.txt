Read Me
--------
This solution indexes .txt and .pdf files in a given s3 bucket in OpenSearch.
If you run this mutiple times, it will keep adding duplicated entries to opensearch index.

1. Create a new OpenSearch domain

2. Give the correct end point details and index name (you wish) and bucket details in the sample.py function

3. In the sample.py function the file content, name, size, last modified dates are indexed. An index is created for each file in the bucket (If you keep calling this function it will keep adding document entries in opensearch, for the same files in the bucket. Which will create duplicated records.)

4. Create a deployment package.
	-- Create a new dir for the deployment package (deployment_package), copy the .py file to the folder and run the pip commands to package the external libraries.
		cd lambda_deployment
		pip install --target ./ requests
		pip install --target ./ requests_aws4auth
	-- Now create a lambda function in AWS Lambda and set a new IAM role with permission to ElasticSearch execution and S3 execution.
	-- Upload the zip folder (deployment package)
	-- Make sure you change the Runtime settings->handler name according to the name of the file in your deployment package where the Lambda function is located.


5. If you want to see the data rows(documents) of the index you are creating as part of the lambda function in OpenSearch dashboard -> Create a new index pattern with name of the index you have specified in the lambda function

6. Set up permissions in open search to allow the lambda to write to the index.
	- Go to open search dashboard using the url and login using master user. 
	- Then go to security-> create a new role "s3-alldocsbucket-index-role" ->For Cluster permissions, add the cluster_composite_ops action group -> For Index Permissions, add an index pattern "s3-alldocsbucket-index*" -> For index permissions, add the "write" and "create_index" action groups.
	- Choose Create.
	Ref: https://opensearch.org/docs/latest/security-plugin/access-control/users-roles/
	
7. Now upload a .txt/.pdf file in the specific s3 bucket.

8. Now to check if the documents are added, run the following rest api cmd on open search.
GET s3-alldocsbucket-index/_search
{
    "query": {
        "match_all": {}
    }
}