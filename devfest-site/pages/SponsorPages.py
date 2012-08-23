from lib.view import FrontendPage
from lib.view import UploadPage
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from lib.model import Sponsor, Event
from lib.forms import SponsorForm
from lib.cobjects import CEventList, CEvent, CEventScheduleList
from datetime import datetime
import urllib
import json

class SponsorCreatePage(FrontendPage):
  def show(self):
    self.template = 'sponsor_create'
    self.values['current_navigation'] = 'sponsor'
    user = users.get_current_user()
    form = SponsorForm()
    self.values['form'] = form
    self.values['form_url'] = blobstore.create_upload_url('/event/sponsor/upload')
    if not user:
      return self.redirect(users.create_login_url("/event/sponsor/create"))

class SponsorEditPage(FrontendPage):
  def show(self):
    self.template = 'sponsor_create'
    user = users.get_current_user()
    form = SponsorForm()
    if self.request.get('edit') != '':
      sponsor = Sponsor.get(self.request.get('edit'))   
      if sponsor:
        self.values['edit'] = str(sponsor.key())
        form = SponsorForm(obj=sponsor)        
    self.values['current_navigation'] = 'sponsor'
    self.values['form_url'] = blobstore.create_upload_url('/event/sponsor/upload')
    self.values['form'] = form
    if not sponsor:
      return self.redirect("event/sponsor/create")
    

class SponsorUploadPage(UploadPage):
  def show_post(self):
    self.values['current_navigation'] = 'sponsors'
    form = SponsorForm(self.request.POST)
    self.values['form'] = form
    self.template = 'sponsor_create'
    self.values['form_url'] = blobstore.create_upload_url('/event/sponsor/upload')
    user = users.get_current_user()
    if not user:
      return self.redirect(users.create_login_url("/event/sponsor/edit"))


    if form.validate():
      sponsor = Sponsor()
      if self.request.get('edit') != '':
        sponsor = Sponsor.get(self.request.get('edit'))        

      sponsor.gplus_id = self.request.get('gplus_id')
      sponsor.description = self.request.get('description')
      sponsor.level = self.request.get('level')
      
      existing_event = Event.all().filter('organizers =', user).get()
      if not existing_event:
        return self.redirect(users.create_login_url("/event/create"))
        
      sponsor.event = existing_event

      upload_files = self.get_uploads('logo')
      if len(upload_files) > 0:
        blob_info = upload_files[0]
        sponsor.logo = '%s' % blob_info.key()

      sponsor.put()
      self.values['edit'] = str(sponsor.key())
      self.values['created_successful'] = True


