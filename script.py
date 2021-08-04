#!/usr/bin/python3

import sys
import boto3

if len(sys.argv) != 4:
	print("Usage:")
	print(f"{' '*4} {sys.argv[0]} [PORT] [VPC] [TAGNAME Key:Value] ")
	sys.exit(1)

PORT = int(sys.argv[1])
KEY,VALUE = str(sys.argv[3]).split(":")
VPC = str(sys.argv[2])
temp = {}
instanceids= []
tg_name = 'New-target-grp'


alb = boto3.client('elbv2',region_name='us-east-1')
client = boto3.client('ec2',region_name='us-east-1')

response = client.describe_instances(
    Filters=[
        {
            'Name': str('tag:'+KEY),
            'Values': [
                VALUE,
            ]
        },
    ]).get('Reservations', [])
instances = sum([[i for i in r['Instances']]for r in response], [])
for instance in instances:
	temp['Id']=instance['InstanceId']
	instanceids.append(temp.copy())

response = alb.create_target_group( Name=tg_name, Protocol='HTTP', Port=PORT, VpcId=VPC,TargetType='instance')

arn = response['TargetGroups'][0]['TargetGroupArn']

response = alb.register_targets(TargetGroupArn=arn,Targets=instanceids)
if response['ResponseMetadata']['HTTPStatusCode'] == 200:
	temp =[i["Id"] for i in instanceids]
	print(f"Completed: New target group named {tg_name} created and targets {temp} attached to it.")
