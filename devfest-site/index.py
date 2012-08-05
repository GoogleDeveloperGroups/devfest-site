import webapp2
from lib.view import FrontendPage
from google.appengine.api import users
from google.appengine.ext import db
from pages.StartPage import *
from pages.LoginPage import *

app = webapp2.WSGIApplication([
                              ('^/login$', LoginPage),
                              ('^/$', StartPage),
                              ('^/location$', EventPage),
                              ],
                              debug=True)

