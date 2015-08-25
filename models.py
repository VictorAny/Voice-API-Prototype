
class User(ndb.Model):
	name = ndb.StringProperty()
	email = ndb.StringProperty()
	user_id = ndb.IntegerProperty()
	picture_url = ndb.StringProperty()
	# string of friend_ids

class Voice(ndb.Model):
	#parent will be User
	title = ndb.StringProperty()
	url = ndb.StringProperty()
	dateCreated = ndb.DateTimeProperty()
	reach = ndb.IntegerProperty()
	v_id = ndb.StringProperty()
	tag = ndb.StringProperty()
	#might make this integer, and treat it like an enum.
	privacy = ndb.StringProperty()

class Listeners(ndb.Model):
	user_id = ndb.StringProperty()
	listener_id = ndb.StringProperty()

