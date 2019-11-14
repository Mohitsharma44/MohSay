#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import json
import pathlib
import tornado
import tornado.web
import tornado.ioloop
import tornado.httpserver
from redis.sentinel import Sentinel
from tornado.log import app_log as log
from tornado.options import define, options, parse_command_line

# redis_master_password = os.getenv('REDIS_MASTER_PASSWORD')
# if not redis_master_password:
#     redis_master_password = Path('/run/secrets/redis-master-password').read_text().strip()    
base_dir = os.path.dirname(__file__)
static_dir = os.path.join(base_dir, "static")
invitations_dir = os.path.join(static_dir, "images/invitations/test/high/")

define("port", default=8080, help="run on the given port", type=int)

def get_from_redis(rsvp):
    """
    Get the data corresponding to the rsvp code
    """
    # We want to connect to a different replica everytime
    # we need to run a query
    # try:
    #     sentinel = Sentinel([('redis-sentinel', 16379)],
    #                         socket_timeout=0.1,
    #                         password=redis_master_password)
    #     replica = sentinel.slave_for('master-node')
    #     response = replica.hgetall(rsvp)
    # except Exception as ex:
    #     print("Error fetching response for rsvp code: {}\n {}".format(rsvp, ex))
    #     response = False
    # finally:
    #     return response
    user_data = {'Name': 'Foo Bar', 'Cat': 1, 'Photo': 0,
                 'RSVP': 1, 'Contact No': '1234567890'}
    return user_data

class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        return (self.get_secure_cookie("rsvp_code"),
                self.get_secure_cookie("username"))

class LoginHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        print('Got get request for login')
        self.render('login.html')

    @tornado.gen.coroutine
    def post(self):
        print('Got post request for login')
        # grab the username based on rsvp code
        #user_data = get_from_redis(self.get_argument("rsvp-code"))
        user_data = {'Name': 'Foo Bar', 'Cat': 1, 'Photo': 0,
                     'RSVP': 1, 'Contact No': '1234567890'}
        self.set_secure_cookie("rsvp_code", self.get_argument("rsvp_code"))
        self.set_secure_cookie('username', user_data['Name'])
        print("Stored username: {} and rsvp: {}".format(user_data['Name'],
                                                        self.get_argument("rsvp_code")))
        # self.set_secure_cookie('cat', user_data['Cat'])
        # self.set_secure_cookie('photo', user_data['Photo'])
        # self.set_secure_cookie('rsvp', user_data['RSVP'])
        # self.set_secure_cookie('contact_no', user_data['Contact No'])
        self.redirect("/dashboard/")

class DashHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        self.render('index.html')

    @tornado.gen.coroutine
    def post(self):
        log.warn("I shouldn't be getting post requests")

class PhotoHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        log.info('got request for photohandler')
        self.render('photoviewer.html')

    @tornado.gen.coroutine
    def post(self):
        log.warn("I shouldn't be getting post requests for photohandler")


class InvitationHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        log.info("got request for InvitationHandler from {}".format(self.get_current_user()))
        # Lets obtain user information
        user_data = get_from_redis(self.get_current_user()[0])
        self.render('invitation.html',
                    guest_name= user_data["Name"],
                    invitation_link=os.path.join('/', invitations_dir, "cat{}.pdf".format(user_data["Cat"])),
                    image_links=[
                        os.path.join('/', invitations_dir, 'first.png'),
                        os.path.join('/', invitations_dir, 'second.png'),
                        os.path.join('/', invitations_dir, "cat{}.png".format(user_data["Cat"]))
                        ])

    @tornado.gen.coroutine
    def post(self):
        log.warn("I shouldn't be receiving post requests for invitationhandler")

class UserTableHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        log.info('get request for UserTableHandler')
        self.render('tables.html')

    @tornado.gen.coroutine
    def post(self):
        log.warn("I shouldn't be gettng post requests")

class DBHandler(BaseHandler):

    def set_default_headers(self):
        log.info("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')

    def options(self):
        # no body
        #self.set_status(204)
        self.finish()

    @tornado.gen.coroutine
    def get(self):
        with open("test/test_invites.txt", 'r') as fh:
            #data = fh.readlines()
            data = json.load(fh)
        self.write('{{"data": {}}}'.format(json.dumps(data)))
        self.finish()

    @tornado.gen.coroutine
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        log.info("Data received in POST: {}".format(data))
        return "{'response': 'OK'}"

class Application(tornado.web.Application):
    def __init__(self):
        settings = {
            "cookie_secret": "123", # Change this in prod
            "login_url": "/auth/login",
            'template_path': os.path.join(base_dir, "templates"),
            'static_path': os.path.join(base_dir, "static"),
            'debug':True,
            "xsrf_cookies": False,
        }
        tornado.web.Application.__init__(self, [
            tornado.web.url(r'/login/.*', LoginHandler, name='loginhandler'),
            tornado.web.url(r'/invitation/.*', InvitationHandler, name='invitationhandler'),
            # Testing photoviewer
            tornado.web.url(r'/photoviewer/.*', PhotoHandler, name='photohandler'),
            tornado.web.url(r'/dashboard/.*', DashHandler, name="dashhandler"),
            tornado.web.url(r'/tables/.*', UserTableHandler, name="usertablehandler"),
            tornado.web.url(r'/update_record/.*', DBHandler, name="dbhandler"),
        ], **settings)

if __name__ == "__main__":
    parse_command_line()
    Application().listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
