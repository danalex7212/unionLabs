import json
import boto3
import re
import time
from botocore.exceptions import ClientError
import psycopg2
ec2 = boto3.client('ec2')
sqs = boto3.client('sqs')
host = 'unionlabs.ckptn7db2lof.us-east-1.rds.amazonaws.com'
username = 'postgres'
password = 'rootroot'
database = 'test'


def lambda_handler(event, context):

    # TODO implement
    message = event['Records'][0]['body']
    # print(event[])
    action = re.findall(r'\b\w+\b', message)[0]

    if action == 'deleteInstance':
        resource = re.findall(r'\b\w+\b', message)[2]
        print("deleting Instance...")
        instance_id = 'i-'+resource
        try:

            response = ec2.terminate_instances(InstanceIds=[instance_id])
            if response['TerminatingInstances'][0]['CurrentState']['Code'] == 32:
                return {
                    'statusCode': 200,
                    'body': json.dumps('Hello from Lambda!')
                }
        except ClientError as e:
            print(e)
    if action == 'deleteSg':
        resource = re.findall(r'\b\w+\b', message)[2]
        print('deleting security group...')
        sg_id = 'sg-'+resource
        try:
            response = ec2.delete_security_group(GroupId=sg_id)
            print("Security Group Deleted")

        except ClientError as e:
            print(e)
            print('Sending message to deletSg Queue')
            message = 'deleteSg '+sg_id
            message += ' '+str(int(time.time()*10e6))
            response = sqs.send_message(
                QueueUrl='https://sqs.us-east-1.amazonaws.com/780492718645/deleteSg.fifo',
                MessageBody=message,
                MessageGroupId='unionLabs'
            )
    if action == 'createInstance':

        numOpenInst = int(re.findall(r'\b\w+\b', message)[1])
        new_port = int(re.findall(r'\b\w+\b', message)[2])
        port_id = int(re.findall(r'\b\w+\b', message)[3])
        print('creating instance...')
        new_sg_id = create_security_group(f'client{numOpenInst+1}')
        new_instance_id = create_instance(
            f'client{numOpenInst+1}', new_sg_id, new_port)
        print("new instance and security group created")
        con = psycopg2.connect(host=host, database=database,
                               user=username, password=password)
        cur = con.cursor()

        cur.execute("INSERT INTO aws_openinstance (name, instance_id, port_id, sg_id) VALUES (%s, %s, %s, %s)",
                    (f'client{numOpenInst+1}', new_instance_id, port_id, new_sg_id))
        con.commit()
        con.close()
    return {}


def create_instance(instance_name, security_group_id, port):
    instance_id = ''
    ec2 = boto3.client('ec2')
    proxy_ip = get_public_ip('i-0d7f446f52790b622')
    com = f'sudo novnc --listen {port} --vnc {proxy_ip}:{port}'
    # print(com)
    bash = '#!/bin/bash\n'+com
    print(bash)
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


def get_public_ip(instance_id):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]

    if 'PublicIpAddress' in instance:
        public_ip = instance['PublicIpAddress']
        # print(public_ip)
        return public_ip


def create_security_group(group_name):

    ec2 = boto3.client('ec2')
    security_group_id = ''
    response = ec2.describe_vpcs()
    vpcId = ((response['Vpcs'][0]['VpcId']))
    try:
        response = ec2.create_security_group(
            GroupName=group_name, Description=group_name, VpcId=vpcId)
        print(response)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' %
              (security_group_id, vpcId))

        return security_group_id
    except ClientError as e:
        print(e)
    return security_group_id
