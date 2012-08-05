from lib.view import FrontendPage
from google.appengine.api import users
from datamodel import Event

class StartPage(FrontendPage):
  def show(self):
    user = users.get_current_user()
    self.template = 'locations'

    interestedEvents = Event.gql("WHERE status='interested'")
    plannedEvents = Event.gql("WHERE status='planned'")
    confirmedEvents = Event.gql("WHERE status='confirmed'")