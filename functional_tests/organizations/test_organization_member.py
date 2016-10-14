from base import FunctionalTest
from fixtures import load_test_data
from fixtures.common_test_data_2 import get_test_data
from pages.Dashboard import DashboardPage
from pages.OrganizationMember import OrganizationMemberPage
from pages.Organization import OrganizationPage
from pages.OrganizationList import OrganizationListPage
from pages.OrganizationMemberList import OrganizationMemberListPage
from pages.Login import LoginPage

from accounts.tests.factories import UserFactory
from organization.models import OrganizationRole
from core.tests.factories import PolicyFactory


class OrganizationMemberTest(FunctionalTest):
    def setUp(self):
        super().setUp()
        PolicyFactory.load_policies()

        test_objs = load_test_data(get_test_data())
        self.org = test_objs['organizations'][0]
        self.testuser = test_objs['users'][1]
        self.adminuser = test_objs['users'][2]

    def test_member_information_displays(self):
        """The organization's individual member page
        displays with the correct user information."""

        LoginPage(self).login('testadmin', 'password')
        self.get_screenshot()
        page = OrganizationMemberPage(self, self.org.slug,
                                      self.testuser.username)
        page.go_to()
        self.get_screenshot()

        testuser_title = self.panel_title()
        assert "MEMBER: Test User" == testuser_title

        member_form = page.get_displayed_member_info()

        assert "Test User" in member_form.text
        assert "testuser" in member_form.text
        assert "testuser@example.com" in member_form.text
        assert "Last login:" in member_form.text

    def test_changing_a_members_organizational_role(self):
        """An admin member can change a member's role in the organization."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationMemberPage(self, self.org.slug,
                                      self.testuser.username)
        page.go_to()

        roles = page.get_fields()
        assert roles["member"].text == roles["role_selected"].text

        roles["admin"].click()
        page.try_submit()
        page.go_to()

        roles = page.get_fields()
        assert roles["admin"].text == roles["role_selected"].text

        roles["member"].click()
        page.try_submit()
        page.go_to()

        roles = page.get_fields()
        assert roles["member"].text == roles["role_selected"].text

    def test_changing_an_admins_organizational_role(self):
        """An admin member cannot change a their role in the organization."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationMemberPage(self, self.org.slug,
                                      self.adminuser.username)
        page.go_to()

        role_select = page.get_member_role_select('')
        assert role_select.get_attribute('disabled')
        roles = page.get_fields()
        assert roles["admin"].text == roles["role_selected"].text

    def test_removing_a_member_from_an_organization(self):
        """An admin member can remove a member from an organization."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationMemberPage(self, self.org.slug,
                                      self.testuser.username)
        page.go_to()

        page.try_cancel_and_close_remove_member()
        assert self.panel_title() == "MEMBER: Test User"

        page.click_remove_member_and_confirm_buttons()

        members = page.get_member_list().text
        assert "Test User" not in members

    def test_removing_an_admin_member_from_an_organization(self):
        """An admin member cannot remove themselves from an organization."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationMemberPage(self, self.org.slug,
                                      self.adminuser.username)
        page.go_to()

        assert self.panel_title() == "MEMBER: Test Admin"

        page.click_disabled_remove_button()
        assert self.panel_title() == "MEMBER: Test Admin"

    def test_changing_member_project_permissions(self):
        """An admin user can change a member's permissions
        on individual projects."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationMemberPage(self, self.org.slug,
                                      self.testuser.username)
        page.go_to()
        first_project = page.get_project_title_in_table()
        assert first_project != 'Another Project'
        assert first_project == 'Test Project'
        options = page.get_fields()
        assert options['per_selected'].text == options['pb'].text
        options['pm'].click()

        page.try_submit()
        page.go_to()

        options = page.get_fields()
        assert options['per_selected'].text == options['pm'].text

    def test_admin_creation_when_adding_organization(self):
        """A user that can create a new organization and
        is automatically made an admin."""

        LoginPage(self).login('testuser', 'password')
        OrganizationListPage(self).go_to()

        OrganizationListPage(self).click_add_button()
        fields = OrganizationListPage(self).get_fields()
        fields['name'].send_keys('New Organization')
        fields['description'].send_keys('This is a test organization')
        OrganizationListPage(self).try_submit()

        page = OrganizationMemberPage(self, 'new-organization',
                                      self.testuser.username)
        page.go_to()

        roles = page.get_fields()
        assert roles['role_selected'].text == "Administrator"

    def test_editing_member_in_archived_organization(self):
        """A user that can create a new organization and
        is automatically made an admin."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationPage(self, self.org.slug)
        page.go_to()
        page.get_archive_button()
        page.click_on_more_button()
        page.click_on_archive_and_confirm(archive="archive")

        page = OrganizationMemberPage(self, self.org.slug,
                                      self.testuser.username)
        page.go_to()
        DashboardPage(self).is_on_page()
        self.assert_has_message('alert', "have permission")
