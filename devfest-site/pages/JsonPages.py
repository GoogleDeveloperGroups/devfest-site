from lib.view import JSONPage
from lib.view import Page
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from lib.model import Event
from lib.forms import EventForm
from lib.cobjects import (CEventList, CEvent, CSponsorList,
     CSpeakerList, CSessionList, CTrackList)
from datetime import datetime
import urllib
import json

# export all events
class JsonEventListPage(JSONPage):
  def show(self):
    # go through all events
    response = []
    for country in CEventList().get():
      for event in country["data"]:
        ev = { 'event_id': str(event.key()),
               'country': country["name"],
               'city': event.city,
               'location': event.location,
               'start': event.start.isoformat(),
               'end': event.end.isoformat()
             }
        response.append(ev)
    self.values["response"] = response

# export one event
class JsonEventPage(JSONPage):
  def show(self, event_id):
    event = CEvent(event_id).get()
    response = {
        'gdg_chapters': event.gdg_chapters,
        'gplus_event_url': event.gplus_event_url,
        'status': event.status,
        'location': event.location,
        'logo': event.logo,
        'city': event.city,
        'country': event.country,
        'start': event.start.isoformat(),
        'end': event.end.isoformat(),
        'agenda': event.agenda,
        'agenda_description': event.agenda_description,
        'technologies': event.technologies }
    self.values["response"] = response

# export all speakers of an event
class JsonSpeakerListPage(JSONPage):
  def show(self, event_id):
    response = []
    for speaker in CSpeakerList(event_id).get():
      sp = { 'bio': speaker.short_bio,
             'first_name': speaker.first_name,
             'last_name': speaker.last_name,
             'display_name': speaker.first_name + " " + speaker.last_name,
             'plusone_url': "https://plus.google.com/" + speaker.gplus_id,
             'user_id': str(speaker.key()),
             'speaker_id': str(speaker.key())
           }
      if speaker.thumbnail:
        sp["thumbnail_url"] = "http://www.devfest.info/blob/" + speaker.thumbnail
      response.append(sp)
    self.values["response"] = response

# export all sponsors of an event
class JsonSponsorListPage(JSONPage):
  def show(self, event_id):
    response = []
    for sponsor in CSponsorList(event_id).get():
      sp = { 'company_name': sponsor.name,
             'company_description': sponsor.description
           }
      if sponsor.logo:
        sp["logo_img"] = "http://www.devfest.info/blob/" + sponsor.logo
      if sponsor.gplus_id:
        sp["website"] = "https://plus.google.com/" + sponsor.gplus_id
      response.append(sp)
    self.values["response"] = response

# export all tracks of an event
class JsonTrackListPage(JSONPage):
  def show(self, event_id):
    response = []
    for track in CTrackList(event_id).get():
      tr = { 'name': track.name,
             'color': track.color,
             'abstract': track.abstract
           }
      response.append(tr)
    self.values["response"] = response

# export all sessions of an event
class JsonSessionListPage(JSONPage):
  def show(self, event_id):
    response = []
    for session in CSessionList(event_id).get():
      se = { 'title': session.title,
             'abstract': session.abstract,
             'start': session.slot.start.isoformat(),
             'end': session.slot.end.isoformat(),
             'room': session.room,
             'level': session.level,
             'track': session.track,
             'live_url': session.live_url,
             'youtube_url': session.youtube_url,
             'speakers': [ str(key) for key in session.speakers ]
           }
      response.append(se)
    self.values["response"] = response
