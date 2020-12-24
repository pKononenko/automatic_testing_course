from subprocess import PIPE, Popen
from backend import task
import time

import requests
from requests import exceptions
import unittest
import json


class WebAppHTTPTest(unittest.TestCase):
    BACKEND_FILE_NAME = "backend.py"
    BACKEND_URL = 'http://localhost:8000'

    EXISTING_USER_DATA = {'user_name': 'Kostia', 'email': 'kostia1@gmail.com', 'password': '123456'}
    UNKNOWN_USER_DATA = {'user_name': 'Alice', 'email': 'alice_2002@gmail.com', 'password': 'aaa'}
    TEST_COMMENT = {"user_name": "Kostia", "task_data": [1, 2, 0, 2], "result": 1.5}
    TEST_DATA_TASK = {"user_name": "Kostia", "task_data": [1, 0, -1.4, 2.456, 5], "result": task([1, 0, -1.4, 2.456, 5])}

    def setUp(self):
        self.backend_process = Popen(['python', self.BACKEND_FILE_NAME])
    
    def tearDown(self):
        self.backend_process.kill()

    ## Utilities
    def custom_request(self, url_, data = None, method = "POST", get_cookie = False, send_cookie = None, timeout = 1, reconection_tries = 10):
        is_err = True
        return_arguments = {}
        headers = {
            'Accept':'text/html,application/javascript,text/javascript',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        }
        url = self.BACKEND_URL + url_
        
        while is_err:
            try:
                if method == "POST":
                    response = requests.post(url, data = data, headers = headers, timeout = timeout, cookies = send_cookie)
                else:
                    response = requests.get(url, data = data, headers = headers, timeout = timeout, cookies = send_cookie)
                is_err = False
            
            except exceptions.ConnectionError as e:
                is_err = True

            except exceptions.TooManyRedirects:
                print(e)
                return

            except exceptions.Timeout as e:
                is_err = True
            
            except exceptions.RequestException as e:
                print(e)
                return
            
            finally:
                reconection_tries -= 1
                if reconection_tries == 0:
                    return
                time.sleep(1)

        return_arguments['content'] = response.content
        return_arguments['text'] = response.text
        return_arguments['status_code'] = response.status_code
        if get_cookie:
            return_arguments['cookies'] = list(response.cookies)
        
        return return_arguments

    def check_cookies(self, user, cookies):
        list_name = list(user)
        list_cookie_name = [cookie.name for cookie in cookies]
        
        if len(cookies) != 3 and sorted(list_name) != sorted(list_cookie_name):
            return False
        
        for cookie in cookies:
            if cookie.name == user["user_name"] and user["user_name"] in cookie.value:
                return True
        return False

    ## Tests
    def test_1_correct_login(self):
        response = self.custom_request('/api/login', data = self.EXISTING_USER_DATA, get_cookie=True)
        self.check_cookies(self.EXISTING_USER_DATA, response['cookies'])

    def test_2_incorrect_login(self):
        response = self.custom_request('/api/login', data = self.UNKNOWN_USER_DATA, get_cookie=True)
        self.check_cookies(self.UNKNOWN_USER_DATA, response['cookies'])

    def test_3_register_new_user(self):
        response = self.custom_request('/api/register', data = self.UNKNOWN_USER_DATA, get_cookie=True)
        self.check_cookies(self.UNKNOWN_USER_DATA, response['cookies'])
    
    def test_4_register_new_user(self):
        response = self.custom_request('/api/register', data = self.EXISTING_USER_DATA, get_cookie=True)
        self.check_cookies(self.EXISTING_USER_DATA, response['cookies'])

    def test_5_get_data(self):
        response = self.custom_request('/api/task', method = "GET")
        json_returned = json.loads(response['content'])[0]
        self.assertDictEqual(json_returned, self.TEST_COMMENT)

    def test_6_user_correct_get_solution(self):
        data = json.dumps([1, 0, -1.4, 2.456, 5])
        response = self.custom_request('/api/task', data = data, send_cookie = self.EXISTING_USER_DATA)
        result_dict = json.loads(response['content'])
        self.assertDictEqual(result_dict, self.TEST_DATA_TASK)

    def test_7_user_unknown_get_solution(self):
        data = json.dumps([1, 0, -1.4, 2.456, 5])
        response = self.custom_request('/api/task', data = data, send_cookie = self.UNKNOWN_USER_DATA)
        result_dict = json.loads(response['content'])
        self.assertDictEqual(result_dict, {'status': 'no logged'})


if __name__ == "__main__":
    unittest.main(warnings='ignore')
