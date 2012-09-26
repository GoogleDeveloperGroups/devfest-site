import webapp2
import jinja2
import json
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from lib.cobjects import CEventBySubdomain

try:
  import settings_local as settings
except:
  import settings

import datetime, time, os

# shameless copy from stackoverflow... thanks tux21b!
def format_datetime(value, format='full'):
  if format == 'full':
    format="%A, %d. %B %Y at %H:%M"
  elif format == 'short':
    format="%a %d. %m. %Y %H:%M"
  return value.strftime(format)

class Page(webapp2.RequestHandler):
  redirected = False
  def redirect(self,*args):
    super(Page,self).redirect(*args)
    self.redirected = True

class JSONPage(Page):
  def get(self, *paths):
    self.pre_output()
    self.show(*paths)
    if not self.redirected:
      self.post_output()

  def post(self, *paths):
    self.pre_output()
    self.show_post(*paths)
    if not self.redirected:
      self.post_output()

  def pre_output(self):
    self.values = {}
    self.values['response'] = {}
    self.values['current_date'] = datetime.datetime.now()

  def post_output(self):
    self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
    self.response.out.write(json.dumps(self.values['response']))

class FrontendPage(Page):
  def get(self, *paths):
    self.pre_output()
    self.show(*paths)
    if not self.redirected:
      self.post_output()

  def post(self, *paths):
    self.pre_output()
    self.show_post(*paths)
    if not self.redirected:
      self.post_output()

  def pre_output(self):
    self.template = ''
    self.values = {}
    self.settings = settings
    self.values['current_date'] = datetime.datetime.now()
    self.values['maps_api_key'] = settings.MAPS_API_KEY

    subdomain = self.request.host.split('.')[0]
    domain = self.request.host.replace(subdomain, 'www')
    if subdomain != 'www':
      try:
        event = CEventBySubdomain(subdomain).get()
        self.redirect('http://'+ domain +'/event/' + str(event.key()))
      except:
        pass

    user = users.get_current_user()
    if user:
      self.values['user'] = user
      self.values['is_admin'] = users.is_current_user_admin()

  def post_output(self):
    self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
    jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__) +'/../templates/'), autoescape=True)

    jinja_environment.filters['datetime'] = format_datetime
    template = jinja_environment.get_template(self.template +'.html')
    self.response.out.write(template.render(self.values))
 
class UploadPage(blobstore_handlers.BlobstoreUploadHandler):
  redirected = False
  def redirect(self,*args):
    super(UploadPage,self).redirect(*args)
    self.redirected = True

  def post(self, *paths):
    self.pre_output()
    self.show_post(*paths)
    if not self.redirected:
      self.post_output()

  def pre_output(self):
    self.template = ''
    self.values = {}
    self.settings = settings
    self.values['current_date'] = datetime.datetime.now()
    self.values['maps_api_key'] = settings.MAPS_API_KEY
    user = users.get_current_user()
    if user:
      self.values['user'] = user
      self.values['is_admin'] = users.is_current_user_admin()

  def post_output(self):
    self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
    jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__) +'/../templates/'), autoescape=True)

    template = jinja_environment.get_template(self.template +'.html')
    self.response.out.write(template.render(self.values))
