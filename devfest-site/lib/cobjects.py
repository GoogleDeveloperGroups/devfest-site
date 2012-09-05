try:
  import settings_local as settings
except:
  import settings

import gdata.gauth
import gdata.spreadsheets.client
from django.core.serializers import deserialize, serialize
from google.appengine.api import memcache
from google.appengine.ext import db, search
from google.appengine.datastore import entity_pb
from lib.model import Event, Sponsor, Speaker, Session, Track, Day, Slot
import datetime
import math
import pickle
import sys

# cached version of an object
class CachedObject():
  entity_collection = []
  cache_key = ''
  max_time = 86400

  # initialize object - first lookup in cache, if not there load from DB
  # or - if object already exists - load it from there
  def __init__(self, data=None):
    # data was not provided? load from cache
    if data is None:
      data = memcache.get(self.cache_key)
    # data was provided or just now found in cache
    if data is not None:
      self.entity_collection = self.deserialize_entities(data)
    else:
      self.load_from_db()
      self.expand_data()
      memcache.set(self.cache_key,
                   self.serialize_entities(self.entity_collection),
                   self.max_time
                  )

  # non-datastore: no data expanding possible
  def expand_data(self):
    pass

  # invalidate cache for a specific key
  @classmethod
  def remove_from_cache(class_, cache_key):
    memcache.delete(cache_key)

  # helper function - return the cached object (the 'real' object)
  def get(self):
    return self.entity_collection

# used for caching objects from datastore
# can be used for either single objects or list of objects
class DbCachedObject(CachedObject):
  # initialize, using an id (for an object or a collection)
  def __init__(self,id="",max_time=3600):
    self.id = id
    self.cache_key = self.__class__.__name__ + ("(%s)" % (id))
    self.max_time = max_time
    CachedObject.__init__(self)

  # invalidate cache for a specific id
  @classmethod
  def remove_from_cache(class_, id=""):
    memcache.delete(class_.__name__ + ("(%s)" % (id)))

  # datastore: data expanding means fetch(None) if needed
  def expand_data(self):
    if isinstance(self.entity_collection, db.Query):
      self.entity_collection = self.entity_collection.fetch(limit=None)

  def serialize_entities(self, models):
    if models is None:
      return None
    elif isinstance(models, db.Model):
      # Just one instance
      return db.model_to_protobuf(models).Encode()
    else:
      # A list of models
      return [db.model_to_protobuf(x).Encode() for x in models]

  def deserialize_entities(self, data):
    if data is None:
      return None
    elif isinstance(data, str):
      return db.model_from_protobuf(entity_pb.EntityProto(data))
    else:
      # A list of models
      return [db.model_from_protobuf(entity_pb.EntityProto(x)) for x in data]

# other cached object - not directly from Datastore
class OCachedObject(CachedObject):
  def serialize_entities(self, models):
    if models is None:
      return None
    else:
      return pickle.dumps(models)

  def deserialize_entities(self, data):
    if data is None:
      return None
    else:
      return pickle.loads(data)

# list of all approved events grouped into countries
class CEventList(OCachedObject):
  def __init__(self):
    self.cache_key = self.__class__.__name__
    self.entity_collection = {}
    self.max_time = 3600
    CachedObject.__init__(self)

  def load_from_db(self):
    self.entity_collection = {}

    events = Event.all().filter('approved =', True)
    event_list = {}
    for event in events:
      if event_list.has_key(event.country) is False:
        event_list[event.country] = []

      event_list[event.country].append(event)

    self.entity_collection = event_list

  # get first half of event countries, sorted by country name
  def get_first_half(self):
    length = len(self.entity_collection)
    half_length = int(math.ceil(length/2))
    return_value = []
    i = 0

    for key in sorted(self.entity_collection.iterkeys()):
      if i < half_length:
        return_value.append({'name': key, 'data': self.entity_collection[key]})
      i = i+1

    return return_value

  # get second half of event countries, sorted by country name
  def get_second_half(self):
    length = len(self.entity_collection)
    half_length = int(math.ceil(length/2))
    return_value = []
    i = 0
    for key in sorted(self.entity_collection.iterkeys()):
      if i >= half_length:
        return_value.append({'name': key, 'data': self.entity_collection[key]})
      i = i+1
    return return_value

  # get all events
  def get(self):
    return_value = []
    for key in sorted(self.entity_collection.iterkeys()):
      return_value.append({'name': key, 'data': self.entity_collection[key]})
    return return_value

  # remove the event list from cache
  @classmethod
  def remove_from_cache(class_):
    CachedObject.remove_from_cache(class_.__name__)

