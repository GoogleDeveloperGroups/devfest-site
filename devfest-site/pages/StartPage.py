from lib.view import FrontendPage
from google.appengine.api import users

class StartPage(FrontendPage):
  def show(self):
    self.values['current_navigation'] = 'start'
    user = users.get_current_user()
    self.template = 'index'
