from google.appengine.ext import ndb


class User(ndb.Model):
	name = ndb.StringProperty()
	username = ndb.StringProperty()
	email = ndb.StringProperty()
	user_id = ndb.StringProperty()
	picture_url = ndb.StringProperty()
	#max is 15 characters??
	slogan = ndb.StringProperty()
	#listeners = ndb.KeyProperty(kind ='User', repeated=True)

class Voice(ndb.Model):
	#parent will be User
	title = ndb.StringProperty()
	url = ndb.BlobKeyProperty()
	# dateCreated = ndb.DateTimeProperty()
	dateCreated = ndb.StringProperty()
	reach = ndb.IntegerProperty(default=0)
	v_id = ndb.IntegerProperty()
	tag = ndb.StringProperty()
	#might make this integer, and treat it like an enum.
	privacy = ndb.StringProperty()
	#holds the user id of the voice creator. To be used solely for easy fetching and comapring. 
	userid = ndb.StringProperty()

class Listener(ndb.Model):
	user_id = ndb.StringProperty()
	listener_id = ndb.StringProperty()
	#used to see if the user has been added backed. 
	#added = ndb.IntegerProperty()

