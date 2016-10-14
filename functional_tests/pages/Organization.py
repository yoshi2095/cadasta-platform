from .base import Page
from selenium.webdriver.common.by import By


class OrganizationPage(Page):
    BY_MODAL_FADE = (By.CSS_SELECTOR, "div.modal.fade.in")
    BY_MODAL_BACKDROP = (By.CLASS_NAME, 'modal-backdrop')
    BY_ORG_OVERVIEW = (
        By.XPATH, "//h2[normalize-space(.)='Organization Overview']"
    )

    def __init__(self, test, org_slug):
        self.path = '/organizations/{}/'.format(
            org_slug)
        super().__init__(test)

    def click_through(self, button, wait, screenshot=None):
        return self.test.click_through(button, wait, screenshot)

    def click_through_close(self, button, wait):
        return self.test.click_through_close(button, wait)

    def get_container(self, xpath):
        return self.test.container(xpath)

    def get_page_header(self, xpath):
        return self.test.page_header(xpath)

    def get_page_content(self, xpath):
        return self.test.page_content(xpath)

    def get_org_description_and_members(self):
        return self.get_page_content(
            "//div[contains(@class, 'detail')]").text

    def click_on_more_button(self):
        more = self.get_page_header(
                "//div[contains(@class, 'btn-more')]")
        self.click_through(
            more, (By.CSS_SELECTOR, "div.dropdown.pull-right.btn-more"))

    def click_on_edit_button(self, error=False):
        self.click_on_more_button()
        edit = self.get_page_header("//a[@class='edit']")
        if error:
            self.click_through(edit, self.test.BY_ALERT)
        else:
            self.test.click_through(edit, self.BY_MODAL_BACKDROP)

    def get_edit_organization_form(self, xpath):
        return self.test.form_field('edit-org', xpath)

    def get_name_input(self):
        return self.get_edit_organization_form("input[@name='name']")

    def get_description_input(self):
        return self.get_edit_organization_form("textarea[@name='description']")

    def get_urls_input(self):
        return self.get_edit_organization_form("input[@name='urls']")

    def get_submit_button(self):
        return self.get_edit_organization_form("button[@name='submit']")

    def get_fields(self):
        return {
            'name':        self.get_name_input(),
            'description': self.get_description_input(),
            'urls':        self.get_urls_input(),
            'submit':      self.get_submit_button(),
        }

    def fill_inputboxes(self):
        fields = self.get_fields()
        fields['name'].clear()
        fields['name'].send_keys("Evil Coorporation")
        fields['description'].clear()
        fields['description'].send_keys("Planning world domination.")
        fields['urls'].clear()
        fields['urls'].send_keys("notstaying.com")

    def check_inputboxes(self):
        fields = self.get_fields()
        assert fields["name"].get_attribute('value') == "Organization #0"
        assert fields["description"].text == "This is a test."
        assert fields["urls"].text == ""

    def try_cancel_and_close(self):
        self.test.try_cancel_and_close(
            self.click_on_edit_button,
            self.fill_inputboxes,
            self.check_inputboxes
        )

    def get_archive_button(self):
        return self.get_page_header("//a[@class='archive']")

    def click_on_archive_and_confirm(self, archive):
        archive_button = self.get_archive_button()
        self.click_through(archive_button, self.BY_MODAL_FADE)

        final = self.test.link("{archive}-final".format(archive=archive))
        self.click_through_close(final, self.BY_MODAL_FADE)
        self.click_on_more_button()
        return self.get_archive_button().text

    def click_archive_button(self):
        archive = self.get_archive_button()
        self.click_through(archive, self.BY_MODAL_FADE)

    def check_archived(self):
        self.click_on_more_button()
        archive = self.get_archive_button()
        assert "Archive" in archive.text

    def try_cancel_and_close_archive(self):
        self.click_on_more_button()
        self.test.try_cancel_and_close_confirm_modal(
            self.click_archive_button,
            self.check_archived
        )

    def click_on_close_alert_button(self):
        close = self.browser.find_element_by_xpath(
            "//div[contains(@class, 'alert')]"
            "//button[contains(@class, 'close')]")
        self.click_through_close(close, self.test.BY_ALERT)

    def click_on_view_all_members_button(self, error=False):
        view_all = self.get_page_content(
            "//div[contains(@class, 'detail')]//a"
            "[contains(./text(), 'View all')]")

        if error:
            self.click_through(view_all, (By.CLASS_NAME, 'panel-default'))
        else:
            self.test.click_through_close(view_all, (By.CLASS_NAME, 'detail'))
            view_all = self.get_page_content("//h2").text
            return view_all

    def get_table_headers(self, xpath):
        table_head = self.test.table('DataTables_Table_0')
        return table_head.find_element_by_xpath("//thead//tr//th" + xpath)

    def get_project_title_in_table(self, row='1'):
        return self.test.table_body('DataTables_Table_0', "//tr[{}]".format(
            row))

    def click_on_project_in_table(self):
        project = self.get_project_title_in_table()
        self.click_through(project, (By.CLASS_NAME, "leaflet-container"))
        project_title = self.test.page_title()
        return project_title.text

    def get_new_project_welcome_message(self):
        return self.get_page_content(
            "//div[contains(@class, 'panel-body')]").text

    def click_add_new_project_button(self, error=False):
        try:
            button = self.get_page_content(
                "//a[contains(@href, '/projects/new/')]")
        except:
            button = self.get_page_header(
                "//a[contains(@href, '/projects/new/')]")
        if error:
            self.click_through(button, self.test.BY_ALERT)
        else:
            self.click_through(button, (By.CLASS_NAME, 'new-project-page'))
            return self.test.page_title().text

    def get_empty_project_panel(self):
        panel = self.browser.find_element_by_xpath(
            "//div[contains(@class, 'panel-body')]")
        return panel.text

    def sort_table_by(self, order, col):
        order = "asc" if order == "ascending" else "desc"
        if col == "project":
            col = "[2]"
        elif col == "country":
            col = "[3]"
        else:
            col = "[4]"
        self.click_through(
            self.get_table_headers(col),
            (By.CLASS_NAME, 'sorting_{}'.format(order))
        )
        project_title = self.get_project_title_in_table()
        return project_title.text

    def get_archive_option(self, option):
        return self.browser.find_element_by_xpath(
            "//select[contains(@id, 'archive-filter')]" +
            "//option[contains(@value, '{}')]".format(option))

    def click_archive_filter(self, option):
        option = self.get_archive_option(option)
        self.test.click_through(option, (By.CLASS_NAME, 'sorting_asc'))

    def go_back_to_organization_list(self):
        back_button = self.test.link('index-link')
        self.click_through(back_button, (By.CLASS_NAME, 'add-org'))
        return self.test.page_title().text

    def try_submit(self, get_fields=None,
                   by=None, err=None, ok=None,):
        get_fields = self.get_fields
        if err:
            by = (By.CLASS_NAME, 'modal-backdrop')
        else:
            by = (By.CLASS_NAME, 'content-single')

        self.test.try_submit(get_fields, by, err, ok)
