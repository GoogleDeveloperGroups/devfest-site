from lib.view import JSONPage
from google.appengine.api import memcache
from google.appengine.ext import db
from lib.model import Track

class MigratePage(JSONPage):
  def show(self):
    # return json of migrated data
    response = []
    # clear memcache
    memcache.flush_all()
    # get all sessions
    tracks = Track.all()
    for track in tracks:
      s = { 'name' : track.name }
      if not track.event_key:
        try:
          track.event_key = str(Track.event.get_value_for_datastore(track))
          s['track'] = track.event_key
        except:
          pass
      # write back the session
      track.put()
      response.append(s)
    self.values['response'] = response
