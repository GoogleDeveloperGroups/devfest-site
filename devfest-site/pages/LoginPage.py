from lib.view import FrontendPage
from google.appengine.api import users

class LoginPage(FrontendPage):
  def show(self):
    self.template = 'login'
    user = users.get_current_user()
    if not user:
      return self.redirect(users.create_login_url("/"))
    else:
      return self.redirect('/')


