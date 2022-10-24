from ipaddress import ip_address
from urllib import response
import boto3
from botocore.exceptions import ClientError

from asgiref.sync import sync_to_async
import time
# s3 = boto3.resource('s3')
# Print out bucket names
# for bucket in s3.buckets.all():
#     print(bucket.name)



# Get the queue. This returns an SQS.Queue instance
# try:
#     # Get the service resource
#     sqs = boto3.resource('sqs')
#     queue = sqs.get_queue_by_name(QueueName='test')

#     # You can now access identifiers and attributes
#     print(queue.url)
#     print(queue.attributes.get('DelaySeconds'))
# except Exception as e:
#     print("Queue does not exist" , str(e))

def create_security_group(group_name):

    ec2 = boto3.client('ec2')
    security_group_id = ''
    response = ec2.describe_vpcs()
    vpcId = ((response['Vpcs'][0]['VpcId']))
    try:
        response = ec2.create_security_group(GroupName=group_name, Description=group_name, VpcId=vpcId)
        print(response)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpcId))

        return security_group_id
    except ClientError as e:
        print(e)
    return security_group_id

def change_securtiy_group(group_id,ip,port):
    ec2 = boto3.client('ec2')
    try:
        data = ec2.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges': [{'CidrIp': f'{ip}/32'}]}
            ])
        print('Security group changed as  %s' % data)
    except ClientError as e:
        print(e)
# response = ec2.authorize_security_group_ingress(
#     GroupId=sucurity_group_id,
#     IpPermissions=[
#         {
#             'FromPort': 6080,
#             'IpProtocol': 'tcp',
#             'IpRanges': [
#                 {
#                     'CidrIp': '69.12.21.94/32',
#                     'Description': 'VNC Client access to my PC',
#                 },
#             ],
#             'ToPort': 6081,
#         },
#     ],
# )

# print(response)

# response = ec2.revoke_security_group_ingress(
#     GroupId='sg-084672eaac289697c',
#     IpPermissions=[
#         {
#             'FromPort': 6080,
#             'IpProtocol': 'tcp',
#             'IpRanges': [
#                 {
#                     'CidrIp': '69.12.21.94/32',
#                     'Description': 'VNC Client access to my PC',
#                 },
#             ],
#             'ToPort': 6081,
#         },
#     ],
# )

# print(response)


# ec2 = boto3.resource('ec2')
# try:
#     instance_params = {
#                 'ImageId': " ami-08f5f8ed43b9c257c", 'InstanceType': "t2.micro", 'KeyName': "client"
#             }
#     instances = ec2.create_instances(
#             ImageId="ami-08f5f8ed43b9c257c",
#             MinCount=1,
#             MaxCount=1,
#             InstanceType="t2.micro",
#             KeyName="client"
#         )
# except ClientError as e:
#     print(e)

def create_instance(instance_name,security_group_id,port):
    instance_id =''
    ec2 = boto3.client('ec2')
    proxy_ip = get_public_ip('i-0d7f446f52790b622')
    com = f'sudo novnc --listen {port} --vnc {proxy_ip}:{port-100}'
    #print(com)
    bash = '#!/bin/bash\n'+com
    try:
        response = ec2.run_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {

                    'DeleteOnTermination': True,
                    'VolumeSize': 8,
                    'VolumeType': 'gp2'
                },
            },
        ],
        ImageId='ami-08f5f8ed43b9c257c',
        InstanceType='t2.micro',
        KeyName='client',
        MaxCount=1,
        MinCount=1,
        Monitoring={
            'Enabled': False
        },
        SecurityGroupIds=[
            security_group_id,
        ],
        UserData=bash,
        TagSpecifications=[
                {   
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instance_name
                        },
                    ]
                },
            ],
        )
        print(response)
        instance_id = response['Instances'][0]['InstanceId']
        return instance_id
    except ClientError as e:
        print(e)

def run_command(instance_id,port):
    
    
    ssm_client = boto3.client('ssm')
    response =  ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': [f'novnc --listen {port} --vnc 54.235.238.105:{port-100}']}, )

    command_id = response['Command']['CommandId']
    output = ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id,
        )
    print(output)
#instance_id = 'i-0807d0d82361cae36'
def get_public_ip(instance_id):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]

    if 'PublicIpAddress' in instance:
        public_ip = instance['PublicIpAddress']
        #print(public_ip)
        return public_ip
def terminate_instance(instance_id):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.terminate_instances(InstanceIds=[instance_id])
        if response['TerminatingInstances'][0]['CurrentState']['Code'] == 32:
            return True   
    except ClientError as e:
        print(e)


async def delete_security_group(group_id):
    ec2 = boto3.client('ec2')
    security_group_id = group_id
    flag = False
    while flag == False:
        try:
            response = ec2.delete_security_group(GroupId=security_group_id)
            
            flag = True
            print("Security Group Deleted")
            
        except ClientError as e:
            print(e)
        time.sleep(10)



