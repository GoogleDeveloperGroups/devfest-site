import webapp2
from lib.view import FrontendPage
from google.appengine.api import users
from google.appengine.ext import db
from pages.StartPage import *
from pages.LoginPage import *
from pages.EventPages import *
from pages.OtherPages import *

app = webapp2.WSGIApplication([
                              ('^/logout$', LogoutPage),
                              ('^/login$', LoginPage),
                              ('^/$', StartPage),
                              ('^/event/create$', EventCreatePage),
                              ('^/event/upload$', EventUploadPage),
                              ('^/events$', EventListPage),
                              ('^/events/schedule$', EventSchedulePage),
                              ('^/event/(.*)$', EventPage),
                              ],
                              debug=True)
