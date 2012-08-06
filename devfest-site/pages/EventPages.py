from lib.view import FrontendPage
from google.appengine.api import users
from lib.model import Event
from lib.forms import EventForm

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
      event.status = self.request.get('status')
      event.agenda = self.request.get_all('agenda')
      event.put()
      self.values['created_successful'] = True
    self.values['form'] = form
    self.template = 'event_create'

class EventPage(FrontendPage):
  def show(self, *paths):
    user = users.get_current_user()
    self.template = 'single_event'
    
    raw_id = paths[0]
    id = int(raw_id)
    event = Event.get_by_id(id)

class EventListPage(FrontendPage):
  def show(self):
    user = users.get_current_user()
    self.template = 'event_list'

    interestedEvents = Event.all().filter('status =', 'interested')
    plannedEvents = Event.all().filter('status =', 'planned')
    confirmedEvents = Event.all().filter('status =', 'confirmed')
