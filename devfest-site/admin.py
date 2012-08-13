import webapp2
from pages.AdminPage import *

app = webapp2.WSGIApplication([
                              ('^/admin/get_access_token$', AdminAuthTokenPage),
                              ('^/admin/import$', AdminImportPage),
                              ('^/admin$', AdminPage),
                              ],
                              debug=True)
