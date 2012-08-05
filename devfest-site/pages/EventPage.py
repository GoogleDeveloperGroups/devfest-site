from lib.view import FrontendPage
from google.appengine.api import users
from datamodel import Event

class StartPage(FrontendPage):
  def show(self):
    user = users.get_current_user()
    self.template = 'location'
    
    raw_id = self.request.get('id')
    id = int(raw_id)
    event = Event.get_by_id(id)
