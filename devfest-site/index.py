import webapp2
from lib.view import FrontendPage
from google.appengine.api import users
from google.appengine.ext import db
from pages.StartPage import *
from pages.LoginPage import *
from pages.EventPages import *
from pages.OtherPages import *
from pages.ContactPage import *
from pages.SponsorsPages import *
from pages.SpeakersPages import *
from pages.SessionsPages import *

app = webapp2.WSGIApplication([
                              ('^/logout$', LogoutPage),
                              ('^/login$', LoginPage),
                              ('^/$', StartPage),
                              ('^/event/create$', EventCreatePage),
                              ('^/event/edit$', EventSelectPage),
                              ('^/event/edit/(.*)$', EventEditPage),
                              ('^/event/delete/(.*)$', EventDeletePage),
                              ('^/event/upload$', EventUploadPage),
                              # upload sponsors list for an event
                              ('^/event/sponsors/upload$', SponsorsUploadPage),
                              # show / change sponsors list for an event id
                              ('^/event/sponsors/edit/(.*)$', SponsorsEditPage),
                              # upload speakers list for an event
                              ('^/event/speakers/upload$', SpeakersUploadPage),
                              # show / change speakers list for an event id
                              ('^/event/speakers/edit/(.*)$', SpeakersEditPage),
                              # upload sessions list for an event
                              ('^/event/sessions/upload$', SessionsUploadPage),
                              # show / change sessions list for an event id
                              ('^/event/sessions/edit/(.*)$', SessionsEditPage),
                              ('^/events$', EventListPage),
                              ('^/events/schedule$', EventSchedulePage),
                              ('^/event/(.*)$', EventPage),
                              ('^/about$', AboutPage),
                              ('^/report$', ReportBugPage),
                              ('^/branding$', BrandingPage),
                              ('^/faq$', FaqPage),
                              ('^/register$', RegisterFormPage),
                              ('^/contact$', ContactPage),
                              ('^/blob/(.*)$', BlobPage),
                              ('^/.*$', NotFoundPage),
                              ],
                              debug=False)
