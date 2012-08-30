from lib.view import FrontendPage
from lib.view import UploadPage
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from lib.model import Session, Event, Day, Slot
from lib.forms import SingleDayForm, SingleSlotForm, DaysSlotsForm
from lib.cobjects import CEvent, CDayList, CSlotList
from datetime import datetime, time
import urllib
import json

# This page is displayed in the context of a single event.
# It shows the currently defined slots and days for an event and
# allows modification of this list. All of this only if the
# user is logged in and is one of the organizers of the event.
class SlotsEditPage(FrontendPage):
  def show(self,event_id):
    self.template = 'slots_edit'
    user = users.get_current_user()
    event = CEvent(event_id).get()
    form = DaysSlotsForm()
    # check permissions...
    if user and event and user in event.organizers:
      # get list of event days
      days = CDayList(event_id).get()
      for d in days:
        d.day = str(d.key())
      # get list of event slots
      slots = CSlotList(event_id).get()
      for s in slots:
        s.slot = str(s.key())
        s.date = s.day.date
      # we need to store the event
      self.values['event'] = event
      form = DaysSlotsForm(days=days,slots=slots)
    elif not user:
      return self.redirect(
                   users.create_login_url("/event/slots/edit/" + event_id))
    else:
      return self.redirect("/event/create");
    self.values['current_navigation'] = 'slots'
    self.values['form_url'] = '/event/slots/upload'
    self.values['form'] = form

# process the results uploaded by the user - and then display the edit form
class SlotsUploadPage(UploadPage):
  def show_post(self):
    self.template = 'slots_edit'
    user = users.get_current_user()
    event_id = self.request.get('event')
    event = CEvent(event_id).get()
    form = DaysSlotsForm(self.request.POST)
    # check permissions...
    if user and event and user in event.organizers:
      # add the days for validation
      if form.validate():
        # start with the days as they are used by slots
        old_days = CDayList(event_id).get()
        for i in range(0,1024):
          prefix = 'days-' + str(i) + '-'
          if self.request.get(prefix + 'date'):
            # is this a modification of an existing day or a new one?
            day_id = self.request.get(prefix + 'day')
            if day_id in [str(d.key()) for d in old_days]:
              day = [d for d in old_days if str(d.key()) == day_id][0]
              # delete from old_days
              old_days = [d for d in old_days if str(d.key()) != day_id]
            else:
              day = Day()
            # fill in values for old/new day
            day.description = self.request.get(prefix + 'description')
            day.date = datetime.strptime(self.request.get(prefix + 'date'), '%Y-%m-%d').date()
            day.event = event
            # update day
            day.put()
        # end for
        # now delete all days not mentioned yet
        for d in old_days:
          d.delete()
        # clear day list
        CDayList.remove_from_cache(event_id)
        # and load uploaded day list
        days = CDayList(event_id).get()
        # now the slots...
        old_slots = CSlotList(event_id).get()
        for i in range(0,1024):
          prefix = 'slots-' + str(i) + '-'
          if self.request.get(prefix + 'name'):
            # is this a modification of an existing slot or a new one?
            slot_id = self.request.get(prefix + 'slot')
            if slot_id in [str(s.key()) for s in old_slots]:
              slot = [s for s in old_slots if str(s.key()) == slot_id][0]
              # delete from old_slots
              old_slots = [s for s in old_slots if str(s.key()) != slots_id]
            else:
              slot = Slot()
            # fill in values for old/new slot
            slot.name = self.request.get(prefix + 'name')
            (hour,min) = self.request.get(prefix + 'start').split(':')
            if hour and min:
              slot.start = time(int(hour), int(min))
            (hour,min) = self.request.get(prefix + 'end').split(':')
            if hour and min:
              slot.end = time(int(hour), int(min))
            date = datetime.strptime(self.request.get(prefix + 'date'), '%Y-%m-%d').date()
            slot.day = [ day for day in days if day.date == date ][0]
            slot.event = event
            # update slot
            slot.put()
        # end for
        # now delete all slots not mentioned yet
        for s in old_slots:
          s.delete()
        # set info that modification was successful
        self.values['modified_successful'] = True
        # clear the cache for the event
        CSlotList.remove_from_cache(event_id)
      # set event into form object
      self.values['event'] = event
    elif not user:
      return self.redirect(
                   users.create_login_url("/event/slots/edit/" + event_id))
    else:
      return self.redirect("/event/create");
    self.values['current_navigation'] = 'slots'
    self.values['form_url'] = '/event/slots/upload'
    self.values['form'] = form
