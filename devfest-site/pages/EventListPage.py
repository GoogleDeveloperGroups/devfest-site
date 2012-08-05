from lib.view import FrontendPage
from google.appengine.api import users
from datamodel import Event

class StartPage(FrontendPage):
  def show(self):
    user = users.get_current_user()
    self.template = 'locations'

    interestedEvents = Event.all().filter('status =', 'interested')
    plannedEvents = Event.all().filter('status =', 'planned')
    confirmedEvents = Event.all().filter('status =', 'confirmed')
