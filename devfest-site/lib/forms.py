from wtforms import Form, TextField, SelectField, SelectMultipleField, widgets, validators
from wtforms.ext.appengine.db import model_form
from lib.model import Event

class MultiCheckboxField(SelectMultipleField):
  widget = widgets.ListWidget(prefix_label=False)
  option_widget = widgets.CheckboxInput()

class EventForm(Form):
  gplus_event_url = TextField('Google+ Event URL', [validators.URL(), validators.Required()])
  location = TextField('Location', [validators.Length(min=3), validators.Required()])
  status = SelectField('Status', choices=[('1', 'interested'), ('2', 'planned'), ('3', 'confirmed')])
  agenda = MultiCheckboxField('Agenda', choices=[('1', 'Conference'), ('2', 'Hackathon/VHackAndroid'), ('3', 'Barcamp'), ('4', 'Google Developer Live sessions')])
