import webapp2
import jinja2
from google.appengine.api import users
import json

try:
  import settings_local as settings
except:
  import settings

import datetime, time, os

class Page(webapp2.RequestHandler):
  pass

class JSONPage(Page):
  def get(self, *paths):
    self.pre_output()
    self.show(*paths)
    self.post_output()

  def post(self, *paths):
    self.pre_output()
    self.show_post(*paths)
    self.post_output()

  def pre_output(self):
    self.values = {}
    self.values['response'] = {}
    self.values['current_date'] = datetime.datetime.now().strftime("%B %d, %Y %H:%M")

  def post_output(self):
    self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
    self.response.out.write(json.dumps(self.values['response']))

class FrontendPage(Page):
  def get(self, *paths):
    self.pre_output()
    self.show(*paths)
    self.post_output()

  def post(self, *paths):
    self.pre_output()
    self.show_post(*paths)
    self.post_output()

  def pre_output(self):
    self.template = ''
    self.values = {}
    self.values['current_date'] = datetime.datetime.now().strftime("%B %d, %Y %H:%M")
    self.values['maps_api_key'] = settings.MAPS_API_KEY

  def post_output(self):
    self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
    jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__) +'/../templates/'))

    template = jinja_environment.get_template(self.template +'.html')
    self.response.out.write(template.render(self.values))
 
