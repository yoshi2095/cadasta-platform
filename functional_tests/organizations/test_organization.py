from base import FunctionalTest
from fixtures import load_test_data
from fixtures.common_test_data_2 import get_test_data
from pages.Organization import OrganizationPage
from pages.Login import LoginPage

from organization.models import OrganizationRole
from accounts.tests.factories import UserFactory
from core.tests.factories import PolicyFactory


class OrganizationTest(FunctionalTest):
    def setUp(self):
        super().setUp()
        PolicyFactory.load_policies()
        test_objs = load_test_data(get_test_data())
        self.org = test_objs['organizations'][0]
        self.new_org = test_objs['organizations'][1]

    def test_organization_view(self):
        """A registered user can view an organization's dashboard.
           Org description and users are displayed."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationPage(self, self.org.slug)
        page.go_to()

        info = page.get_org_description_and_members()
        assert "This is a test." in info
        assert "Test User" in info
        assert "testuser" in info
        self.logout()

        LoginPage(self).login('testuser', 'password')
        page = OrganizationPage(self, self.org.slug)
        page.go_to()

        info = page.get_org_description_and_members()
        assert "This is a test." in info
        assert "Test User" in info
        assert "testuser" in info

    def test_edit_organization(self):
        """A registered admin user can edit an organization's information."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationPage(self, self.org.slug)
        page.go_to()

        page.click_on_edit_button()
        page.try_cancel_and_close()

        fields = page.get_fields()
        assert fields["name"].get_attribute("value") == "Organization #0"
        assert fields["description"].text == "This is a test."
        assert fields["urls"].text == ""

        fields["name"].clear()
        page.try_submit(err=['name'], ok=['description', 'urls'])

        fields = page.get_fields()
        fields["name"].send_keys("Stark Enterprise")
        fields["description"].clear()
        page.try_submit()

        page.click_on_edit_button()
        fields = page.get_fields()
        fields["description"].send_keys("A technology company.")
        page.try_submit()

        name = self.page_title().text
        info = page.get_org_description_and_members()
        assert "Stark Enterprise".upper() in name
        assert "A technology company." in info

    def test_archiving_organization(self):
        """A registered admin user can archive/unarchive an organization."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationPage(self, self.org.slug)
        page.go_to()

        page.try_cancel_and_close_archive()

        archive = page.click_on_archive_and_confirm(archive="archive")
        assert archive == "Unarchive organization"

        archive = page.click_on_archive_and_confirm(archive="unarchive")
        assert archive == "Archive organization"

        archive = page.click_on_archive_and_confirm(archive="archive")
        page.click_on_more_button()

        page.click_on_edit_button(error=True)
        page.click_on_close_alert_button()
        page.click_add_new_project_button(error=True)

    def test_getting_to_the_user_list(self):
        """A registered admin user can view an organization's member list,
        but a regular member can't."""

        LoginPage(self).login('testuser', 'password')
        page = OrganizationPage(self, self.org.slug)
        page.go_to()

        page.click_on_view_all_members_button(error=True)
        url = self.get_url_path()
        assert "members" not in url
        self.logout()

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationPage(self, self.org.slug)
        page.go_to()

        title = page.click_on_view_all_members_button()
        assert title == "Members".upper()

    def test_navigating_to_project_page(self):
        """A registered user can view an organization's project page."""

        LoginPage(self).login('testuser', 'password')
        page = OrganizationPage(self, self.org.slug)
        page.go_to()

        title = page.click_on_project_in_table()
        assert title == "Organization #0\nTest Project".upper()

    def test_new_organization_view(self):
        """An organization without projects has a different view for its
        creator.

        """
        LoginPage(self).login('testuser', 'password')
        page = OrganizationPage(self, self.new_org.slug)
        page.go_to()

        welcome = page.get_new_project_welcome_message()
        assert "You're ready to go" in welcome

        title = page.click_add_new_project_button()
        assert title == "ADD NEW PROJECT"

    def test_new_organization_view_with_unauthorized_user(self):
        """An organization without projects has a different view for
        non-org members. """

        page = OrganizationPage(self, self.new_org.slug)
        page.go_to()

        project_list = page.get_empty_project_panel()
        assert project_list == ('This organization does not '
                                'have any public projects.')

        LoginPage(self).login('testanonymous', 'password')
        page = OrganizationPage(self, self.new_org.slug)
        page.go_to()

        project_list = page.get_empty_project_panel()
        assert project_list == ('This organization does not '
                                'have any public projects.')

    def test_navigate_back_to_organization_list(self):
        """A user can click on the index-link
        and it takes them back to the organizations list."""

        LoginPage(self).login('testuser', 'password')
        page = OrganizationPage(self, self.org.slug)
        page.go_to()

        page_title = page.go_back_to_organization_list()
        assert page_title == "Organizations".upper()

    def test_archived_projects_appear_for_testadmin(self):
        """The option to filter active/archived projects within an organization
        is available to organization administrators."""

        LoginPage(self).login('testadmin', 'password')
        page = OrganizationPage(self, self.org.slug)
        page.go_to()

        first_project = page.get_project_title_in_table().text
        assert 'Test Project' in first_project

        self.get_screenshot()
        page.click_archive_filter("Archived")
        first_project = page.get_project_title_in_table().text
        assert 'Another Project' in first_project

        first_project = page.sort_table_by("descending", col="project")
        assert 'Another Project' in first_project

        page.sort_table_by("ascending", col="project")
        page.click_archive_filter("All")
        assert 'Another Project' in first_project

        first_project = page.sort_table_by("descending", col="project")
        assert 'Test Project' in first_project

        page.sort_table_by("ascending", col="project")
        page.click_archive_filter("Archived")
        page.click_archive_filter("Active")
        first_project = page.get_project_title_in_table().text
        assert 'Test Project' in first_project
