from lib.view import FrontendPage
from lib.view import UploadPage
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from lib.model import Session, Event, Track, Speaker
from lib.forms import SingleSessionForm, SingleTrackForm, SessionsTracksForm
from datetime import datetime
import urllib
import json

# helper class for filling in the speakers in the form
class SessionFormHelper:
  @staticmethod
  def add_speakers(form,speakers):
    # now iterate through the sessions fields in the form
    for session_form in form.sessions.entries:
      session_form.speakers.choices = [ (str(sp.key()), sp.first_name + " " + sp.last_name) for sp in speakers ]
    return form
    
# This page is displayed in the context of a single event.
# It shows the currently defined sessions for an event and
# allows modification of this list. All of this only if the
# user is logged in and is one of the organizers of the event.
class SessionsEditPage(FrontendPage):
  def show(self,event_id):
    self.template = 'sessions_edit'
    user = users.get_current_user()
    event = Event.get(event_id)
    form = SessionsTracksForm()
    # check permissions...
    if user and event and user in event.organizers:
      # get list of event sessions - assumption: not more than 1024
      sessions = Session.all().filter('event =', event).fetch(1024)
      for s in sessions:
        s.session = str(s.key())
      # get list of event tracks - assumption: not more than 1024
      tracks = Track.all().filter('event =', event).fetch(1024)
      for t in tracks:
        t.track = str(t.key())
      # we need to store the event
      self.values['event'] = event
      form = SessionsTracksForm(sessions=sessions,tracks=tracks)
      speakers = Speaker.all().filter('event =', event).fetch(1024)
      form = SessionFormHelper.add_speakers(form,speakers)
    elif not user:
      return self.redirect(
                   users.create_login_url("/event/sessions/edit/" + event_id))
    else:
      return self.redirect("/event/create");
    self.values['current_navigation'] = 'sessions'
    self.values['form_url'] = '/event/sessions/upload'
    self.values['form'] = form

# process the results uploaded by the user - and then display the edit form
class SessionsUploadPage(UploadPage):
  def show_post(self):
    self.template = 'sessions_edit'
    user = users.get_current_user()
    event_id = self.request.get('event')
    event = Event.get(event_id)
    form = SessionsTracksForm(self.request.POST)
    # check permissions...
    if user and event and user in event.organizers:
      speakers = Speaker.all().filter('event =', event).fetch(1024)
      form = SessionFormHelper.add_speakers(form,speakers)
      # if form.validate():
      if True:
        # start with the tracks as they are used by sessions
        old_tracks = Track.all().filter('event =', event).fetch(1024)
        for i in range(0,1024):
          prefix = 'tracks-' + str(i) + '-'
          if self.request.get(prefix + 'name'):
            # is this a modification of an existing track or a new one?
            track_id = self.request.get(prefix + 'track')
            if track_id in [str(t.key()) for t in old_tracks]:
              track = [t for t in old_tracks if str(t.key()) == track_id][0]
              # delete from old_session
              old_tracks = [t for t in old_tracks if str(t.key()) != track_id]
            else:
              track = Track()
            # fill in values for old/new session
            track.name = self.request.get(prefix + 'name')
            track.color = self.request.get(prefix + 'color')
            track.abstract = self.request.get(prefix + 'abstract')
            track.event = event
            # update track
            track.put()
        # end for
        # now delete all tracks not mentioned yet
        for t in old_tracks:
          t.delete()
        # now the sessions...
        old_sessions = Session.all().filter('event =', event).fetch(1024)
        for i in range(0,1024):
          prefix = 'sessions-' + str(i) + '-'
          if self.request.get(prefix + 'title'):
            # is this a modification of an existing session or a new one?
            session_id = self.request.get(prefix + 'session')
            if session_id in [str(s.key()) for s in old_sessions]:
              session = [s for s in old_sessions if str(s.key()) == session_id][0]
              # delete from old_session
              old_sessions = [s for s in old_sessions if str(s.key()) != session_id]
            else:
              session = Session()
            # fill in values for old/new session
            session.title = self.request.get(prefix + 'title')
            session.abstract = self.request.get(prefix + 'abstract')
            session.start = datetime.strptime(
                   self.request.get(prefix + 'start'), '%Y-%m-%d %H:%M')
            session.end   = datetime.strptime(
                   self.request.get(prefix + 'end'), '%Y-%m-%d %H:%M')
            session.level = self.request.get(prefix + 'level')
            session.track = self.request.get(prefix + 'track')
            session.live_url = self.request.get(prefix + 'live_url')
            session.youtube_url = self.request.get(prefix + 'youtube_url')
            session.event = event
            session.speakers = [ sp.key() for sp in speakers if str(sp.key()) in self.request.get_all(prefix + 'speakers') ]
            # update session
            session.put()
        # end for
        # now delete all sessions not mentioned yet
        for s in old_sessions:
          s.delete()
        # set info that modification was successful
        self.values['modified_successful'] = True
      # set event into form object
      self.values['event'] = event
    elif not user:
      return self.redirect(
                   users.create_login_url("/event/sessions/edit/" + event_id))
    else:
      return self.redirect("/event/create");
    self.values['current_navigation'] = 'sessions'
    self.values['form_url'] = '/event/sessions/upload'
    self.values['form'] = form
