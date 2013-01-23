try:
  import settings_local as settings
except:
  import settings
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
import urllib
import json
import re
import string
import datetime

class Series(db.Model):
  name                  = db.StringProperty()
  logo                  = db.StringProperty()
  description           = db.StringProperty()  
    
class Event(db.Model):
  series                = db.ReferenceProperty(Series)
  series_key            = db.StringProperty()
  organizers            = db.ListProperty(users.User)
  participants          = db.ListProperty(users.User)
  gdg_chapters          = db.StringListProperty()
  gplus_event_url       = db.StringProperty()
  external_url          = db.StringProperty()
  external_width        = db.IntegerProperty()
  external_height       = db.IntegerProperty()
  register_url          = db.StringProperty()
  register_max          = db.IntegerProperty()
  status                = db.StringProperty()
  name                  = db.StringProperty()
  location              = db.StringProperty()
  logo                  = db.StringProperty()
  city                  = db.StringProperty()
  country               = db.StringProperty()
  geo_location          = db.GeoPtProperty()
  start                 = db.DateTimeProperty()
  end                   = db.DateTimeProperty()
  timezone              = db.FloatProperty()
  agenda                = db.StringListProperty()
  agenda_description    = db.StringProperty(multiline = True)
  technologies          = db.StringListProperty()
  is_vhackandroid       = db.BooleanProperty(default = False)
  kind_of_support       = db.TextProperty()
  expected_participants = db.StringProperty()
  subdomain             = db.StringProperty()  
  approved              = db.BooleanProperty(default = False)
  

  # get the location of the event from Google Maps
  # done in two phases to allow for asynchronous request
  def set_geolocation_prep(self):
    location = self.location
    url = u"http://maps.google.com/maps/api/geocode/json?address=%s&sensor=false" % (urllib.quote(location.encode('utf-8')))
    rpc = urlfetch.create_rpc()
    urlfetch.make_fetch_call(rpc, url)
    return rpc

  # second phase: fetch results from async call
  def set_geolocation_final(self, rpc):
    result = rpc.get_result()
    
    lat = 0.0
    long = 0.0
    city = ''
    country = ''

    if result.status_code == 200:
      data = json.loads(result.content)
      if 'results' in data and len(data['results']) > 0:
        event_location = data['results'][0]
        if 'geometry' in event_location and 'location' in event_location['geometry']:
          lat = event_location['geometry']['location']['lat']
          long = event_location['geometry']['location']['lng']
          self.geo_location = db.GeoPt(lat, long)

        if 'address_components' in event_location:
          for component in event_location['address_components']:
            if "locality" in component['types']:
              self.city = component['long_name']
            if "country" in component['types']:
              self.country = component['long_name']

  # during put, update the geo location and fetch (if needed)
  # the Google docs form
  def put(self, **kwargs):
    rpc_geo = self.set_geolocation_prep()
    # do other stuff which can be done ...
    # (ok, currently async fetch does not make much sense here)
    self.set_geolocation_final(rpc_geo)
    retval = super(Event, self).put(**kwargs)
    if settings.DOCSAPI_CONSUMER_SECRET:
      self.save_to_gdrive()
    return retval

  def save_to_gdrive(self):
    import gdata.gauth
    import gdata.docs.client
    import gdata.spreadsheets.client

    client = gdata.spreadsheets.client.SpreadsheetsClient(source='Devfest-Website-v1')
    access_token = gdata.gauth.AeLoad('spreadsheed_token')
    feed = client.get_list_feed(settings.DOCSAPI_SPREADSHEET_ID, settings.DOCSAPI_SPREADSHEET_EXPORT_WORKSHEET_ID, auth_token=access_token)

    organizers = []
    for organizer in self.organizers:
      organizers.append(organizer.email())

    agenda = []
    for agenda_entry in self.agenda:
      if agenda_entry == '1':
        agenda.append('Conference')
      elif agenda_entry == '2':
        agenda.append('Hackathon')
      elif agenda_entry == '3':
        agenda.append('Barcamp')
      elif agenda_entry == '4':
        agenda.append('GDL Sessions')
      elif agenda_entry == '5':
        agenda.append('Others')

    eventdate = ''
    if self.start is not None:
      eventdate = "%s" % self.start.strftime('%m/%d/%Y %H:%M:%S')
    if self.end is not None:
      eventdate = "%s - %s" % (eventdate, self.end.strftime('%m/%d/%Y %H:%M:%S'))

    data = {
        'timestamp': datetime.datetime.utcnow().strftime('%m/%d/%Y %H:%M:%S'),
        'gdgchaptername': ', '.join(self.gdg_chapters),
        'country': self.country,
        'eventdate': eventdate,
        'organizerse-mailid': ', '.join(organizers),
        'whatareyouplanningtodo': ', '.join(agenda),
        'whatproductstechnologiesyouproposetocoverintheevent': ', '.join(self.technologies),
        'whatkindofsupportyouexpectforthisevent': self.kind_of_support,
        'expectednumberofparticipants': '%s' % self.expected_participants,
        'city': self.city,
        'preferredsubdomainfortheeventwebsite': self.subdomain,
        'eventwebsiteforyourgdgdevfest': self.gplus_event_url,
        'registrationpagefortheevent': self.register_url
        }
    entry = gdata.spreadsheets.data.ListEntry()
    entry.from_dict(data)
    client.add_list_entry(entry, settings.DOCSAPI_SPREADSHEET_ID, settings.DOCSAPI_SPREADSHEET_EXPORT_WORKSHEET_ID, auth_token=access_token)

