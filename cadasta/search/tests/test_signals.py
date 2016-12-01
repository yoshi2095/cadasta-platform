import json
from django.test import TestCase

from core.tests.utils.cases import UserTestCase
from party.models import Party, TenureRelationship, TenureRelationshipType
from organization.models import Project
from resources.models import Resource
from spatial.models import SpatialUnit

from party.tests.factories import PartyFactory, TenureRelationshipFactory
from organization.tests.factories import ProjectFactory
from resources.tests.factories import ResourceFactory
from spatial.tests.factories import SpatialUnitFactory

from search import signals as s


class SignalsTest(UserTestCase, TestCase):
    def test_format_send_message(self):
        # if sender not a Record model, return none
        sender = Party
        instance = PartyFactory.create()

        response = s._format_send_message(sender, instance, "POST")
        response = json.loads(response)

        assert response["POST"] == "/{}/party/_bulk?pretty".format(
            instance.project.slug)
        assert response["body"] == [{"index": {"_id": "{}".format(
            instance.id)}}]

        instance_id = instance.id
        slug = instance.project.slug

        response = s._format_send_message(sender, instance, "DELETE")
        instance.delete()
        response = json.loads(response)

        assert response["DELETE"] == (
            "/{project_slug}/party/"
            "{instance_id}?pretty").format(
            project_slug=slug,
            instance_id=instance_id)

    def test_format_send_message_returns_none(self):
        # if sender not a Record model, return none
        sender = Project
        instance = ProjectFactory.create()
        method = "POST"

        response = s._format_send_message(sender, instance, method)
        assert response is None

    def test_format_sender(self):
        sender = Party
        response = s._format_sender(sender)
        assert response == Party

        sender = TenureRelationship
        response = s._format_sender(sender)
        assert response == TenureRelationship

        sender = SpatialUnit
        response = s._format_sender(sender)
        assert response == SpatialUnit

        sender = Resource
        response = s._format_sender(sender)
        assert response == Resource

    def test_format_sender_deferred(self):
        PartyFactory.create()
        sender_deferred = type(Party.objects.defer('attributes').first())
        assert sender_deferred != Party

        response = s._format_sender(sender_deferred)
        assert response == Party
        assert response != sender_deferred

        SpatialUnitFactory.create()
        sender_deferred = type(SpatialUnit.objects.defer('attributes').first())
        assert sender_deferred != SpatialUnit

        response = s._format_sender(sender_deferred)
        assert response == SpatialUnit
        assert response != sender_deferred

        TenureRelationshipType.objects.create()
        TenureRelationshipFactory.create()
        sender_deferred = type(
            TenureRelationship.objects.defer('party').first())
        assert sender_deferred != TenureRelationship

        response = s._format_sender(sender_deferred)
        assert response == TenureRelationship
        assert response != sender_deferred

        ResourceFactory.create()
        sender_deferred = type(Resource.objects.defer('description').first())
        assert sender_deferred != Resource

        response = s._format_sender(sender_deferred)
        assert response == Resource
        assert response != sender_deferred

    def test_entity_type(self):
        sender = Party
        response = s._format_entity_type(sender)
        assert response == 'party'

        sender = TenureRelationship
        response = s._format_entity_type(sender)
        assert response == 'tenure_rel'

        sender = SpatialUnit
        response = s._format_entity_type(sender)
        assert response == 'location'

        sender = Resource
        response = s._format_entity_type(sender)
        assert response == 'resource'

    def test_format_project(self):
        instance = PartyFactory.create()
        response = s._format_project(instance)
        assert response == instance.project

        instance = SpatialUnitFactory.create()
        response = s._format_project(instance)
        assert response == instance.project

        instance = TenureRelationshipFactory.create()
        response = s._format_project(instance)
        assert response == instance.project

        instance = ResourceFactory.create()
        response = s._format_project(instance)
        assert response == instance.project

    def test_format_url_post(self):
        instance = PartyFactory.create()
        response = s._format_url(
            'test-project', 'party', instance.id, 'POST')
        assert response == "/test-project/party/_bulk?pretty"

        instance = SpatialUnitFactory.create()
        response = s._format_url(
            'test-project', 'location', instance.id, 'POST')
        assert response == "/test-project/location/_bulk?pretty"

        instance = TenureRelationshipFactory.create()
        response = s._format_url(
            'test-project', 'tenure_rel', instance.id, 'POST')
        assert response == "/test-project/tenure_rel/_bulk?pretty"

        instance = ResourceFactory.create()
        response = s._format_url(
            'test-project', 'resource', instance.id, 'POST')
        assert response == "/test-project/resource/_bulk?pretty"

    def test_format_url_delete(self):
        instance = PartyFactory.create()
        response = s._format_url(
            'test-project', 'party', instance.id, 'DELETE')
        assert response == "/test-project/party/{}?pretty".format(
            instance.id)

        instance = SpatialUnitFactory.create()
        response = s._format_url(
            'test-project', 'location', instance.id, 'DELETE')
        assert response == "/test-project/location/{}?pretty".format(
            instance.id)

        instance = TenureRelationshipFactory.create()
        response = s._format_url(
            'test-project', 'tenure_rel', instance.id, 'DELETE')
        assert response == "/test-project/tenure_rel/{}?pretty".format(
            instance.id)

        instance = ResourceFactory.create()
        response = s._format_url(
            'test-project', 'resource', instance.id, 'DELETE')
        assert response == "/test-project/resource/{}?pretty".format(
            instance.id)

    def test_format_message_body_post(self):
        instance = PartyFactory.create()
        url = s._format_url(
            'test-project', 'party', instance.id, 'POST')
        response = s._format_message_body(url, instance.id, 'POST')
        response = json.loads(response)

        assert response['POST'] == url
        assert response['body'] == [{"index": {"_id": "{}".format(
            instance.id)}}]

        instance = SpatialUnitFactory.create()
        url = s._format_url(
            'test-project', 'location', instance.id, 'POST')
        response = s._format_message_body(url, instance.id, 'POST')
        response = json.loads(response)

        assert response['POST'] == url
        assert response['body'] == [{"index": {"_id": "{}".format(
            instance.id)}}]

        instance = TenureRelationshipFactory.create()
        url = s._format_url(
            'test-project', 'tenure_rel', instance.id, 'POST')
        response = s._format_message_body(url, instance.id, 'POST')
        response = json.loads(response)

        assert response['POST'] == url
        assert response['body'] == [{"index": {"_id": "{}".format(
            instance.id)}}]

        instance = ResourceFactory.create()
        url = s._format_url(
            'test-project', 'resource', instance.id, 'POST')
        response = s._format_message_body(url, instance.id, 'POST')
        response = json.loads(response)

        assert response['POST'] == url
        assert response['body'] == [{"index": {"_id": "{}".format(
            instance.id)}}]

    def test_format_message_body_delete(self):
        instance = PartyFactory.create()
        url = s._format_url(
            'test-project', 'party', instance.id, 'DELETE')
        response = s._format_message_body(url, instance.id, 'DELETE')
        response = json.loads(response)
        assert response["DELETE"] == url

        instance = SpatialUnitFactory.create()
        url = s._format_url(
            'test-project', 'location', instance.id, 'DELETE')
        response = s._format_message_body(url, instance.id, 'DELETE')
        response = json.loads(response)
        assert response["DELETE"] == url

        instance = TenureRelationshipFactory.create()
        url = s._format_url(
            'test-project', 'tenure_rel', instance.id, 'DELETE')
        response = s._format_message_body(url, instance.id, 'DELETE')
        response = json.loads(response)
        assert response["DELETE"] == url

        instance = ResourceFactory.create()
        url = s._format_url(
            'test-project', 'resource', instance.id, 'DELETE')
        response = s._format_message_body(url, instance.id, 'DELETE')
        response = json.loads(response)
        assert response["DELETE"] == url
