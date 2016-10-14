from .base import Page
from selenium.webdriver.common.by import By


class OrganizationMemberPage(Page):
    def __init__(self, test, org_slug, member):
        self.path = '/organizations/{org}/members/{member}'.format(
            org=org_slug,
            member=member)
        super().__init__(test)

    def click_through(self, button, wait):
        return self.test.click_through(button, wait)

    def get_member_list(self, xpath=""):
        return self.test.table('DataTables_Table_0')

    def get_displayed_member_info(self):
        return self.get_form_field("div[contains(@class, 'member-info')]")

    def get_form_field(self, xpath):
        return self.test.form_field('org-member-edit', xpath)

    def get_member_role_select(self, xpath):
        return self.get_form_field(
            "select[contains(@id, 'id_org_role')]" + xpath
        )

    def get_member_role_option(self):
        return self.get_member_role_select("//option[contains(@value, 'M')]")

    def get_admin_role_option(self):
        return self.get_member_role_select("//option[contains(@value, 'A')]")

    def get_selected_role(self):
        return self.get_member_role_select(
            "//option[contains(@selected, 'selected')]")

    def get_project_title_in_table(self, row="[1]"):
        return self.test.table_body(
            "projects-permissions", "//tr{}//td//label".format(row)).text

    def get_project_permission(self, xpath):
        try:
            return self.test.table_body(
                "projects-permissions", '//select' + xpath)
        except:
            print("No project permissions available.")
            None

    def get_project_user(self):
        return self.get_project_permission(
                "//option[contains(@value, 'PU')]")

    def get_data_collector(self):
        return self.get_project_permission(
                "//option[contains(@value, 'DC')]")

    def get_project_manager(self):
        return self.get_project_permission(
                "//option[contains(@value, 'PM')]")

    def get_public_user(self):
        return self.get_project_permission(
                "//option[contains(@value, 'Pb')]")

    def get_selected_permission(self):
        return self.get_project_permission(
                "//option[contains(@selected, 'selected')]")

    def get_submit_button(self):
        return self.get_form_field("button[contains(@name, 'submit')]")

    def get_fields(self):
        return {
            "member": self.get_member_role_option(),
            "admin": self.get_admin_role_option(),
            "role_selected": self.get_selected_role(),
            'pu':       self.get_project_user(),
            'dc':       self.get_data_collector(),
            'pm':       self.get_project_manager(),
            'pb':       self.get_public_user(),
            'per_selected': self.get_selected_permission(),
            "submit": self.get_submit_button(),
        }

    def try_submit(self, err=None, ok=None):
        if err:
            by = (By.ID, 'projects-permissions_wrapper')
        else:
            by = (By.ID, 'DataTables_Table_0_wrapper')
        self.test.try_submit(self.get_fields, by, err, ok)

    def click_remove_button(self):
        self.click_through(
            self.test.button("remove"), (By.CSS_SELECTOR, "div.modal.fade.in")
        )

    def click_disabled_remove_button(self):
        self.test.click_through_close(
            self.test.button("remove"), (By.CSS_SELECTOR, "div.modal.fade.in")
        )

    def click_remove_member_and_confirm_buttons(self):
        self.click_remove_button()
        self.click_through(
            self.test.link("confirm"), (By.CLASS_NAME, 'page-title')
        )

    def try_cancel_and_close_remove_member(self):
        self.test.try_cancel_and_close_confirm_modal(
            self.click_remove_button
        )
