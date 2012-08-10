from google.appengine.ext import db

class Event(db.Model):
  user = db.UserProperty()
  gplus_id = db.StringProperty()
  gplus_img_url = db.StringProperty()
  gplus_event_url = db.StringProperty()
  status = db.StringProperty()
  location = db.StringProperty()
  city = db.StringProperty()
  country = db.StringProperty()
  geo_location = db.GeoPtProperty()
  start = db.DateTimeProperty()
  end = db.DateTimeProperty()
  agenda = db.StringListProperty()
  agenda_description = db.StringProperty()
    
class UserGroup(db.Model):
  gplus_id = db.StringProperty(required=True)
  group_name = db.StringProperty()
  gplus_img_url = db.StringProperty()
  event = db.ReferenceProperty(Event)

class UserSettings(db.Model):
  user = db.UserProperty()
  gplus_id = db.StringProperty()
  location = db.StringProperty(default='Mountain View, CA')
  default_zoom = db.IntegerProperty(default=13)
  admin_user_group = db.ReferenceProperty(UserGroup)
  
class Sponsor(db.Model):
  gplus_id = db.StringProperty()
  img_url = db.StringProperty()
  event = db.ReferenceProperty()
  
