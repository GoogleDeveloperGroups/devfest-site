import gdata.gauth
import gdata.docs.client
import gdata.spreadsheets.client
from lib.view import FrontendPage
from lib.model import Event
from google.appengine.api import users
from datetime import datetime
import re

class AdminImportPage(FrontendPage):
  def show(self):
    self.template = 'admin/index'
    client = gdata.spreadsheets.client.SpreadsheetsClient(source='Devfest-Website-v1')
    access_token = gdata.gauth.AeLoad('spreadsheed_token')
    feed = client.get_list_feed(self.settings.DOCSAPI_SPREADSHEET_ID,
                                self.settings.DOCSAPI_SPREADSHEET_WORKSHEET_ID,
                                auth_token=access_token)
    if feed.entry:
      for entry in feed.entry:
        ev = entry.to_dict()
        original_users = ev['organizerse-mailid'].split(',')
        event_users = []
        for user in original_users:
          event_users.append(users.User(user.strip()))

        event = Event()
        event.organizers = event_users
        event.location = "%s, %s" % (ev['city'], ev['country'])
        event.gdg_chapters = [ev['gdgchaptername']]
        event.subdomain = ev['preferredsubdomainfortheeventwebsite']
        try:
          num_participants = re.sub(r'[^0-9]', '', ev['expectednumberofparticipants'])
          event.register_max = int(num_participants)
        except:
          pass
        event.kind_of_support = ev['whatkindofsupportyouexpectforthisevent']
        event.approved = False
        try:
          event.start = datetime.strptime(ev['eventdate'], '%m/%d/%Y')
        except:
          pass

        event.put()

class AdminImportCompletePage(FrontendPage):
  def show(self):
    events = Event.all().filter('city =', None)
    for event in events:
      event.put()

class AdminPage(FrontendPage):
  def show(self):
    self.template = 'admin/index'

class AdminAuthorizePage(FrontendPage):
  def show(self):
    client = gdata.docs.client.DocsClient(source='Devfest-Website-v1')

    oauth_callback_url = 'http://%s/admin/get_access_token' % self.request.host
    request_token = client.GetOAuthToken(self.settings.DOCSAPI_SCOPES,
                                         oauth_callback_url,
                                         self.settings.DOCSAPI_CONSUMER_KEY,
                                         consumer_secret=self.settings.DOCSAPI_CONSUMER_SECRET
                                        )

    gdata.gauth.AeSave(request_token, 'admin_request_token')
    self.values['auth_url'] = request_token.generate_authorization_url()

    access_token = gdata.gauth.AeLoad('spreadsheed_token')

    self.template = 'admin/authorize'

class AdminAuthTokenPage(FrontendPage):
  def show(self):
    client = gdata.docs.client.DocsClient(source='Devfest-Website-v1')
    saved_request_token = gdata.gauth.AeLoad('admin_request_token')
    request_token = gdata.gauth.AuthorizeRequestToken(saved_request_token, self.request.uri)
    access_token = client.GetAccessToken(request_token)
    gdata.gauth.AeSave(access_token, 'spreadsheed_token')
    self.template = 'admin/index'
    self.redirect('/admin')
