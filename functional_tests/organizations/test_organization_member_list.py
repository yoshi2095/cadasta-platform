from base import FunctionalTest
from fixtures import load_test_data
from fixtures.common_test_data_2 import get_test_data
from pages.OrganizationMemberList import OrganizationMemberListPage
from pages.Organization import OrganizationPage
from pages.OrganizationMember import OrganizationMemberPage
from pages.Login import LoginPage

from accounts.tests.factories import UserFactory
from organization.models import OrganizationRole
from core.tests.factories import PolicyFactory


class OrganizationMemberListTest(FunctionalTest):
    def setUp(self):
        super().setUp()
        PolicyFactory.load_policies()
        test_objs = load_test_data(get_test_data())

        self.org = test_objs['organizations'][0]
        self.archived_org = test_objs['organizations'][2]

    def test_registered_user_view(self):
        """A registered admin user can view the member list."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationMemberListPage(self, self.org.slug)
        page.go_to()

        title = self.panel_title()
        assert title == "Members".upper()

    def test_adding_members(self):
        """A registered admin user can add members to an organization."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationMemberListPage(self, self.org.slug)
        page.go_to()

        page.click_on_add_button()
        page.try_cancel_and_close()

        fields = page.get_fields()

        error_message = page.try_submit(err=['username'])
        assert error_message == 'This field is required.'

        fields = page.get_fields()
        fields['username'].send_keys("darthvader")
        error_message = page.try_submit(err=['username'])
        assert error_message == ('User with username or email'
                                 ' darthvader does not exist')

        fields = page.get_fields()
        fields['username'].clear()
        fields['username'].send_keys("testuser")
        error_message = page.try_submit(err=['username'])
        assert error_message == 'User is already a member of the organization.'

        fields = page.get_fields()
        fields['username'].clear()
        fields['username'].send_keys("testanonymous")
        page.try_submit()
        member = self.panel_title()
        assert member == "MEMBER: Test Anonymous"

        member_page = OrganizationMemberPage(self, self.org.slug,
                                             'testanonymous')
        member_page.click_remove_member_and_confirm_buttons()

        page.click_on_add_button()
        fields = page.get_fields()
        fields['username'].clear()
        fields['username'].send_keys("testanonymous@example.com")
        page.try_submit()
        member = self.panel_title()
        assert member == "MEMBER: Test Anonymous"

    def test_adding_members_to_archived_organization(self):
        """If an organization is archive, you cannot add members."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationMemberListPage(self, self.archived_org.slug)
        page.go_to()
        self.get_screenshot()

        title = self.panel_title()
        assert title == "Members".upper()
        page.click_on_add_button(err=True)
