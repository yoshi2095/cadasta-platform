from django.test import TestCase
import boto3
from moto import mock_sqs
from party.tests.factories import PartyFactory


class SignalsTest(TestCase):
    @mock_sqs
    def test_boto3_get_queue(self):
        sqs = boto3.resource('sqs', region_name='us-west-2')
        new_queue = sqs.create_queue(QueueName='test-queue')
        new_queue.should_not.be.none
        new_queue.should.have.property('url').should.contain('test-queue')
