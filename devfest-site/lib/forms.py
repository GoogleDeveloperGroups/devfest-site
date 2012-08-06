from wtforms import Form
from wtforms.ext.appengine.db import model_form
from lib.model import Event

EventForm = model_form(Event, Form)
