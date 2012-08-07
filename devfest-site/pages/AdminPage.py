import gdata.gauth
import gdata.docs.client
from lib.view import FrontendPage
from google.appengine.api import users

class AdminPage(FrontendPage):
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

    self.template = 'admin/index'

class AdminAuthTokenPage(FrontendPage):
  def show(self):
    client = gdata.docs.client.DocsClient(source='Devfest-Website-v1')
    saved_request_token = gdata.gauth.AeLoad('admin_request_token')
    request_token = gdata.gauth.AuthorizeRequestToken(saved_request_token, self.request.uri)
    access_token = client.GetAccessToken(request_token)
    gdata.gauth.AeSave(access_token, 'spreadsheed_token')
    self.template = 'admin/index'
    self.redirect('/admin')
