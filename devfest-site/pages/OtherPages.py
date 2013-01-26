from lib.view import FrontendPage
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import settings

class AboutPage(FrontendPage):
    def show(self):
        self.values['current_navigation'] = 'about'
        user = users.get_current_user()
        self.template="about"
        
class ReportBugPage(FrontendPage):
    def show(self):
        user = users.get_current_user()
        self.redirect(settings.REPORT_URL)

class BrandingPage(FrontendPage):
    def show(self):
        user = users.get_current_user()
        self.values['current_navigation'] = 'branding'
        self.template="branding"

class FaqPage(FrontendPage):
    def show(self):
        user = users.get_current_user()
        self.values['current_navigation'] = 'faq'
        self.template="eventfaq"

class DevfestwPage(FrontendPage):
    def show(self):
        self.values['current_navigation'] = 'start'
        self.values['current_series'] = 'devfestw'
        user = users.get_current_user()
        self.template="devfestw/devfestw"

class DevfestwFaqPage(FrontendPage):
    def show(self):
        self.values['current_navigation'] = 'faq'
        self.values['current_series'] = 'devfestw'
        user = users.get_current_user()
        self.template="devfestw/devfestw_faq"

class GADC13Page(FrontendPage):
    def show(self):
        self.values['current_navigation'] = 'start'
        self.values['current_series'] = 'gadc13'
        user = users.get_current_user()
        self.template="gadc13"

class GADC13FaqPage(FrontendPage):
    def show(self):
        self.values['current_navigation'] = 'faq'
        self.values['current_series'] = 'gadc13'
        user = users.get_current_user()
        self.template="gadc13_faq"

class VHackAndroidPage(FrontendPage):
    def show(self):
        self.values['current_navigation'] = 'start'
        self.values['current_series'] = 'vhackandroid'
        user = users.get_current_user()
        self.template="vhackandroid"

class VHackAndroidSponsorsPage(FrontendPage):
    def show(self):
        self.values['current_navigation'] = 'sponsors'
        self.values['current_series'] = 'vhackandroid'
        user = users.get_current_user()
        self.template="vhackandroid_sponsors"


class RegisterFormPage(FrontendPage):
    def show(self):
        user = users.get_current_user()
        self.values['current_navigation'] = 'register'
        self.template="register"

# serving blobs, e.g. logos
class BlobPage(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        if not blobstore.get(resource):
            # self.error(404)
            self.redirect("/images/gdgbig.png")
        else:
            self.send_blob(resource)

class NotFoundPage(FrontendPage):
    def show(self):
        user = users.get_current_user()
        self.template="error404"   
