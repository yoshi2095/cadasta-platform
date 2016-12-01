import boto3
import json
from django.dispatch import receiver
from django.db import models

from party.queue_name import return_queue_name
from organization.models import Project

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=return_queue_name())


@receiver(models.signals.post_save)
def update_search_index(sender, instance, **kwargs):
    _format_send_message(sender, instance, 'POST')


@receiver(models.signals.pre_delete)
def delete_search_index(sender, instance, **kwargs):
    _format_send_message(sender, instance, 'DELETE')


def _format_send_message(sender, instance, method):
    sender = _format_sender(sender)
    if sender is None:
        return

    entity_type = _format_entity_type(sender)
    project = _format_project(instance)
    url = _format_url(project.slug, entity_type, instance.id, method)
    message_body = _format_message_body(url, instance.id, method)

    if message_body:
        queue.send_message(
            MessageGroupId=project.slug,
            MessageBody=message_body
        )
        return message_body


def _format_sender(sender):
    model_list = ('SpatialUnit', 'Resource', 'Party', 'TenureRelationship')

    sender = sender.__base__ if sender._deferred else sender
    if sender.__name__ in model_list:
        return sender


def _format_entity_type(sender):
    if sender.__name__ == 'Party':
        entity_type = 'party'

    if sender.__name__ == 'TenureRelationship':
        entity_type = 'tenure_rel'

    if sender.__name__ == 'SpatialUnit':
        entity_type = 'location'

    if sender.__name__ == 'Resource':
        entity_type = 'resource'

    return entity_type


def _format_project(instance):
    if hasattr(instance, 'project'):
        project = instance.project
    else:
        project = Project.objects.get(id=instance.project_id)

    return project


def _format_url(project_slug, entity_type, instance_id, method):
    if method == 'POST':
        url = "/{project_slug}/{record_type}/_bulk?pretty".format(
            project_slug=project_slug,
            record_type=entity_type)

    elif method == 'DELETE':
        url = "/{project_slug}/{entity_type}/{instance_id}?pretty".format(
            project_slug=project_slug,
            entity_type=entity_type,
            instance_id=instance_id
            )

    return url


def _format_message_body(url, instance_id, method):
    if method == 'POST':
        message_body = {
            "POST": url,
            "body": [
                {"index": {"_id": instance_id}},
            ]
        }

    elif method == 'DELETE':
        message_body = {
            "DELETE": url,
        }

    return json.dumps(message_body)
