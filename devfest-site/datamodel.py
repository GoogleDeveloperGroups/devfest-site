
from google.appengine.ext import db

class Settings(db.Model):
  user = db.UserProperty()
  location = db.StringProperty(default = 'Mountain View, CA')
  default_zoom = db.IntegerProperty(default = 13)
  admin_user_group = db.ReferenceProperty(UserGroups)

class UserGroups(db.Model):
   gplus_id = db.StringProperty(required=True)
   group_name = db.StringProperty()   
   gplus_img_url = db.StringProperty()
   gplus_event_url = db.StringProperty()
   status = db.StringProperty(choices=set(["interested", "planned", "confirmed"]))   
  
