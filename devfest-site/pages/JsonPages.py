from lib.view import JSONPage
from lib.view import Page
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from lib.model import Event
from lib.forms import EventForm
from lib.cobjects import (CEventList, CEvent, CSponsorList,
     CSpeakerList, CSessionList, CTrackList, CSlotList)
from datetime import datetime
import urllib
import json
import base64
import zlib

# export all events
class JsonEventListPage(JSONPage):
  def show(self):
    # go through all events
    response = []
    for country in CEventList().get():
      for event in country["data"]:
        if event.geo_location is not None:
          ev = { 'event_id': str(event.key()),
                 'country': country["name"],
                 'city': event.city,
                 'location': event.location,
                 'name': event.name,
                 'lat': event.geo_location.lat,
                 'lon': event.geo_location.lon,
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
        'name': event.name,
        'lat': event.geo_location.lat,
        'lon': event.geo_location.lon,
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
    self.values["response"] = {'devsite_speakers': response}

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
    self.values["response"] = {'track': response}

# export all sessions of an event
class JsonSessionListPage(JSONPage):
  def show(self, event_id):
    response = []
    # prepare tracks
    tracks = CTrackList(event_id).get()
    track_for_key = { str(t.key()) : t for t in tracks }
    # prepare slots
    slots = CSlotList(event_id).get()
    slot_for_key = { str(s.key()) : s for s in slots }
    for session in CSessionList(event_id).get():
      se = { 'title': session.title,
             'abstract': session.abstract,
             'room': session.room,
             'level': session.level,
             'livestream_url': session.live_url,
             'youtube_url': session.youtube_url,
             'speaker_id': session.speakers_key,
             'id': str(session.key()),
             'attending': 'N'
           }

      se['has_streaming'] = False
      if session.youtube_url != '':
        se['has_streaming'] = True

      try:
        se['track'] = [track_for_key[session.track_key].name]
        se['tags'] = track_for_key[session.track_key].name
      except:
        pass

      try:
        start_time = slot_for_key[session.slot_key].start
        end_time = slot_for_key[session.slot_key].end
        start_date = slot_for_key[session.slot_key].day.date
        se['start_time'] = start_time.strftime('%H:%M')
        se['end_time'] = end_time.strftime('%H:%M')
        se['start_date'] = start_date.strftime('%Y-%m-%d')
        se['end_date'] = start_date.strftime('%Y-%m-%d')
      except:
        pass  
      response.append(se)

    data_crc = zlib.crc32(json.dumps(response))
    etag = base64.b64encode(str(data_crc))
    self.values["response"] = {'etag': etag, 'result': [{'event_timeslots': '', 'events': response, 'event_type': 'sessions'}], 'error': 'No auth token in request'}
