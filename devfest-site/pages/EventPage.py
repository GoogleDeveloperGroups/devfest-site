from lib.view import FrontendPage
from google.appengine.api import users
from lib.model import Event

class StartPage(FrontendPage):
  def show(self, *paths):
    user = users.get_current_user()
    self.template = 'location'
    
    raw_id = paths[0]
    id = int(raw_id)
    event = Event.get_by_id(id)
