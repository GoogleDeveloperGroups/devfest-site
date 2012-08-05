from lib.view import FrontendPage
from google.appengine.api import users
from lib.model import Event

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
