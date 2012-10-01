from lib.view import JSONPage
from google.appengine.api import memcache
from google.appengine.ext import db
from lib.model import Session

class MigratePage(JSONPage):
  def show(self):
    # return json of migrated data
    response = []
    # clear memcache
    memcache.flush_all()
    # get all sessions
    sessions = Session.all()
    for session in sessions:
      s = { 'name' : session.title }
      if not session.track_key:
        try:
          session.track_key = str(Session.track.get_value_for_datastore(session))
          s['track'] = session.track_key
        except:
          pass
      if not session.slot_key:
        try:
          session.slot_key = str(Session.slot.get_value_for_datastore(session))
          s['slot'] = session.slot_key
        except:
          pass
      if not session.speakers_key:
        session.speakers_key = []
        try:
          for sp in session.speakers:
            try:
              session.speakers_key.append(str(sp))
            except:
              pass
          s['speakers'] = session.speakers_key
        except:
          pass
      if not session.event_key:
        try:
          session.event_key = str(Session.event.get_value_for_datastore(session))
          s['event'] = session.event_key
        except:
          pass
      # write back the session
      session.put()
      response.append(s)
    self.values['response'] = response