# Event days
class Day(db.Model):
  date        = db.DateProperty()
  description = db.TextProperty()
  event       = db.ReferenceProperty(Event)

# Event slots
class Slot(db.Model):
  name        = db.StringProperty()
  start       = db.TimeProperty()
  end         = db.TimeProperty()
  day         = db.ReferenceProperty(Day)
  non_session = db.BooleanProperty()
  event       = db.ReferenceProperty(Event)

# session tracks - defined on a per-event base
class Track(db.Model):
  name        = db.StringProperty()
  color       = db.StringProperty()
  icon        = db.StringProperty()
  abstract    = db.TextProperty()
  event       = db.ReferenceProperty(Event)
  event_key   = db.StringProperty()

# Sponsors for an event.
class Sponsor(db.Model):
  name        = db.StringProperty()
  gplus_id    = db.StringProperty()
  url         = db.StringProperty()
  logo        = db.StringProperty()
  description = db.TextProperty()
  level       = db.StringProperty()
  event       = db.ReferenceProperty()
  
# Sessions for an event. Note that there is an m-to-n relation between
# sessions and speakers, it is here reflected as a 'session has many speakers'
# type of property.
class Session(db.Model):
  title       = db.StringProperty()
  abstract    = db.TextProperty()
  slot        = db.ReferenceProperty(Slot)
  slot_key    = db.StringProperty()
  room        = db.StringProperty()
  level       = db.StringProperty()
  track       = db.ReferenceProperty(Track)
  track_key   = db.StringProperty()
  live_url    = db.StringProperty()
  youtube_url = db.StringProperty()
  speakers    = db.ListProperty(db.Key)
  speakers_key = db.StringListProperty()
  # OK, I know this violates "normalized" DB best practice.
  # a slot belongs to an event so I know already the event.
  # but for fast access I duplicate the information here as well.
  event       = db.ReferenceProperty(Event)
  event_key   = db.StringProperty()

class Speaker(db.Model):
  first_name  = db.StringProperty()
  last_name   = db.StringProperty()
  gplus_id    = db.StringProperty()
  company     = db.StringProperty()
  thumbnail   = db.StringProperty()
  short_bio   = db.TextProperty()
  event       = db.ReferenceProperty(Event)

