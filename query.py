from urllib import response
import boto3
from botocore.exceptions import ClientError

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

ec2 = boto3.client('ec2')

# response = ec2.describe_vpcs()

# vpcId = ((response['Vpcs'][0]['VpcId']))
# try:
#     response = ec2.create_security_group(GroupName='vnc_sg', Description='test', VpcId=vpcId)
#     security_group_id = response['GroupId']
#     print('Security Group Created %s in vpc %s.' % (security_group_id, vpcId))

#     data = ec2.authorize_security_group_ingress(
#         GroupId=security_group_id,
#         IpPermissions=[
#             {'IpProtocol': 'tcp',
#                 'FromPort': 22,
#                 'ToPort': 22,
#                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
#             {'IpProtocol': 'tcp',
#                 'FromPort': 80,
#                 'ToPort': 80,
#                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
#         ])
#     print('Ingress Successfully Set %s' % data)
# except ClientError as e:
#     print(e)

response = ec2.authorize_security_group_ingress(
    GroupId='sg-084672eaac289697c',
    IpPermissions=[
        {
            'FromPort': 6080,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '69.12.21.94/32',
                    'Description': 'VNC Client access to my PC',
                },
            ],
            'ToPort': 6081,
        },
    ],
)

print(response)

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