from django.core.serializers import deserialize, serialize
from google.appengine.api import memcache
from google.appengine.ext import db, search
from google.appengine.datastore import entity_pb
from lib.model import Event
import math
import pickle

class CachedObject():
  entity_collection = []
  cache_key = ''
  max_time = 86400

  def __init__(self):
    data = memcache.get(self.cache_key)
    if data is not None:
      self.entity_collection = self.deserialize_entities(data)
    else:
      self.load_from_db()
      memcache.set(self.cache_key,
                   self.serialize_entities(self.entity_collection),
                   self.max_time
                  )

  def remove_from_cache(self, *args, **kwds):
    memcache.delete(self.cache_key)

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

class CEventList(OCachedObject):
  def __init__(self):
    self.cache_key = "Eventlist"
    self.entity_collection = {}
    self.max_time = 10
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

  def get(self):
    return self.entity_collection

  def get_first_half(self):
    length = len(self.entity_collection)
    half_length = int(math.ceil(length/2))
    return_value = {}
    i = 0
    for key in self.entity_collection:
      if i < half_length:
        return_value[key] = self.entity_collection[key]
      i = i+1

    return return_value

  def get_second_half(self):
    length = len(self.entity_collection)
    half_length = int(math.ceil(length/2))
    return_value = {}
    i = 0
    for key in self.entity_collection:
      if i >= half_length:
        return_value[key] = self.entity_collection[key]
      i = i+1

    return return_value

class CEvent(CachedObject):
  def __init__(self, event_id):
    self.event_id = event_id
    self.max_time = 3600
    self.cache_key = "Event(%s)" % (self.id)
    CachedObject.__init__(self)

  def load_from_db(self):
    self.entity_collection = None
    data = Event.get_by_id(id)

    if isinstance(data, Event):
      self.entity_collection = data

  def get(self):
    return self.entity_collection
