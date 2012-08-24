from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
import urllib
import json

class Event(db.Model):
  organizers            = db.ListProperty(users.User)
  gdg_chapters          = db.StringListProperty()
  gplus_event_url       = db.StringProperty()
  external_url          = db.StringProperty()
  external_width        = db.IntegerProperty()
  external_height       = db.IntegerProperty()
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

  def set_geolocation(self):
    location = self.location
    url = u"http://maps.google.com/maps/api/geocode/json?address=%s&sensor=false" % (urllib.quote(location.encode('utf-8')))
    result = urlfetch.fetch(url)
    
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

  def put(self, **kwargs):
    self.set_geolocation()
    return super(Event, self).put(**kwargs)
    
class Sponsor(db.Model):
  name        = db.StringProperty()
  gplus_id    = db.StringProperty()
  img_url     = db.StringProperty()
  description = db.StringProperty()
  level       = db.StringProperty()
  event       = db.ReferenceProperty()
  
class Session(db.Model):
  title       = db.StringProperty()
  abstract    = db.StringProperty()
  event       = db.ReferenceProperty(Event)
  start       = db.DateTimeProperty()
  end         = db.DateTimeProperty()
  room        = db.StringProperty()
  track       = db.StringProperty()
  is_keynote  = db.BooleanProperty(default = False)
  is_break    = db.BooleanProperty(default = False)
  
class Speaker(db.Model):
  name        = db.StringProperty()
  company     = db.StringProperty()
  img_url     = db.StringProperty()
  short_bio   = db.StringProperty()
  event       = db.ReferenceProperty()
  
class SpeakerSession(db.Model):
  speaker = db.ReferenceProperty(Speaker)
  session = db.ReferenceProperty(Session)
