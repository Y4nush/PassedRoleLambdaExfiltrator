# PassedRoleLambdaExfiltrator
 PassedRoleLambdaExfiltrator: An AWS tool to detect and exploit iam:PassRole with Lambda for privilege escalation. It enumerates vulnerable roles, deploys a function, and sends credentials to an ngrok endpoint using an HTTP POST request.

## Description
PassedRoleLambdaExfiltrator is an AWS security testing tool tailored to detect and automate the exploitation of the iam:PassRole permission alongside AWS Lambda functions. Its primary goal is to pinpoint potential privilege escalation vulnerabilities. If an executing user holds the lambda, iam:Read, and iam:PassRole permissions, the tool identifies this potential gap and demonstrates its exploitability. It accomplishes this by listing assumable Lambda roles, deploying a sample function, and subsequently exfiltrating the AWS environment credentials to a designated ngrok endpoint.


## Features
* Scans for lambda, iam:Read, and iam:PassRole permissions.
* Enumerates roles assumable by Lambda functions.
* Deploys Lambda functions under user-selected roles.
* Automatically exfiltrates the lambda secrets from the AWS environment variables to an ngrok endpoint.

## Usage
```
pip install -r requirements.txt
```
```
python PassedRoleLambdaExfiltrator.py [--access_key_id YOUR_ACCESS_KEY] [--secret_access_key YOUR_SECRET_KEY] [--profile AWS_CLI_PROFILE]
```
Follow the on-screen instructions to select roles and regions for Lambda deployment.

## Demo
![image](https://github.com/Y4nush/PassedRoleLambdaExfiltrator/assets/104491821/3aad5996-7d2e-42c2-9ac5-b43a8ae4aad8)
![image](https://github.com/Y4nush/PassedRoleLambdaExfiltrator/assets/104491821/5a80a522-2743-45e7-a905-3820369a58a2)
![image](https://github.com/Y4nush/PassedRoleLambdaExfiltrator/assets/104491821/818c3a3d-7315-4ec5-b447-ccb2b5c90f76)