# list of all events grouped into countries
class CAdminEventList(CEventList):
  def __init__(self):
    self.cache_key = self.__class__.__name__
    self.entity_collection = {}
    self.max_time = 3600
    CachedObject.__init__(self)

  def load_from_db(self):
    self.entity_collection = {}

    events = Event.all()
    event_list = {}
    for event in events:
      if event_list.has_key(event.country) is False:
        event_list[event.country] = []

      event_list[event.country].append(event)

    self.entity_collection = event_list

# list of VHackAndroid events
class CVHAEventList(CEventList):
  def load_from_db(self):
    self.entity_collection = {}
    events = Event.all().filter('approved =', True).filter('is_vhackandroid =', True)
    event_list = {}
    for event in events:
      if event_list.has_key(event.country) is False:
        event_list[event.country] = []
      event_list[event.country].append(event)
    self.entity_collection = event_list

# list of sponsors per event
class CSponsorList(DbCachedObject):
  def __init__(self, event_id):
    DbCachedObject.__init__(self, event_id)

  # load all sponsors from db
  def load_from_db(self):
    self.entity_collection = Sponsor.all().filter('event =', CEvent(self.id).get())

# list of speakers per event
class CSpeakerList(DbCachedObject):
  def __init__(self, event_id):
    DbCachedObject.__init__(self, event_id)

  # load all speakers from db
  def load_from_db(self):
    self.entity_collection = Speaker.all().filter('event =', CEvent(self.id).get())

# list of tracks per event
class CTrackList(DbCachedObject):
  def __init__(self, event_id):
    DbCachedObject.__init__(self, event_id)

  # load all tracks from db
  def load_from_db(self):
    self.entity_collection = Track.all().filter('event =', CEvent(self.id).get())

# list of sessions per event
class CSessionList(DbCachedObject):
  def __init__(self, event_id):
    DbCachedObject.__init__(self, event_id)

  # load all sessions from db
  def load_from_db(self):
    sessions = Session.all().filter('event =', CEvent(self.id).get())
    # I have to manually sort them, sorry...
    self.entity_collection = sorted(sessions, key=lambda x: x.slot.start)

# list of sessions per event grouped by slots and rooms
class CSessionAgendaList(OCachedObject):
  def __init__(self, event_id):
    self.cache_key = "SessionAgendaList_"  + ("(%s)" % (event_id))
    self.event_id = event_id
    self.entity_collection = {}
    self.max_time = 3600
    CachedObject.__init__(self)    

  # helper function - key for slot
  def key_for_slot(self, slot):
    return slot.start.strftime("%H:%M") + "-" + slot.end.strftime("%H:%M") + "_" + slot.name

  # load all sessions from db
  # very first order: days
  def load_from_db(self):
    self.entity_collection = {} 
    sessions = Session.all().filter('event =', CEvent(self.event_id).get())    
            
    # list of all rooms per day
    room_list = {}
    # list of all sessions, first per day, then organized by slot
    by_slot = {}
    # list of all sessions, first per day, then organized by room
    by_room = {}
    # list of all sessions, first by day, then by slot then by room
    by_slot_room = {}
    
    for session in sessions:
      # empty room? make a " " out of it.
      if not session.room:
        session.room = " "
      # get the day for the session
      day = session.slot.day.date
      # is day known?
      if not day in room_list:
        room_list[day] = []
        by_slot[day] = {}
        by_room[day] = {}
        by_slot_room[day] = {}
      # is the slot already known?
      session.slot_key = self.key_for_slot(session.slot)
      if session.slot_key not in by_slot[day]:
        by_slot[day][session.slot_key] = []
        by_slot_room[day][session.slot_key] = {}
      # is the room already known?
      if session.room and (session.room not in room_list[day]):
        room_list[day].append(session.room)
        by_room[day][session.room] = []
      # append the session to the three lists
      by_slot[day][session.slot_key].append(session)
      by_room[day][session.room].append(session)
      # we want only one session at one time in one room
      by_slot_room[day][session.slot_key][session.room] = session
      
    # list of all slots - even empty ones. we add an element count
    # for the number of sessions
    slot_list = {}
    date_list = []
    for s in CSlotList(self.event_id).get():
      s.date = s.day.date
      s.slot_key = self.key_for_slot(s)
      if s.slot_key in by_slot:
        s.sessioncount = len(by_slot[s.slot_key])
      else:
        s.sessioncount = 0
      if s.date not in date_list:
        date_list.append(s.date)
        slot_list[s.date] = []
      slot_list[s.date].append(s)

    # store the data!
    self.entity_collection['room_list'] = room_list
    self.entity_collection['slot_list'] = slot_list
    self.entity_collection['date_list'] = date_list
    self.entity_collection['by_slot'] = by_slot
    self.entity_collection['by_room'] = by_room
    self.entity_collection['by_slot_room'] = by_slot_room

