import boto3
import json
from django.dispatch import receiver
from django.db import models

from party.queue_name import return_queue_name
from party import serializers
from organization.models import Project
from spatial.serializers import SpatialUnitSerializer
from resources.serializers import ResourceSerializer

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=return_queue_name())


def get_updated_record_data(sender, instance, project, **kwargs):
    serializer, entity_type = get_serializer(sender)
    url = format_post_url(project.slug, entity_type)

    serializer = serializer(context={'search': True})
    updated_data = dict(serializer.to_representation(instance))

    message_in_queue = get_current_queue(
        project=project.slug,
        entity_type=sender.__name__)

    if message_in_queue:
        message = json.loads(message_in_queue.body)
        message_in_queue.delete()

        message_body = message['body']
        instance_index = {'index': {'_id': instance.id}}

        if instance_index in message_body:
            body_index = message_body.index(instance_index) + 1
            message_body[body_index] = updated_data
            updated_message = json.dumps(message)
            print('updated_message')
            return updated_message
        else:
            message_body.append(instance_index)
            message_body.append(updated_data)
            print('appended message')
            return json.dumps(message)

    else:
        message_body = {
            "POST": url,
            "body": [
                {"index": {"_id": instance.id}},
                updated_data,
            ]
        }

        return json.dumps(message_body)


def get_serializer(sender):
    if sender.__name__ == 'Party':
        serializer = serializers.PartySerializer
        entity_type = 'party'

    if sender.__name__ == 'TenureRelationship':
        serializer = serializers.TenureRelationshipWriteSerializer
        entity_type = 'tenure_rel'

    if sender.__name__ == 'SpatialUnit':
        serializer = SpatialUnitSerializer
        entity_type = 'location'

    if sender.__name__ == 'Resource':
        serializer = ResourceSerializer
        entity_type = 'resource'

    return serializer, entity_type


def get_current_queue(project, entity_type):
    print('project: ', project)
    print('entity_type: ', entity_type)
    messages = queue.receive_messages(
        MessageAttributeNames=['Project', 'EntityType'],
        MaxNumberOfMessages=10)
    print("Are there messages? ", len(messages))
    for message in messages:
        if message.message_attributes:
            print("message_attributes: ", message.message_attributes)

            msg_atrs = message.message_attributes
            if (msg_atrs.get('Project').get('StringValue') == project and
               msg_atrs.get('EntityType').get('StringValue') == entity_type):
                print('A message exists for project {}, entity {}.'.format(
                    project, entity_type))
                return message
    return None


def format_post_url(project_slug, record_type):
    url = "/{project_slug}/{record_type}/_bulk?pretty".format(
        project_slug=project_slug,
        record_type=record_type)
    return url


@receiver(models.signals.post_save)
def update_search_index(sender, instance, **kwargs):
    model_list = ('SpatialUnit', 'Resource', 'Party', 'TenureRelationship')

    sender = sender.__base__ if sender._deferred else sender
    if sender.__name__ not in model_list:
        return

    if hasattr(instance, 'project'):
        project = instance.project
    else:
        project = Project.objects.get(id=instance.project_id)

    message_body = get_updated_record_data(sender, instance, project)
    print('final message_body: ', message_body)

    if message_body:
        queue.send_message(
            MessageAttributes={
                'Project': {
                    'StringValue': project.slug,
                    'DataType': 'String'
                },
                'EntityType': {
                    'StringValue': sender.__name__,
                    'DataType': 'String'
                }
            },
            MessageGroupId=project.slug,
            MessageBody=message_body,
        )

models.signals.pre_delete.connect(update_search_index)
