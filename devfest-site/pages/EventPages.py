from lib.view import FrontendPage
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from lib.model import Event
from lib.forms import EventForm
from lib.cobjects import CEventList, CEvent
import urllib
import json

class EventCreatePage(FrontendPage):
  def show(self):
    form = EventForm()
    self.values['form'] = form
    self.template = 'event_create'

  def show_post(self):
    form = EventForm(self.request.POST)
    
    if form.validate():
      event = Event()
      event.gplus_event_url = self.request.get('gplus_event_url')
      event.location = self.request.get('location')
      lat, long, city, country = self.get_geolocation(self.request.get('location'))

      event.city = city
      event.country = country
      event.geo_location = db.GeoPt(lat, long)
      event.status = self.request.get('status')
      event.agenda = self.request.get_all('agenda')
      event.put()
      self.values['created_successful'] = True
    self.values['form'] = form
    self.template = 'event_create'

  def get_geolocation(self, location):
    url = "http://maps.google.com/maps/api/geocode/json?address=%s&sensor=false" % (urllib.quote(location))
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

        if 'address_components' in event_location:
          for component in event_location['address_components']:
            print component
            if "locality" in component['types']:
              city = component['long_name']
            if "country" in component['types']:
              country = component['long_name']

    return (lat, long, city, country)

class EventPage(FrontendPage):
  def show(self, *paths):
    user = users.get_current_user()
    self.template = 'single_event'
    
    event_id = paths[0]
    self.values['event'] = CEvent(event_id).get()
    print 'test'
    print self.values['event']

class EventListPage(FrontendPage):
  def show(self):
    user = users.get_current_user()
    self.template = 'event_list'

    self.values['events'] = CEventList()

    interested_events = Event.all().filter('status =', 'interested')
    planned_events = Event.all().filter('status =', 'planned')
    confirmed_events = Event.all().filter('status =', 'confirmed')
