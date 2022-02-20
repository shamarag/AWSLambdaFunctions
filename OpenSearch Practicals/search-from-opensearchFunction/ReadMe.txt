Read Me
--------
This lambda function search for a document indexed in opensearch based on content or name.

1. Give the correct end point details and index name (you want to search) in the search.py function

2. Create a deployment package.
	-- Create a new dir for the deployment package (deployment_package), copy the .py file to the folder and run the pip commands to package the external libraries.
		cd lambda_deployment
		pip install --target ./ requests
		pip install --target ./ requests_aws4auth
	-- Now create a lambda function in AWS Lambda and set a new IAM role with permission to ElasticSearch execution.
	-- Upload the zip folder (deployment package)
	-- Make sure you change the Runtime settings->handler name according to the name of the file in your deployment package where the Lambda function is located.

3. Set up permissions in open search to allow the lambda to write to the index.
	- Go to open search dashboard using the url and login using master user. 
	- Then go to security -> create a new role "s3-alldocsbucket-index-read-role" ->For Cluster permissions, add the "cluster_composite_ops_ro" action group -> For Index Permissions, add an index pattern "s3-alldocsbucket-index*" -> For index permissions, add the "read" action group.
	- Choose Create.
	Ref: https://opensearch.org/docs/latest/security-plugin/access-control/users-roles/
	

4. Create a lambda function event to test the function.
	-- Use query parameters
	e.g.
	{
	  "q": "Something"
	}