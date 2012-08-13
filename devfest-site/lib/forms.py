from wtforms import Form, TextField, SelectField, SelectMultipleField, DateTimeField, FileField, widgets, validators
from wtforms.ext.appengine.db import model_form
from lib.model import Event

class MultiCheckboxField(SelectMultipleField):
  widget = widgets.ListWidget(prefix_label=False)
  option_widget = widgets.CheckboxInput()

class EventForm(Form):
  gplus_event_url = TextField('Google+ Event URL', [validators.URL(), validators.Required()])
  location = TextField('Location', [validators.Length(min=3), validators.Required()])
  status = SelectField('Status', choices=[('1', 'interested'), ('2', 'planned'), ('3', 'confirmed')])
  logo = FileField('Logo')
  agenda = MultiCheckboxField('Agenda', choices=[('1', '<img src="\images/icons/conf-icon.png">Conference'), ('2', '<img src="\images/icons/hack-icon.png"> Hackathon/VHackAndroid'), ('3', '<img src="\images/icons/barcamp-icon.png"> Barcamp'), ('4', '<img src="\images/icons/gdl-icon.png"> Google Developer Live sessions'),('5', '<img src="\images/icons/others-icon.png"> Others')])
  start = DateTimeField('Start', format="%Y-%m-%d %H:%M")
  end = DateTimeField('End', format="%Y-%m-%d %H:%M")
