# PassedRoleLambdaExfiltrator
An AWS offensive security tool designed to detect and exploit the iam:PassRole with Lambda for privilege escalation. It enumerates vulnerable roles, deploys a function, and sends credentials to an ngrok endpoint using an HTTP POST request by invoking the malicious lambda function.

## Overview
PassedRoleLambdaExfiltrator is an AWS security testing tool designed to detect and automate the exploitation of the iam:PassRole permission in conjunction with AWS Lambda functions. Its primary objective is to identify potential privilege escalation vulnerabilities within an AWS environment. The tool specifically targets situations where a user possesses both the lambda and iam:PassRole permissions, highlighting this potential security gap and demonstrating its exploitability. It achieves this by listing assumable Lambda roles, deploying a sample Lambda function, and subsequently exfiltrating AWS environment credentials to a designated ngrok endpoint.

## Exploitation of `iam:PassRole` Permission
The primary focus of this tool is to demonstrate the exploitation of the iam:PassRole permission in combination with AWS Lambda permissions. The Lambda function created by the tool's deployment is intentionally configured to assume a specified role and then send the assumed role's credentials via an HTTP POST request to a server controlled by the attacker. This method showcases the potential for privilege escalation, as an attacker with access to these credentials could potentially gain unauthorized access to resources within the AWS environment.

## Features
* Scans for lambda, iam:Read, and iam:PassRole permissions.
* Enumerates roles assumable by Lambda functions.
* Deploys Lambda functions under user-selected roles.
* Automatically exfiltrates the lambda secrets from the AWS environment variables to an ngrok endpoint.

## Usage
```bash
git clone https://github.com/Y4nush/PassedRoleLambdaExfiltrator.git
```
```bash
cd PassedRoleLambdaExfiltrator
```
```bash
pip install -r requirements.txt
```
```bash
python PassedRoleLambdaExfiltrator.py [--access_key_id YOUR_ACCESS_KEY] [--secret_access_key YOUR_SECRET_KEY] [--profile AWS_CLI_PROFILE]
```
Follow the on-screen instructions to select roles and regions for Lambda deployment.

## Demo
![image](https://github.com/Y4nush/PassedRoleLambdaExfiltrator/assets/104491821/aeeafac8-7f76-4644-a7ca-23264887a1bf)
![image](https://github.com/Y4nush/PassedRoleLambdaExfiltrator/assets/104491821/c0b80f40-07ec-4d6c-bed9-e7c761810f06)
![Untitled](https://github.com/Y4nush/PassedRoleLambdaExfiltrator/assets/104491821/064d4f28-15da-4952-9d1e-c42deedfbb35)



