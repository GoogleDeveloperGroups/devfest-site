from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
import urllib
import json
import re
import string

class Event(db.Model):
  organizers            = db.ListProperty(users.User)
  participants          = db.ListProperty(users.User)
  gdg_chapters          = db.StringListProperty()
  gplus_event_url       = db.StringProperty()
  external_url          = db.StringProperty()
  external_width        = db.IntegerProperty()
  external_height       = db.IntegerProperty()
  register_url          = db.StringProperty()
  register_formkey      = db.StringProperty()
  register_html         = db.TextProperty()
  status                = db.StringProperty()
  location              = db.StringProperty()
  logo                  = db.StringProperty()
  city                  = db.StringProperty()
  country               = db.StringProperty()
  geo_location          = db.GeoPtProperty()
  start                 = db.DateTimeProperty()
  end                   = db.DateTimeProperty()
  agenda                = db.StringListProperty()
  agenda_description    = db.StringProperty()
  technologies          = db.StringListProperty()
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

  # fetch Google Docs form - for event-specific questions
  # first step: start async call
  def set_register_prep(self):
    if self.register_formkey and not self.register_html:
      url = u"https://docs.google.com/spreadsheet/viewform?formkey=%s" % self.register_formkey
      rpc = urlfetch.create_rpc()
      urlfetch.make_fetch_call(rpc, url)
      return rpc
    else:
      return False;

  # get the HTML form from the Google spreadsheet
  def set_register_final(self, rpc):
    if rpc:
      self.register_html = ""
      html = ""
      result = rpc.get_result()
      if result.status_code == 200:
        html = result.content.decode("utf-8")
      self.register_html = html
 
  # during put, update the geo location and fetch (if needed)
  # the Google docs form
  def put(self, **kwargs):
    rpc_geo = self.set_geolocation_prep()
    rpc_register = self.set_register_prep()
    self.set_geolocation_final(rpc_geo)
    self.set_register_final(rpc_register)
    return super(Event, self).put(**kwargs)
    
class Sponsor(db.Model):
  name        = db.StringProperty()
  gplus_id    = db.StringProperty()
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
  event       = db.ReferenceProperty(Event)
  start       = db.DateTimeProperty()
  end         = db.DateTimeProperty()
  room        = db.StringProperty()
  level       = db.StringProperty()
  track       = db.StringProperty()
  live_url    = db.StringProperty()
  youtube_url = db.StringProperty()
  speakers    = db.ListProperty(db.Key)

class Speaker(db.Model):
  first_name  = db.StringProperty()
  last_name   = db.StringProperty()
  gplus_id    = db.StringProperty()
  thumbnail   = db.StringProperty()
  short_bio   = db.TextProperty()
  event       = db.ReferenceProperty(Event)

# session tracks - defined on a per-event base
class Track(db.Model):
  name        = db.StringProperty()
  color       = db.StringProperty()
  abstract    = db.TextProperty()
  event       = db.ReferenceProperty(Event)