# list of all events which are not yet started
class CEventScheduleList(DbCachedObject):
  def __init__(self):
    DbCachedObject.__init__(self,max_time=10)

  def load_from_db(self):
    self.entity_collection = Event.all().filter('approved =', True).filter('start >=', datetime.datetime.now()).order('start')

# list of all events relevant for a single organizer
class COrganizersEventList(DbCachedObject):
  def __init__(self, user):
    self.user = user
    DbCachedObject.__init__(self, user.user_id())

  def load_from_db(self):
    self.entity_collection = Event.all().filter('organizers =', self.user)

# list of days of an event
class CDayList(DbCachedObject):
  def __init__(self, event_id):
    DbCachedObject.__init__(self, event_id)

  # load all days for an event
  def load_from_db(self):
    self.entity_collection = Day.all().filter('event =', CEvent(self.id).get())

# list of slots of an event
class CSlotList(DbCachedObject):
  def __init__(self, event_id):
    DbCachedObject.__init__(self, event_id)

  # load all slots for an event
  def load_from_db(self):
    self.entity_collection = Slot.all().filter('event =', CEvent(self.id).get())

# a single event
class CEvent(DbCachedObject):
  def __init__(self, event_id):
    DbCachedObject.__init__(self, event_id)

  # load single event from DB
  def load_from_db(self):
    self.entity_collection = None

    try:
      data = Event.get(self.id)

      if isinstance(data, Event):
        self.entity_collection = data
    except:
      pass

        
  # remove from cache - one event and all event lists
  @staticmethod
  def remove_all_from_cache(id):
    CEvent.remove_from_cache(id)
    CEventList.remove_from_cache()
    CVHAEventList.remove_from_cache()
    CEventScheduleList.remove_from_cache()
    COrganizersEventList.remove_from_cache()
    CTrackList.remove_from_cache(id)
    CSpeakerList.remove_from_cache(id)
    CSessionList.remove_from_cache(id)
    CSessionAgendaList.remove_from_cache(id)
    CSponsorList.remove_from_cache(id)
    CDayList.remove_from_cache(id)
    CSlotList.remove_from_cache(id)
    # TODO CSession.remove_from_cache_for_event(id)
    CSession.remove_from_cache()


class CSession (DbCachedObject):
  def __init__(self, session_id):
    DbCachedObject.__init__(self, session_id)
        
  # load single session from DB
  def load_from_db(self):
   self.entity_collection = None

   try:
     data = Session.get(self.id)

     if isinstance(data, Session):
       self.entity_collection = data
                        
   except:
     pass


class CSlot (DbCachedObject):
  def __init__(self, slot_id):
    DbCachedObject.__init__(self, slot_id)
        
  # load single session from DB
  def load_from_db(self):
   self.entity_collection = None

   try:
     data = Slot.get(self.id)

     if isinstance(data, Slot):
       self.entity_collection = data
                        
   except:
     pass
    
