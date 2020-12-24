from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from warnings import simplefilter

from subprocess import Popen, PIPE, STDOUT
from backend import task
import unittest
import time


def load_driver():
    DRIVER_OPTIONS = ChromeOptions()
    DRIVER_OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = Chrome(options = DRIVER_OPTIONS)
    return driver

class WebAppTest(unittest.TestCase):
    BACKEND_FILE_NAME = "backend.py"
    BACKEND_URL = 'http://localhost:8000'

    ## Setup
    @classmethod
    def setUpClass(cls):
        simplefilter('ignore', ResourceWarning)

    def setUp(self):
        self.driver = load_driver()
        self.backend_process = Popen(['python', self.BACKEND_FILE_NAME], 
            stdin = None, stdout = PIPE, stderr = STDOUT)

    def tearDown(self):
        self.driver.quit()
        self.backend_process.kill()

    ## Utilities
    def login(self, user, dr):
        login_rad_button = dr.find_element_by_id('login-radio-label')
        login_rad_button.click()
        
        login_button = dr.find_element_by_id('login-button')
        for (destination_name, data) in user:
            log_in_form_element = dr.find_elements_by_name(destination_name)[0]
            log_in_form_element.clear()
            log_in_form_element.send_keys(data)
        login_button.click()
        time.sleep(0.5)

    def logout(self, dr):
        logout_button = dr.find_element_by_id('logout-button')
        logout_button.click()
        time.sleep(0.5)

    def register(self, user, dr):
        reg_rad_button = dr.find_element_by_id('reg-radio-label')
        reg_rad_button.click()
        
        register_button = dr.find_element_by_id('register-button')
        for (destination_name, data) in user:
            register_form_element = dr.find_elements_by_name(destination_name)[-1]
            register_form_element.clear()
            register_form_element.send_keys(data)
        register_button.click()
        time.sleep(0.5)

    def get_task_area_elements(self, dr, status = "login"):
        block_style = "block" if status else "none"
        
        task_area = dr.find_elements_by_xpath(f'//div[@id="task"][@style="display: {block_style};"]')
        result_button = dr.find_elements_by_xpath(f'//div[@id="task"][@style="display: {block_style};"]/form/div/input[@id="result-button"]')
        input_form = dr.find_elements_by_xpath(f'//div[@id="task"][@style="display: {block_style};"]/form/ul[@id="task-area-input-form"]/li/input')
        expandable_list_add = dr.find_elements_by_xpath(f'//div[@id="task"][@style="display: {block_style};"]/form/div[@id="expandable-list"]/input[@id="add-l"]')
        expandable_list_remove = dr.find_elements_by_xpath(f'//div[@id="task"][@style="display: {block_style};"]/form/div[@id="expandable-list"]/input[@id="remove-l"]')

        if status == "login":
            messages = ["Logged in user can't see tasks", "Logged in user can't see submit button", 
                    "User can't see input form (list)", "User can't see add list element button",
                    "User can't see remove list element button"]
        
        else:
            messages = ["Anonymous user see tasks", "Anonymous user see submit button", 
                    "Anonymous user see input form (list)", "Anonymous user see add list element button",
                    "Anonymous user see remove list element button"]

        form_elements = [task_area, result_button, input_form, expandable_list_add, expandable_list_add]
        return form_elements, messages

    def add_remove_elements_to_list(self, dr, el_count):
        if el_count == 0:
            return

        btn_id = "add-l" if el_count > 0 else "remove-l"
        button_l = dr.find_element_by_id(btn_id)

        for i in range(abs(el_count)):
            button_l.click()

    def clear_inputs(self, dr):
        li_inputs = dr.find_elements_by_xpath('//ul[@id="task-area-input-form"]/li/input')

        for inp in li_inputs:
            inp.clear()

    def post_solution(self, dr, data):
        li_inputs = dr.find_elements_by_xpath('//ul[@id="task-area-input-form"]/li/input')
        submit_button = dr.find_element_by_id('result-button')

        for inp, elem in zip(li_inputs, data):
            inp.clear()
            inp.send_keys(elem)
        submit_button.click()
        time.sleep(0.5)
    
    def get_last_comment(self, dr):
        last_comment = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')[-1]
        last_comment_text = last_comment.text
        return last_comment_text, last_comment

    ## Tests
    def test_01_login_logout_existing_user(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)
        
            existing_user_data = [
                ('email', 'kostia1@gmail.com'),
                ('password', '123456')
            ]
            self.login(existing_user_data, dr)

            # Check logout button on page
            logout_button = dr.find_elements_by_id('logout-button')
            self.assertTrue(logout_button, "Problems with log in")

            # Check tasks
            task_area_elements, messages = self.get_task_area_elements(dr)
            for element, message in zip(task_area_elements, messages):
                self.assertTrue(element, message)

            # Check logout button work
            self.logout(dr)
            login_button = dr.find_elements_by_id('login-button')
            self.assertTrue(login_button, "Problems with logout")
            time.sleep(1.5)
    
    def test_02_login_unknown_user(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)

            unknown_user_data = [
                ('email', 'stia2@gmail.com'),
                ('password', '3456')
            ]
            self.login(unknown_user_data, dr)
            
            # Check logout and login button on page
            logout_button = dr.find_elements_by_id('logout-button')
            login_button = dr.find_elements_by_id('login-button')

            # Check tasks
            task_area_elements, messages = self.get_task_area_elements(dr, status = "")
            for element, message in zip(task_area_elements, messages):
                self.assertTrue(element, message)

            self.assertFalse(logout_button, "Unknown user logged in")
            self.assertTrue(login_button, "Some problems occured")
            time.sleep(1.5)
    
    def test_03_register_and_login_new_user(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)

            new_user_data = [
                ('user_name', 'Pasha'),
                ('email', 'pashakononenko@gmail.com'),
                ('password', 'ppppp')
            ]
            self.register(new_user_data, dr)

            # Check logout button on page
            logout_button = dr.find_elements_by_id('logout-button')
            self.assertTrue(logout_button, "User not registered")

            # Check tasks
            task_area_elements, messages = self.get_task_area_elements(dr)
            for element, message in zip(task_area_elements, messages):
                self.assertTrue(element, message)

            logout_button[0].click()
            time.sleep(0.5)
            login_button = dr.find_elements_by_id('login-button')
            self.assertTrue(login_button, "Problems with logout")

            # Try to login with this user
            self.login(new_user_data[1:], dr)
            
            # Check logout button on page
            logout_button = dr.find_elements_by_id('logout-button')
            self.assertTrue(logout_button, "Problems with log in user")
            time.sleep(1.5)
    
    def test_04_register_existing(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)

            existing_user_data = [
                ('user_name', 'Kostia'),
                ('email', 'kostia1@gmail.com'),
                ('password', '123456')
            ]
            self.register(existing_user_data, dr)

            # Check logout button on page
            logout_button = dr.find_elements_by_id('logout-button')
            self.assertFalse(logout_button, "Existing user registered twice")
            
            # Check tasks
            task_area_elements, messages = self.get_task_area_elements(dr, status = "")
            for element, message in zip(task_area_elements, messages):
                self.assertTrue(element, message)
            time.sleep(1.5)

    def test_05_anonymous_view(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)
            
            login_button = dr.find_element_by_id('login-button')
            self.assertTrue(login_button, "Problems with login")

            # Check tasks
            task_area_elements, messages = self.get_task_area_elements(dr, status = "")
            for element, message in zip(task_area_elements, messages):
                self.assertTrue(element, message)
            time.sleep(1.5)

    def test_06_start_comment(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)

            # Check comment in anonymous
            comment = ["Введені дані: 1,2,0,2. Результат: 1.5. Kostia"]
            comment_area = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            comment_area_text = [elem.text for elem in comment_area]
            self.assertTrue(len(comment_area), "No solution comments")
            self.assertListEqual(comment_area_text, comment, "Wrong solution comment")

            existing_user_data = [
                ('email', 'kostia1@gmail.com'),
                ('password', '123456')
            ]
            self.login(existing_user_data, dr)
            
            comment_area = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            comment_area_text = [elem.text for elem in comment_area]
            self.assertTrue(len(comment_area), "No solution comments")
            self.assertListEqual(comment_area_text, comment, "Wrong solution comment")
            time.sleep(1.5)
    
    def test_07_add_remove_buttons(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)

            existing_user_data = [
                ('email', 'kostia1@gmail.com'),
                ('password', '123456')
            ]
            self.login(existing_user_data, dr)

            self.add_remove_elements_to_list(dr, 3)
            li_inputs = dr.find_elements_by_xpath('//ul[@id="task-area-input-form"]/li/input')
            self.assertEqual(len(li_inputs), 4, "Incorrect numbrer of inputs")

            self.add_remove_elements_to_list(dr, -1)
            li_inputs = dr.find_elements_by_xpath('//ul[@id="task-area-input-form"]/li/input')
            self.assertEqual(len(li_inputs), 3, "Incorrect numbrer of inputs")

            self.add_remove_elements_to_list(dr, -100)
            li_inputs = dr.find_elements_by_xpath('//ul[@id="task-area-input-form"]/li/input')
            self.assertEqual(len(li_inputs), 1, "Incorrect numbrer of inputs")
            time.sleep(1.5)
    
    def test_08_add_solution(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)

            last_comment_default_1 = [f"Введені дані: 1,2,2. Результат: {task([1,2,2])}. Max"]
            last_comment_default_2 = [f"Введені дані: 1,0,-2,3,3. Результат: {task([1,0,-2,3,3])}. Max"]
            existing_user_data = [
                ('email', 'max@gmail.com'),
                ('password', '345678')
            ]
            self.login(existing_user_data, dr)

            comment_area = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            self.add_remove_elements_to_list(dr, 2)
            self.clear_inputs(dr)
            self.post_solution(dr, [1, 2, 2])
            last_comment, _ = self.get_last_comment(dr)
            comment_area_new = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            self.assertEqual(len(comment_area_new), len(comment_area) + 1, "Solution comment added")
            self.assertListEqual([last_comment], last_comment_default_1, "Wrong solution comment added")
            
            comment_area = comment_area_new
            self.add_remove_elements_to_list(dr, 2)
            self.clear_inputs(dr)
            self.post_solution(dr, [1, 0, -2, 3, 3])
            last_comment, _ = self.get_last_comment(dr)
            comment_area_new = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            self.assertEqual(len(comment_area_new), len(comment_area) + 1, "Solution comment didn't added")
            self.assertListEqual([last_comment], last_comment_default_2, "Wrong solution comment added")
            time.sleep(1.5)

    def test_09_add_solution_spaces(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)

            last_comment_default = [f"Введені дані: 3,4,0. Результат: {task([3,4,0])}. Max"]
            existing_user_data = [
                ('email', 'max@gmail.com'),
                ('password', '345678')
            ]
            self.login(existing_user_data, dr)

            comment_area = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            last_comment, last_comment_selenuim_obj = self.get_last_comment(dr)
            self.add_remove_elements_to_list(dr, 2)
            self.clear_inputs(dr)
            self.post_solution(dr, [])
            last_comment_new, last_comment_selenuim_obj_new = self.get_last_comment(dr)
            comment_area_new = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            self.assertEqual(len(comment_area_new), len(comment_area), "Solution comment added")
            self.assertEqual(last_comment, last_comment_new, "Wrong solution last comment")
            self.assertEqual(last_comment_selenuim_obj, last_comment_selenuim_obj_new, "Wrong solution comment objects")

            comment_area = comment_area_new
            self.add_remove_elements_to_list(dr, 2)
            self.clear_inputs(dr)
            self.post_solution(dr, ['', 3, 4, '', 0])
            last_comment, _ = self.get_last_comment(dr)
            comment_area_new = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            self.assertEqual(len(comment_area_new), len(comment_area) + 1, "Solution comment added")
            self.assertEqual([last_comment], last_comment_default, "Wrong solution last comment")
            time.sleep(1.5)

    def test_10_bad_data_solution(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)

            existing_user_data = [
                ('email', 'max@gmail.com'),
                ('password', '345678')
            ]
            self.login(existing_user_data, dr)

            comment_area = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            last_comment, last_comment_selenuim_obj = self.get_last_comment(dr)
            self.add_remove_elements_to_list(dr, 2)
            self.clear_inputs(dr)
            self.post_solution(dr, ['a', 1, -3])
            error_message = dr.find_elements_by_xpath('//p[@id="error-message"][@style="display: none;"]')
            time.sleep(5.5)
            self.assertFalse(error_message, "Wrong data sent. Error message didn't printed")
            last_comment_new, last_comment_selenuim_obj_new = self.get_last_comment(dr)
            comment_area_new = dr.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            self.assertEqual(len(comment_area_new), len(comment_area), "Wrong solution comment added")
            self.assertEqual(last_comment, last_comment_new, "Wrong solution last comment")
            self.assertEqual(last_comment_selenuim_obj, last_comment_selenuim_obj_new, "Wrong solution comment objects")
            time.sleep(1.5)

    def test_11_several_user_comments(self):
        with self.driver as dr:
            dr.get(self.BACKEND_URL)
            user1 = [
                ('email', 'kostia1@gmail.com'),
                ('password', '123456')
            ]
            self.login(user1, dr)

            driver2 = load_driver()
            with driver2 as dr2:
                dr2.get(self.BACKEND_URL)
                user2 = [
                    ('email', 'max@gmail.com'),
                    ('password', '345678')
                ]
                self.login(user2, dr2)

                self.clear_inputs(dr)
                self.add_remove_elements_to_list(dr, 3)
                self.post_solution(dr, [1, 2, 3, 0])

                self.clear_inputs(dr2)
                self.add_remove_elements_to_list(dr2, 4)
                self.post_solution(dr2, [1, 2, -3, 0, 2])

                self.clear_inputs(dr2)
                self.add_remove_elements_to_list(dr2, -3)
                self.post_solution(dr2, [0, 2])

                user2_comments = dr2.find_elements_by_xpath('//ul[@id="comments-area"]/li')
                user2_comments_text = [elem.text for elem in user2_comments]
        
        driver3 = load_driver()
        with driver3 as dr3:
            dr3.get(self.BACKEND_URL)
            user_comments = dr3.find_elements_by_xpath('//ul[@id="comments-area"]/li')
            self.assertListEqual([elem.text for elem in user_comments], user2_comments_text, "Different comments")


if __name__ == "__main__":
    unittest.main()
