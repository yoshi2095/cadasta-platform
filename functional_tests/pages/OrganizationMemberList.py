from .base import Page
from selenium.webdriver.common.by import By


class OrganizationMemberListPage(Page):
    def __init__(self, test, org_slug,):
        self.path = '/organizations/{org}/members/'.format(
            org=org_slug,)
        super().__init__(test)

    def click_through(self, button, wait):
        return self.test.click_through(button, wait)

    def get_table_row(self, xpath=""):
        return self.test.table_body('DataTables_Table_0', "//tr" + xpath)

    def click_on_add_button(self, err=False):
        add_button = self.test.page_content("//a[contains(@href, '/add/')]")
        if err:
            self.click_through(add_button, (By.CLASS_NAME, 'alert-warning'))
        else:
            self.click_through(add_button, (By.CLASS_NAME, 'modal-backdrop'))

    def get_modal(self, xpath):
        return self.browser.find_element_by_xpath(
            "//div[contains(@class, 'modal-content')]" + xpath
        )

    def get_username_input(self):
        return self.get_modal(
            "//input[@type='text']"
        )

    def get_submit_button(self):
        return self.get_modal(
                            "//button[@type='submit']")

    def get_fields(self):
        return {
            'username': self.get_username_input(),
            'submit': self.get_submit_button(),
        }

    def try_submit(self, err=None, ok=None):
        if err:
            by = (By.CLASS_NAME, 'errorlist')
        else:
            by = (By.CLASS_NAME, 'content-single')

        return self.test.try_submit(self.get_fields, by, err, ok)

    def fill_form(self):
        fields = self.get_fields()
        fields['username'].send_keys("This should go away.")

    def test_empty_form(self):
        fields = self.get_fields()
        assert fields['username'].text == ""

    def try_cancel_and_close(self):
        self.test.try_cancel_and_close(
            self.click_on_add_button,
            self.fill_form,
            self.test_empty_form)
