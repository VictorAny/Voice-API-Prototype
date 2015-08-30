from google.appengine.ext import ndb


class User(ndb.Model):
	name = ndb.StringProperty()
	email = ndb.StringProperty()
	user_id = ndb.StringProperty()
	picture_url = ndb.StringProperty()

class Voice(ndb.Model):
	#parent will be User
	title = ndb.StringProperty()
	url = ndb.BlobKeyProperty()
	# dateCreated = ndb.DateTimeProperty()
	dateCreated = ndb.StringProperty()
	reach = ndb.IntegerProperty()
	v_id = ndb.IntegerProperty()
	tag = ndb.StringProperty()
	#might make this integer, and treat it like an enum.
	privacy = ndb.StringProperty()

class Listeners(ndb.Model):
	user_id = ndb.StringProperty()
	listener_id = ndb.StringProperty()

