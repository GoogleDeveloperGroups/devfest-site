from wtforms import Form, TextField, TextAreaField, SelectField, SelectMultipleField, DateTimeField, FileField, widgets, validators, IntegerField
from wtforms.ext.appengine.db import model_form
from lib.model import Event

class MultiCheckboxField(SelectMultipleField):
  widget = widgets.ListWidget(prefix_label=False)
  option_widget = widgets.CheckboxInput()

class EventForm(Form):
  gplus_event_url = TextField('Google+ Event URL', [validators.URL(), validators.Required()])
  external_url = TextField('External URL (in an iframe or linked to)', [validators.URL()])
  external_width = IntegerField('Width of the iframe (if embedded)', [validators.NumberRange(min=0,max=700)])
  external_height = IntegerField('Height of the iframe (if embedded)', [validators.NumberRange(min=0,max=500)])
  location = TextField('Location', [validators.Length(min=3), validators.Required()])
  status = SelectField('Status', choices=[('1', 'interested'), ('2', 'planned'), ('3', 'confirmed')])
  logo = FileField('Logo')
  agenda = MultiCheckboxField('Agenda', choices=[('1', '<img src="\images/icons/conf-icon.png"> Conference'), ('2', '<img src="\images/icons/hack-icon.png"> Hackathon/VHackAndroid'), ('3', '<img src="\images/icons/barcamp-icon.png"> Barcamp'), ('4', '<img src="\images/icons/gdl-icon.png"> Google Developer Live sessions'),('5', '<img src="\images/icons/others-icon.png"> Others')])
  start = DateTimeField('Start', format="%Y-%m-%d %H:%M")
  end = DateTimeField('End', format="%Y-%m-%d %H:%M")
  gdg_chapters = TextField('GDG Chapters', [validators.Required()], description='Comma seperated list')
  technologies = MultiCheckboxField('What products, technologies you propose to cover in the event', choices=[('Android', 'Android'), ('Chrome', 'Chrome'), ('Google+', 'Google+'), ('App Engine', 'App Engine'), ('Games', 'Games'), ('Google Maps', 'Google Maps'), ('Google Apps', 'Google Apps'), ('Google TV', 'Google TV'), ('Commerce', 'Commerce'), ('Youtube', 'Youtube'), ('Other', 'Other')])
  kind_of_support = TextAreaField('What kind of support you expect for this event?', [validators.Required()])
  subdomain = TextField('Preferred subdomain for the event website')

class ContactForm(Form):
  name = TextField('Your Name', [validators.Required()])
  email = TextField('Email Address', [validators.Email(), validators.Required()])
  organizer = SelectField('Are you GDG organizer?', choices=[('0', 'No'), ('1', 'Yes')])
  gdg_chapter = TextField('Your GDG Chapter')
  subject = TextField('Subject', [validators.Required()])
  message = TextAreaField('Message', [validators.Required()])

