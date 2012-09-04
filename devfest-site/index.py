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
from pages.RegisterPage import *
from pages.JsonPages import *
from pages.SlotsPages import *

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
                              # show / change days/slots list for an event id
                              ('^/event/slots/edit/(.*)$', SlotsEditPage),
                              # upload days/slots list for an event id
                              ('^/event/slots/upload$', SlotsUploadPage),
                              # show / change sessions list for an event id
                              ('^/event/sessions/edit/(.*)$', SessionsEditPage),
                              # register for an event
                              ('^/event/register/(.*)$', RegisterPage),
                              # agenda of an event
                              ('^/event/agenda/(.*)$', EventAgendaPage),
                              # json export of events
                              ('^/json/events$', JsonEventListPage),
                              ('^/json/event/(.*)/speakers$', JsonSpeakerListPage),
                              ('^/json/event/(.*)/sponsors$', JsonSponsorListPage),
                              ('^/json/event/(.*)/tracks$', JsonTrackListPage),
                              ('^/json/event/(.*)/sessions$', JsonSessionListPage),
                              ('^/json/event/(.*)$', JsonEventPage),
                              ('^/events$', EventListPage),
                              ('^/events/schedule$', EventSchedulePage),
                              ('^/event/(.*)$', EventPage),
                              ('^/about$', AboutPage),
                              ('^/report$', ReportBugPage),
                              ('^/branding$', BrandingPage),
                              ('^/vhackandroid$', VHackAndroidPage),
                              ('^/faq$', FaqPage),
                              ('^/register$', RegisterFormPage),
                              ('^/contact$', ContactPage),
                              ('^/blob/(.*)$', BlobPage),
                              ('^/.*$', NotFoundPage),
                              ],
                              debug=False)
