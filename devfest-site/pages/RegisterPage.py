from lib.view import FrontendPage
from lib.view import UploadPage
from lib.view import Page
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from lib.model import Event
from lib.forms import EventForm
from lib.cobjects import CEventList, CEvent, CEventScheduleList
from datetime import datetime
import urllib
import json
import re

# show the event registration form, and analyse the submission
class RegisterPage(FrontendPage):
  # we either show the external register page, or
  # we check if the user is logged in, and if yes, if the
  # capacity is already exceeded.
  # if this is not the case we let her in!
  def show(self,event_id):
    self.template = 'register_success'
    event = CEvent(event_id).get()
    if not event:
      return self.redirect("/events")
    self.values['event'] = event
    # is the event using external registration?
    if event.register_url:
      return self.redirect(str(event.register_url))
    user = users.get_current_user()
    # check if user is already registered
    if not user:
      return self.redirect(users.create_login_url("/events"))
    # is user not yet registered?
    if user not in event.participants:
      if len(event.particpiants) >= event.register_max:
        self.template = 'register_full'
      else:
        # add user to participants
        event.participants = event.particpants + [user]
        # invalidate event
        CEvent.remove_from_cache(event.key())
