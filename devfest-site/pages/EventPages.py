from lib.view import FrontendPage
from lib.view import UploadPage
from lib.view import Page
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from lib.model import Event
from lib.forms import EventForm
from lib.cobjects import (CEventList, CEvent, CEventScheduleList,
      COrganizersEventList, CSponsorList, CVHAEventList, CSessionList,
      CSessionAgendaList, CSlotList, CDayList, CTrackList,
      CAdminEventList, CSpeakerList)
from datetime import datetime
import urllib
import json
import logging

# convert to int if possible / value exists, to null otherwise
def saveint(str):
  try:
    return int(str)
  except ValueError:
    return None

# convert to bool if possible / value exists, to False otherwise
def savebool(str):
  try:
    return bool(str)
  except ValueError:
    return False

# show all events which are not yet started
class EventSchedulePage(FrontendPage):
  def show(self):
    self.template = 'event_schedule'
    self.values['current_navigation'] = 'events'
    self.values['events'] = CEventScheduleList().get()

# create a new event
class EventCreatePage(FrontendPage):
  def show(self):
    self.template = 'event_edit'
    self.values['current_navigation'] = 'events'
    user = users.get_current_user()
    form = EventForm()
    if not users.is_current_user_admin():
      del form.approved
    self.values['form'] = form
    self.values['form_url'] = blobstore.create_upload_url('/event/upload')
    if not user:
      return self.redirect(users.create_login_url("/event/create"))

# for an organizer, show all "her" events. If only one
# redirect to the one event, if multiple allow to select
class EventSelectPage(FrontendPage):
  def show(self):
    self.template = 'event_select'
    user = users.get_current_user()
    if not user:
      return self.redirect(users.create_login_url("/event/edit"))
    eventlist = COrganizersEventList(user).get()
    eventnumber = len(eventlist)
    if eventnumber == 1:
      event = eventlist[0]
      return self.redirect("/event/edit/" + str(event.key()))
    if eventnumber == 0:
      return self.redirect("/event/create")
    self.values['eventlist'] = eventlist
    self.values['current_navigation'] = 'events'
    
class EventDeletePage(Page):
  def get(self,event_id):
    event = CEvent(event_id).get()
    user = users.get_current_user()
    if user and event:
      if user in event.organizers or users.is_current_user_admin():
        event.delete()
    return self.redirect("/event/edit")

class EventEditPage(FrontendPage):
  def show(self,event_id):
    self.template = 'event_edit'
    user = users.get_current_user()
    form = EventForm()
    event = CEvent(event_id).get()
    if user and event:
      if user in event.organizers or users.is_current_user_admin():
        self.values['event'] = event
        form = EventForm(obj=event)
        form.gdg_chapters.process_formdata([','.join(event.gdg_chapters)])
        form.organizers.process_formdata([','.join([u.email() for u in event.organizers])])
        # special handling: if not admin of application then remove the field
        # 'approved'
        if not users.is_current_user_admin():
          del form.approved
    self.values['current_navigation'] = 'events'
    self.values['form_url'] = blobstore.create_upload_url('/event/upload')
    self.values['form'] = form
    if not user:
      return self.redirect(users.create_login_url("/event/edit"))
    if not event:
      return self.redirect("/events")
    
# target of modification of event
class EventUploadPage(UploadPage):
  def show_post(self):
    self.values['current_navigation'] = 'events'
    form = EventForm(self.request.POST)
    inEdit = False
    self.values['form'] = form
    self.template = 'event_edit'
    self.values['form_url'] = blobstore.create_upload_url('/event/upload')
    user = users.get_current_user()
    if not user:
      return self.redirect(users.create_login_url("/event/edit"))
    # special handling: if not admin of application then remove the field
    # 'approved'
    if not users.is_current_user_admin():
      del form.approved
    if self.request.get('event') != '':
      ev = CEvent(self.request.get('event')).get()
      if user in ev.organizers or users.is_current_user_admin():
        inEdit = True
        self.values['event'] = ev
    if form.validate():
      # create a new event (will be overwritten if in edit mode)
      if inEdit:
        event = ev
      else:
        event = Event()
      event.gplus_event_url = self.request.get('gplus_event_url')
      event.external_url = self.request.get('external_url')
      event.external_width = saveint(self.request.get('external_width'))
      event.external_height = saveint(self.request.get('external_height'))
      event.location = self.request.get('location')
      event.name= self.request.get('name')
      event.register_url = self.request.get('register_url')
      if self.request.get('register_max'):
        event.register_max = saveint(self.request.get('register_max'))
      else:
        event.register_max = 0
      if event.organizers == []:
        event.organizers = [user]
      if users.is_current_user_admin:
        event.approved = savebool(self.request.get('approved'))
      upload_files = self.get_uploads('logo')
      if len(upload_files) > 0:
        blob_info = upload_files[0]
        event.logo = '%s' % blob_info.key()

      event.status = self.request.get('status')
      event.agenda = self.request.get_all('agenda')
      event.start = datetime.strptime(self.request.get('start'), '%Y-%m-%d %H:%M')
      event.end = datetime.strptime(self.request.get('end'), '%Y-%m-%d %H:%M')
      event.timezone = float(self.request.get('timezone'))
      event.agenda_description = self.request.get('agenda_description')
      event.technologies = self.request.get_all('technologies')
      event.gdg_chapters = self.request.get('gdg_chapters').split(',')
      event.organizers = [ users.User(e.strip()) for e in self.request.get('organizers').split(',') ]
      event.kind_of_support = self.request.get('kind_of_support')
      event.subdomain = self.request.get('subdomain')
      event.is_vhackandroid = savebool(self.request.get('is_vhackandroid'))
      event.put()
      # time to invalidate the cache
      CEvent.remove_all_from_cache(event.key())
      self.values['event'] = event
      if inEdit:
        self.values['modified_successful'] = True
      else:
        self.values['created_successful'] = True

# show a single event on the front page
class EventPage(FrontendPage):
  def show(self, event_id):
    self.values['current_navigation'] = 'events'
    user = users.get_current_user()
    self.template = 'single_event'
    event = CEvent(event_id).get()
    if event is None:
      return self.redirect('/404')
    self.values['event'] = event
    self.values['has_registration'] = event.register_url or event.register_max
    self.values['sponsors'] = CSponsorList(event_id).get()

# show agenda of a single event on the front page
class EventAgendaPage(FrontendPage):
  def show(self, event_id):
    self.values['current_navigation'] = 'events'
    user = users.get_current_user()
    self.template = 'single_event_agenda'
    self.values['event'] = CEvent(event_id).get()
    self.values['agenda'] = CSessionAgendaList(event_id).get()
    self.values['slots'] = CSlotList(event_id).get()
    self.values['days'] = CDayList(event_id).get()
    self.values['track_list'] = CTrackList(event_id)
    self.values['speaker_list'] = CSpeakerList(event_id)
    self.values['sponsors'] = CSponsorList(event_id).get()


# list of approved events 
class EventListPage(FrontendPage):
  def show(self):
    self.values['current_navigation'] = 'events'
    user = users.get_current_user()
    self.template = 'event_list'
    # only vha events?
    if self.request.get('vha'):
      self.values['events'] = CVHAEventList()
      self.values['current_navigation'] = 'vhackandroid'
    else:
      if users.is_current_user_admin():
        self.values['events'] = CAdminEventList()
      else:
        self.values['events'] = CEventList()
