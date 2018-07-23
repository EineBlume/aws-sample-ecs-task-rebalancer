# -*- coding: utf-8 -*-
import base64
import json
import logging
from time import sleep

import boto3

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Establish boto3 session
session = boto3.session.Session()
logger.info(f'SESSION: {session.region_name}')

ec2_client = session.client(service_name='ec2')
ecs_client = session.client(service_name='ecs')
asg_client = session.client('autoscaling')
sns_client = session.client('sns')
lambda_client = session.client('lambda')


def _get_cluster_name(ec2_instance_id):
    resp = ec2_client.describe_instance_attribute(InstanceId=ec2_instance_id, Attribute='userData')
    logger.info(f'Describe Instance UserData: {resp}')
    user_data = resp['UserData']
    user_data = base64.b64decode(user_data['Value'])
    tokens = map(lambda x: x.decode('utf-8'), user_data.split())
    for token in tokens:
        if token.find("ECS_CLUSTER") > -1:
            # Split and get the cluster name
            cluster_name = token.split('=')[1]
            return cluster_name
    return None


def _get_container_instance(ec2_instance_id, cluster_name=None):
    if not cluster_name:
        cluster_name = _get_cluster_name(ec2_instance_id)
    if not cluster_name:
        return None

    paginator = ecs_client.get_paginator('list_container_instances')
    pages = paginator.paginate(cluster=cluster_name)

    for page in pages:
        container_instances = page['containerInstanceArns']
        container_resp = ecs_client.describe_container_instances(cluster=cluster_name,
                                                                 containerInstances=container_instances)
        for container_instance in container_resp['containerInstances']:
            if container_instance['ec2InstanceId'] == ec2_instance_id:
                return container_instance
    return None


def _get_services(cluster_name):
    resp = ecs_client.list_services(cluster=cluster_name)
    if 'serviceArns' not in resp:
        return []
    return [
        serviceArn.split('/')[1]
        for serviceArn in resp['serviceArns']
    ]


def handler(event, context):
    logger.info(f'event: {event}')

    line = event['Records'][0]['Sns']['Message']
    message = json.loads(line)

    if 'retry_count' in message.keys() and message['retry_count'] >= 18:
        logger.error('Exceed Retry Count')
        return

    if 'Event' not in message.keys():
        logger.error('Not Found Event')
        return

    if 'autoscaling:EC2_INSTANCE_LAUNCH' not in message['Event']:
        logger.error('IS NOT EC2 AUTOSCALING')
        return

    ec2_instance_id = message['EC2InstanceId']
    logger.info(f'EC2 Instance ID: {ec2_instance_id}')
    if not ec2_instance_id:
        return

    cluster_name = _get_cluster_name(ec2_instance_id)
    logger.info(f'ClusterName: {cluster_name}')
    if not cluster_name:
        return

    container_instance = _get_container_instance(ec2_instance_id, cluster_name=cluster_name)
    logger.info(f'ContainerInstance: {container_instance}')
    if not container_instance:
        topic_arn = event['Records'][0]['Sns']['TopicArn']
        response = sns_client.list_subscriptions()
        for key in response['Subscriptions']:
            if key['TopicArn'] == topic_arn and key['Protocol'] == 'lambda':
                if 'retry_count' not in message:
                    message['retry_count'] = 1
                else:
                    message['retry_count'] += 1

                logger.info('Waiting %s seconds', 10)
                sleep(10)
                logger.info("Publish to SNS topic %s", topic_arn)
                resp = sns_client.publish(
                    TopicArn=topic_arn,
                    Message=json.dumps(message),
                    Subject='Publishing SNS message to invoke lambda again..'
                )
                logger.info(f'SNS Publish Resp: {resp}')
        return

    services = _get_services(cluster_name)
    if not services:
        logger.error('Not Found Services')
        return

    logger.info(f'Services: {services}')
    resp = ecs_client.describe_services(
        cluster=cluster_name,
        services=services,
    )

    services = resp['services']
    for service in services:
        logger.info(f'Service: {service["serviceName"]}')
        if service['desiredCount'] == 0:
            logger.info(f'Skip: desiredCount of {service["serviceName"]} is 0')
            continue
        deployments = service['deployments']
        if len(deployments) >= 2:
            logger.error(f'Now {service["serviceName"]} Deploying... Exit')
            continue

        task_definition = service['taskDefinition']
        ecs_client.update_service(
            cluster=cluster_name,
            service=service["serviceArn"],
            taskDefinition=task_definition,
            forceNewDeployment=True,
        )

        logger.info(f'Update Service {service["serviceName"]} forceNewDeployment...')
