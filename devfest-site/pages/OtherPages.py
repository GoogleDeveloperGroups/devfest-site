from lib.view import FrontendPage
from google.appengine.api import users

class AboutPage(FrontendPage):
    def show(self):
        self.values['current_navigation'] = 'about'
        user = users.get_current_user()
        self.template="about"
        
class ReportBugPage(FrontendPage):
    def show(self):
        user = users.get_current_user()
        self.template="report"   
        
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

class RegisterFormPage(FrontendPage):
    def show(self):
        user = users.get_current_user()
        self.values['current_navigation'] = 'register'
        self.template="register"

class NotFoundPage(FrontendPage):
    def show(self):
        user = users.get_current_user()
        self.template="error404"   
