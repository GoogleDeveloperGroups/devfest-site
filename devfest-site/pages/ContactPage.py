from lib.view import FrontendPage
from lib.forms import ContactForm
from google.appengine.api import mail

class ContactPage(FrontendPage):
  def show(self):
    self.template = 'contact'
    self.values['current_navigation'] = 'contact'
    form = ContactForm()
    self.values['form'] = form

  def show_post(self):
    self.values['current_navigation'] = 'contact'

    form = ContactForm(self.request.POST)
    if form.validate():
      mail.send_mail(sender="Devfest.info Contact <contact@devfestglobal.appspotmail.com>",
                         to="Devfest Contact <contact@devfest.info>",
                    subject="Contact Request from the website (%s)" % self.request.get('subject'),
                       body="""Name: %s
Email: %s
Organizer: %s
GDG Chapter: %s
Subject: %s
Body: %s
""" % (self.request.get('name'),
      self.request.get('email'),
      self.request.get('organizer'),
      self.request.get('gdg_chapter'),
      self.request.get('subject'),
      self.request.get('message')))

      self.values['created_successful'] = True

    self.values['form'] = form
    self.template = 'contact'

