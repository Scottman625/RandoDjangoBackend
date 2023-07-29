import boto3
from decouple import config
import json
import os

# Initialize a new session using your AWS credentials
session = boto3.Session(
    aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
    region_name='ap-northeast-1'  # or any other AWS region where you want to create the Identity Pool
)

# Initialize the Cognito Identity client
cognito = session.client('cognito-identity')

# Create a new Identity Pool
response = cognito.create_identity_pool(
    IdentityPoolName='MyIdentityPool',
    AllowUnauthenticatedIdentities=True  # or False depending on your needs
)

print(response['IdentityPoolId'])



# Initialize the IAM client
iam = session.client('iam')

# Create a new IAM role
role_response = iam.create_role(
    RoleName='MyIdentityPoolRole',
    AssumeRolePolicyDocument=json.dumps({
        'Version': '2012-10-17',
        'Statement': [{
            'Effect': 'Allow',
            'Principal': {'Federated': 'cognito-identity.amazonaws.com'},
            'Action': 'sts:AssumeRoleWithWebIdentity',
            'Condition': {'StringEquals': {'cognito-identity.amazonaws.com:aud': response['IdentityPoolId']}}
        }]
    })
)

# Attach the necessary policies to the IAM role
# Replace 'S3BucketName' with your actual S3 bucket name
iam.attach_role_policy(
    RoleName='MyIdentityPoolRole',
    PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
)

# Update the Identity Pool to use the new IAM role
cognito.set_identity_pool_roles(
    IdentityPoolId=response['IdentityPoolId'],
    Roles={
        'authenticated': role_response['Role']['Arn'],
        'unauthenticated': role_response['Role']['Arn'],
    }
)
