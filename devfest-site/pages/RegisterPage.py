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
from bs4 import BeautifulSoup, UnicodeDammit
import urllib
import json
import re

# show the event registration form, and analyse the submission
class RegisterPage(FrontendPage):
  # helper function: prepare form content for integrating into
  # page
  def strip_form(self,full_html):
    soup = BeautifulSoup(full_html)
    form = soup.find("form")
    html = u""
    if form:
      for div in form.find_all("div", class_=re.compile("error")):
        # is there a label with text "Email"?
        label = div.find("label")
        if label and label.text.startswith("Email"):
          # OK, this is a field called "Email". We will replace
          # it with a hidden field holding the current user
          user = users.get_current_user()
          input = div.find("input")
          input["type"] = "hidden"
          input["value"] = user.email()
          # throw away everything else
          div = input
        html = html + u"\n" + div.decode()
    return html

  # we render the Google Spreadsheet form with our CSS and allow
  # submission
  def show(self,event_id):
    self.template = 'register_user'
    event = Event.get(event_id)
    # first check: is the event using external registration?
    if event.register_url:
      return self.redirect(str(event.register_url))
    user = users.get_current_user()
    # check if user is already registered
    if user and event and (user not in event.participants):
      self.values['event'] = event
      self.values['html'] = self.strip_form(event.register_html)
    elif user and event:
      self.values['event'] = event
      self.template = 'register_success'
    else:
      return self.redirect(users.create_login_url("/events"))

  # here the post target.
  # we send the form to big G and see what they say to it
  def show_post(self,event_id):
    body = self.request.body
    event = Event.get(event_id)
    user = users.get_current_user()
    if user and event:
      self.values['event'] = event
      formkey = event.register_formkey
      url = u"https://docs.google.com/spreadsheet/formResponse?formkey=%s" % formkey
      result = urlfetch.fetch(url=url,
                  payload=body,
                  method=urlfetch.POST,
                  headers={'Content-Type': 'application/x-www-form-urlencoded'})
      if result.status_code == 200:
        soup = BeautifulSoup(result.content)
        if soup.find("form"):
          # this is probably bad news. in the result html there is a form,
          # that can only mean big g was not happy with our submission.
          self.values['html'] = self.strip_form(result.content.decode("utf-8"))
          self.template = 'register_user'
        else:
          # assumption: gooooooood news!!! we can add the user to the event
          # participants
          event.participants = event.participants + [user]
          event.put()
          self.template = 'register_success'
      else:
        self.template = 'register_error'
    else:
      return self.redirect(users.create_login_url("/events"))
