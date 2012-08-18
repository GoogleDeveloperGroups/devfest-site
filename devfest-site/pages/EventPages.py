from lib.view import FrontendPage
from lib.view import UploadPage
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

class EventSchedulePage(FrontendPage):
  def show(self):
    self.template = 'event_schedule'
    self.values['current_navigation'] = 'events'
    self.values['events'] = CEventScheduleList().get()

class EventCreatePage(FrontendPage):
  def show(self):
    self.template = 'event_create'
    self.values['current_navigation'] = 'events'
    user = users.get_current_user()
    form = EventForm()
    self.values['form'] = form
    self.values['form_url'] = blobstore.create_upload_url('/event/upload')
    if not user:
      return self.redirect(users.create_login_url("/event/create"))

class EventEditPage(FrontendPage):
  def show(self):
    self.template = 'event_create'
    user = users.get_current_user()
    form = EventForm()
    if not user:
      return self.redirect(users.create_login_url("/event/create"))
    else:
      event = Event.all().filter('user =', user).get()
      if event:
        self.values['edit'] = str(event.key())
        form = EventForm(obj=event)
        form.gdg_chapters.process_formdata([','.join(event.gdg_chapters)])
    
    self.values['current_navigation'] = 'events'
    self.values['form'] = form
    self.values['form_url'] = blobstore.create_upload_url('/event/upload')

class EventUploadPage(UploadPage):
  def show_post(self):
    self.values['current_navigation'] = 'events'
    user = users.get_current_user()
    if not user:
      return self.redirect(users.create_login_url("/event/create"))

    form = EventForm(self.request.POST)

    self.values['form_url'] = blobstore.create_upload_url('/event/upload')

    if form.validate():
      event = Event()
      if self.request.get('edit') != '':
        ev = Event.get(self.request.get('edit'))
        if user in ev.user:
          event = ev

      existing_event = Event.all().filter('user =', user).get()
      if existing_event:
        event = existing_event

      event.gplus_event_url = self.request.get('gplus_event_url')
      event.location = self.request.get('location')

      event.user = [user]

      upload_files = self.get_uploads('logo')
      if len(upload_files) > 0:
        blob_info = upload_files[0]
        event.logo = '%s' % blob_info.key()

      event.status = self.request.get('status')
      event.agenda = self.request.get_all('agenda')
      event.start = datetime.strptime(self.request.get('start'), '%Y-%m-%d %H:%M')
      event.end = datetime.strptime(self.request.get('end'), '%Y-%m-%d %H:%M')
      event.technologies = self.request.get_all('technologies')
      event.gdg_chapters = self.request.get('gdg_chapters').split(',')
      event.kind_of_support = self.request.get('kind_of_support')
      event.subdomain = self.request.get('subdomain')
      event.put()
      self.values['edit'] = str(event.key())
      self.values['created_successful'] = True
    self.values['form'] = form
    self.template = 'event_create'

class EventPage(FrontendPage):
  def show(self, *paths):
    self.values['current_navigation'] = 'events'
    user = users.get_current_user()
    self.template = 'single_event'
    
    event_id = paths[0]
    self.values['event'] = CEvent(event_id).get()

class EventListPage(FrontendPage):
  def show(self):
    self.values['current_navigation'] = 'events'
    user = users.get_current_user()
    self.template = 'event_list'

    self.values['events'] = CEventList()

    interested_events = Event.all().filter('status =', 'interested')
    planned_events = Event.all().filter('status =', 'planned')
    confirmed_events = Event.all().filter('status =', 'confirmed')
