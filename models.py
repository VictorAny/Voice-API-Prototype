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
	title = ndb.StringProperty()
	url = ndb.BlobKeyProperty()
	# dateCreated = ndb.DateTimeProperty()
	dateCreated = ndb.DateTimeProperty(auto_now_add=True)
	reach = ndb.IntegerProperty(default=0)
	v_id = ndb.IntegerProperty()
	tag = ndb.StringProperty()
	#might make this integer, and treat it like an enum.
	privacy = ndb.IntegerProperty()
	#holds the user id of the voice creator. To be used solely for easy fetching and comapring. 
	userid = ndb.StringProperty()

class Listener(ndb.Model):	
	"""
	Specifies the user who is being listened to.
	"""
	user_id = ndb.StringProperty()

	"""
	Specifies the user who is listening to the user and is a 'listener'
	"""
	listener_id = ndb.StringProperty()

	"""
	Tells us if the listener has been approved by the user.
	"""
	added = ndb.IntegerProperty()

