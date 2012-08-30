from lib.view import FrontendPage
from lib.view import UploadPage
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from lib.model import Sponsor, Event
from lib.forms import SingleSponsorForm, SponsorsForm
from lib.cobjects import CEvent, CSponsorList
from datetime import datetime
import urllib
import json

# This page is displayed in the context of a single event.
# It shows the currently defined sponsors for an event and
# allows modification of this list. All of this only if the
# user is logged in and is one of the organizers of the event.
class SponsorsEditPage(FrontendPage):
  def show(self,event_id):
    self.template = 'sponsors_edit'
    user = users.get_current_user()
    event = CEvent(event_id).get()
    form = SponsorsForm()
    # check permissions...
    if user and event and user in event.organizers:
      # get list of event sponsors
      sponsors = CSponsorList(event_id).get()
      for s in sponsors:
        s.sponsor = s.key()
      # we need to store the event
      self.values['event'] = event
      form = SponsorsForm(sponsors=sponsors)        
    elif not user:
      return self.redirect(
                   users.create_login_url("/event/sponsors/edit/" + event_id))
    else:
      return self.redirect("/event/create");
    self.values['current_navigation'] = 'sponsors'
    self.values['form_url'] = blobstore.create_upload_url(
                                    '/event/sponsors/upload')
    self.values['form'] = form

# process the results uploaded by the user - and then display the edit form
class SponsorsUploadPage(UploadPage):
  def show_post(self):
    self.template = 'sponsors_edit'
    user = users.get_current_user()
    event_id = self.request.get('event')
    event = CEvent(event_id).get()
    form = SponsorsForm(self.request.POST)
    # check permissions...
    if user and event and user in event.organizers:
      if form.validate():
        old_sponsors = CSponsorList(event_id).get()
        for i in range(0,1024):
          prefix = 'sponsors-' + str(i) + '-'
          if self.request.get(prefix + 'name'):
            # is this a modification of an existing sponsor or a new one?
            sponsor_id = self.request.get(prefix + 'sponsor')
            if sponsor_id in [s.key() for s in old_sponsors]:
              sponsor = [s for s in old_sponsors if s.key() == sponsor_id][0]
              # delete from old_sponsor
              old_sponsors = [s for s in old_sponsors if s.key() != sponsor_id]
            else:
              sponsor = Sponsor()
            # fill in values for old/new sponsor
            sponsor.name = self.request.get(prefix + 'name')
            sponsor.gplus_id = self.request.get(prefix + 'gplus_id')
            sponsor.description = self.request.get(prefix + 'description')
            upload_files = self.get_uploads(prefix + 'logo')
            if len(upload_files) > 0:
              blob_info = upload_files[0]
              sponsor.logo = '%s' % blob_info.key()
            sponsor.level = self.request.get(prefix + 'level')
            sponsor.event = event
            # update sponsor
            sponsor.put()
        # end for
        # now delete all sponsors not mentioned yet
        for s in old_sponsors:
          s.delete()
        # set info that modification was successful
        self.values['modified_successful'] = True
        # clear sponsor cache
        CSponsorList.remove_from_cache(event_id)
      # set event into form object
      self.values['event'] = event
    elif not user:
      return self.redirect(
                   users.create_login_url("/event/sponsors/edit/" + event_id))
    else:
      return self.redirect("/event/create");
    self.values['current_navigation'] = 'sponsors'
    self.values['form_url'] = blobstore.create_upload_url(
                                    '/event/sponsors/upload')
    self.values['form'] = form
