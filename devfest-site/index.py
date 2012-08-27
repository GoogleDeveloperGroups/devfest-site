import webapp2
from lib.view import FrontendPage
from google.appengine.api import users
from google.appengine.ext import db
from pages.StartPage import *
from pages.LoginPage import *
from pages.EventPages import *
from pages.OtherPages import *
from pages.ContactPage import *
from pages.SponsorPages import *
from pages.SpeakersPages import *

app = webapp2.WSGIApplication([
                              ('^/logout$', LogoutPage),
                              ('^/login$', LoginPage),
                              ('^/$', StartPage),
                              ('^/event/create$', EventCreatePage),
                              ('^/event/edit$', EventSelectPage),
                              ('^/event/edit/(.*)$', EventEditPage),
                              ('^/event/delete/(.*)$', EventDeletePage),
                              ('^/event/upload$', EventUploadPage),
                              ('^/event/sponsor/create$', SponsorCreatePage),
                              ('^/event/sponsor/edit$', SponsorEditPage),
                              ('^/event/sponsor/upload$', SponsorUploadPage),
                              # upload speakers list for an event
                              ('^/event/speakers/upload$', SpeakersUploadPage),
                              # show / change speakers list for an event id
                              ('^/event/speakers/edit/(.*)$', SpeakersEditPage),
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
