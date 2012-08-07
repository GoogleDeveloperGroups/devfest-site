import webapp2
from pages.AdminPage import *

config = {}
config['webapp2_extras.sessions'] = {
       'secret_key': 'C^c)2!]%Y+-9S)@[x)W/;6uYh=;}oz',
      }

app = webapp2.WSGIApplication([
                              ('^/admin/get_access_token$', AdminAuthTokenPage),
                              ('^/admin$', AdminPage),
                              ],
                              debug=True, config=config)

