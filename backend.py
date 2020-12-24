from werkzeug.security import generate_password_hash, check_password_hash
from tornado.web import Application, HTTPError, RequestHandler, url
from tornado.escape import url_unescape, url_escape
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from mimetypes import guess_type
import requests
import json
import os

HTTP_PORT = 8000
BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)
FILES_ROOT = os.path.join(BASEDIR_PATH, 'Server')


class WebApp(Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.users_list = []
        self.users_list_email = []
        self.solutions = []
        
        default_solutions = [
            ('Kostia', [1, 2, 0, 2], 1.5)
        ]
        default_users = [
            ('Kostia', 'kostia1@gmail.com', '123456'),
            ('Pavlo', 'pasha2@gmail.com', '234567'),
            ('Max', 'max@gmail.com', '345678')
        ]

        for user in default_users:
            self.add_user_site(user)
        for solution in default_solutions:
            self.add_solution(*solution)

    def add_user_site(self, user):
        username, email, password = user
        u = SiteUser(username, email)
        u.set_password(password)
        u.set_user_id(len(self.users_list))
        self.users_list_email.append(email)
        self.users_list.append(u)
    
    def add_solution(self, user_name, data_list, answer):
        self.solutions.append((user_name, data_list, answer))

    def login_user(self, email, password):
        if email in self.users_list_email:
            user_idx = self.users_list_email.index(email)
            user = self.users_list[user_idx]
            
            if user.check_password(password):
                return user
        
        return None
    
    def register_user(self, username, email, password):
        if email == "" or email in self.users_list_email:
            return False

        user = (username, email, password)
        self.add_user_site(user)
        return True


class SiteUser:
    
    def __init__(self, username, email):
        self.user_id = None
        self.username = username
        self.email = email
        self.password_hash = None

    def set_user_id(self, user_id):
        self.user_id = user_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, input_password):
        return check_password_hash(self.password_hash, input_password)


class ApiUserLoginHandler(RequestHandler):    
    
    def post(self):
        email = url_unescape(self.get_argument("email"), plus = False)
        password = url_unescape(self.get_argument("password"), plus = False)
        user = app.login_user(email, password)

        if user is not None:
            #self.set_secure_cookie("email", url_escape(email))
            #self.set_secure_cookie("password", url_escape(password))
            self.set_cookie("email", url_escape(email))
            self.set_cookie("password", url_escape(password))
            self.set_cookie("user_name", url_escape(user.username))
        
        self.redirect("/")


class ApiUserRegisterHandler(RequestHandler):
    
    def post(self):
        user_name = url_unescape(self.get_argument("user_name"), plus = False)
        email = url_unescape(self.get_argument("email"), plus = False)
        password = url_unescape(self.get_argument("password"), plus = False)
        is_register = app.register_user(user_name, email, password)
        
        if is_register:
            ApiUserLoginHandler.post(self)
        else:
            self.redirect("/")


class ApiUserLogoutHandler(RequestHandler):
    
    def post(self):
        self.clear_cookie("user_name")
        self.clear_cookie("email")
        self.clear_cookie("password")
        self.redirect("/")


class ApiTaskHandler(RequestHandler):
    
    def get(self):
        solutions = app.solutions
        res_solutions = []
        for solution in solutions:
            res_solutions.append({'user_name': solution[0], 'task_data': solution[1], 'result': solution[2]})
        
        res = json.dumps(res_solutions)
        self.write(res)
        self.finish()

    def post(self):
        email = url_unescape(self.get_cookie("email"), plus = True)
        password = url_unescape(self.get_cookie("password"), plus = True)
        if not(app.login_user(email, password)):
            response = json.dumps({'status': 'no logged'})
            self.write(response)
            self.finish()
            return
        
        user_name = url_unescape(self.get_cookie("user_name"), plus = True)
        request_body = self.request.body.decode("utf-8")
        task_data_request = json.loads(request_body)
        
        result = task(task_data_request)
        app.add_solution(user_name, task_data_request, result)
        response = json.dumps({'user_name': user_name, 'task_data': task_data_request, 'result': result})
        self.write(response)
        self.finish()


class FileHandler(RequestHandler):
    
    def get_cookie_formatted(self, name):
        cookie = self.get_cookie(name)
        return f'"{url_unescape(cookie, plus = False)}"' if cookie is not None else 'null'

    def get(self, path):
        if not path:
            path = 'index.html'
        file_location = os.path.join(FILES_ROOT, path)
        if not os.path.isfile(file_location):
            raise HTTPError(status_code=404)
        content_type, _ = guess_type(file_location)
        self.set_header('Content-Type', content_type)
        
        if ".html" in file_location:
            with open(file_location, 'r', encoding="utf-8") as source_file:
                self.write(source_file.read())
        else:
            with open(file_location, 'rb') as source_file:
                self.write(source_file.read())


def task(data_list):
    positive_data_list = list(filter(lambda elem: elem > 0, data_list))
    n = len(positive_data_list)
    avg_harmonic = n / sum([1 / x for x in positive_data_list]) if n else 0
    return avg_harmonic


if __name__ == "__main__":
    app = WebApp([
        url(r"/api/login", ApiUserLoginHandler),
        url(r"/api/logout", ApiUserLogoutHandler),
        url(r"/api/register", ApiUserRegisterHandler),
        url(r"/api/task", ApiTaskHandler),
        url(r"/(.*)", FileHandler)
    ], cookie_secret = "sha#dnvfi80-4354df")

    http_server = HTTPServer(app)
    http_server.listen(HTTP_PORT, address = 'localhost')
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        IOLoop.instance().stop()
