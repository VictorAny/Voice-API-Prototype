
import webapp2
import os
import cloudstorage as gcs
import json
import time
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from models import User
from models import Voice
from models import Listener

from google.appengine.api import app_identity

#-----------------------------------------------------------
#Helpers
kFetcherBuffer = 20
kNotApproved = 0

class MainHelperClass(webapp2.RequestHandler):
    def writeJson(self, dictionary):
        self.response.out.write(json.dumps(dictionary))

    def writeResponse(self, response):
        responseDictionary = {"response" : response}
        self.response.out.write(json.dumps(responseDictionary))


def create_file(self, filename, bucketName):
	#write_retry_params = gcs.RetryParams(backoff_factor=1.1)
	BUCKET = "/victor-helloworldtest.appspot.com"
	newfile_name = BUCKET + filename
	gcs_file = gcs.open(newfile_name,'w')
	gcs_file.write('abcde\n')
	gcs_file.write('WOO! IT WORKS!')
	gcs_file.close()
	#self.tmp_filenames_to_clean_up.append(filename)

def createUserWithUserInformation(jsonRequest):
    u_name = jsonRequest['name']
    u_email = jsonRequest['email']
    u_id = jsonRequest['id']
    u_profile_url = jsonRequest['picture_url']
    u_username = jsonRequest['username']
    u_slogan = jsonRequest["slogan"]
    user = User()
    user.name = u_name
    user.user_id = u_id
    user.email = u_email
    user.picture_url = u_profile_url
    user.username = u_username
    user.slogan = u_slogan
    userKey = ndb.Key(User, u_id)
    print userKey
    user.key = userKey
    print u_name, user.key
    user.put()
    return userKey


def validateUser(user_id):
    userKey = ndb.Key(User, user_id)
    userProfile = userKey.get()
    if userProfile:
        return userKey
    else:
        return None

def parseVoiceFromVoiceQuery(voiceObjects):
    voiceArray = []
    for voice in voiceObjects:
        voiceDictionary = parseVoiceObject(voice)
        voiceArray.append(voiceDictionary)
    return voiceArray

def parseVoiceObject(voice):

    voiceDictionary = {
                "title" : voice.title,
                "url" : str(voice.url),
                "datecreated" : voice.dateCreated,
                "reach" : voice.reach,
                "v_id" : voice.v_id,
                "tag" : voice.tag,
                "privacy" : voice.privacy
                }
    return voiceDictionary

def parseListenerVoicesAndInformation(listenerProfile, listenerVocies):
    listenerVoiceArray = parseVoiceFromVoiceQuery(listenerVocies)
    sortedArray = sorted(listenerVoiceArray, key=lambda voice: voice.datecreated)
    listenerDict = { "name" : listenerProfile.name,
                    "id"    : listenerProfile.id,
                    "picture_url" : listerProfile.picture_url,
                    "voices" : sortedArray
    }
    return listenerDict


#HANDLERS
#-----------------------------------------------------------


class VoiceUploadFormHandler(MainHelperClass):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload_voice')
        myDict = {"blob_url" : upload_url }
        self.response.out.write(json.dumps(myDict))
      

class VoiceUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        print self.request
        metaData = self.request.get('victor')
        mydict = dict((k.strip(), v.strip()) for k,v in (item.split('=') for item in metaData.split('&')))
        print mydict
        try:
            upload = self.get_uploads()[0]
            print upload.key()
            voice_url = upload.key()
            user_id = mydict['user_id']
            # create unique key for voice_id
            #user_key = ndb.Key(User, user_id)
            voice_id = Voice.allocate_ids(size=1)[0]
            voice_key = ndb.Key(Voice, voice_id)
            userVoice = Voice()
            print "Created voice"
            userVoice.title = mydict['title']
            userVoice.url = voice_url
            userVoice.v_id = voice_id
            userVoice.privacy = mydict['privacy']
            userVoice.tag = mydict['tag']
            userVoice.key = voice_key
            userVoice.userid = user_id
            userVoice.put()

            mynewDict = {"blob_view_url" : '/view_voice/%s' % upload.key()}
            self.response.out.write(json.dumps(mynewDict))
            # self.redirect('/view_photo/%s' % upload.key())
        except:
            self.response.out.write({"respone" : "Failure"})
        

class ViewVoiceHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)

class UserHandler(MainHelperClass):
    def get(self, user_id):
        print "user handler!"
        userKey = ndb.Key(User, user_id)
        userProfile = userKey.get()
        if userProfile:
            user_info = { "response" : "Sucess",
            "userdata" :  {   "name" : userProfile.name,
                            "username" : userProfile.username,
                                "email" : userProfile.email,
                                "user_id" : userProfile.user_id,
                                "picture_url" : userProfile.picture_url,
                                "slogan" : userProfile.slogan
                }
            }
            self.writeJson(user_info)
        else:
            self.writeResponse("Error, user not found")

    def post(self, user_id):
        print "Woohoo posting"
        requestBody = self.request.body
        jsonRequest = json.loads(requestBody)
        user_id = jsonRequest['id']
        userKey = ndb.Key(User, user_id)
        userProfile = userKey.get()
        if userProfile:
            self.writeResponse("Sucess, user already has an account")
        else:
            try:
                user_key = createUserWithUserInformation(jsonRequest)
                self.writeResponse("Sucess, user account created")
            except:
                self.writeResponse("Error setting up user")


class VoicesHandler(MainHelperClass):
    def get(self, user_id):
        print "Voices Handler"
        userKey = validateUser(user_id)
        if userKey:
            user_voices = Voice.query(Voice.userid == user_id).fetch(20)
            voiceArray = parseVoiceFromVoiceQuery(user_voices)
            sucessfulResponse = { "response " : "Sucess",
                "uservoices" : voiceArray
            }
            self.writeJson(sucessfulResponse)
        else:
            self.writeResponse("Error, user not found")


class ListenersHandler(MainHelperClass):
    def get(self, user_id):
        print "Listener's Handler!"
        userKey = validateUser(user_id)
        if userKey:
            print "User key is valid, now attaining listeners"
            #Figure out better way of doing this, go by posts. Get most recent voices from listeners, don't go off all listeners..
            user_listeners = Listener.query(Listener.user_id == user_id).fetch(20)
            listenerArray = []
            print "Listeners objects acquired, now jsonifying information for transmission"
            for listener in user_listeners:
                listenerKey = ndb.Key(User, listener.listener_id)
                if listenerKey:
                    #Change this. We should only return array of listeners, not voices.
                    listenerProfile = listenerKey.get()
                    listenerVoices = Voice.query(ancestor=listenerKey).fetch(20)
                    listenerDictionary = parseListenerVoicesAndInformation(listenerProfile, listenerVoices)
                    listenerArray.append(listenerDictionary)
            sortedResponse = sorted(listenerArray, key= lambda listener: listener["voices"][0].datecreated)
            sucessfulResponse = { "response " : "Sucess",
            "user_listeners" : listenerArray
            }
            self.writeJson(sucessfulResponse)
        else:
            self.writeResponse("Error, user not found")
    
    def post(self, user_id):
        print "Listeners Handler!"
        userKey = validateUser(user_id)
        if userKey:
            requestBody = self.request.body
            jsonRequest = json.loads(requestBody)
            listenerString = jsonRequest['user_ids']
            listenerArray = listenerString.split(',')
            print listenerArray
            for listeneruserid in listenerArray:
                if listeneruserid != "":
                    print listeneruserid
                    userKey = validateUser(listeneruserid)
                    if userKey:
                        listener = Listener()
                        listener.user_id = listeneruserid
                        ##The user who added the person is the one wanting to listen..Thats what their id is the listenerid
                        listener.listener_id = user_id 
                        listener.added = kNotApproved     
                        listener.put() 
                    else:
                        self.writeResponse("Error, listener not found")    
            sucessfulResponse = { "response " : "Sucess"}
            self.writeJson(sucessfulResponse)
        else:
            self.writeResponse("Error, user not found")

#NEEDS QA 
class ListenerVoicesHandler(MainHelperClass):
    def get(self, user_id):
        print "ListenerVoices Handler!"
        userKey = validateUser(user_id)
        if userKey:
            listenerVoices = []
            listenerids = []
            user_listeners = Listener.query(Listener.user_id == user_id).fetch()
            for listener in user_listeners:
                listenerids.append(listener.listener_id)
            voices = Voice.query(Voice.userid.IN(listenerids)).order(Voice.dateCreated).fetch(20)
            print voices
            for voice in voices:
                userKey = validateUser(voice.userid)
                if userKey:
                    userProfile = userKey.get()
                    voiceDict = parseVoiceObject(voice)
                    listenerVoiceDict = {"name" : userProfile.name,
                                        "profile_pic" : userProfile.picture_url,
                                        "id"   : userProfile.user_id,
                                        "userHandler": userProfile.username,
                                        "data" : voiceDict
                     }
                    listenerVoices.append(listenerVoiceDict)
            returnDictionary = {"response" : "Sucess",
                                "info" : listenerVoices
                                }
            self.writeJson(returnDictionary)
        else:
            self.writeResponse("Error, finding user")







app = webapp2.WSGIApplication([
    ('/upload_form', VoiceUploadFormHandler),
    ('/upload_voice', VoiceUploadHandler),
    ('/view_voice/([^/]+)?', ViewVoiceHandler),
    ('/user/(\d{10,18})', UserHandler),
    ('/voice/(\d{10,18})', VoicesHandler),
    ('/listener/(\d{10,18})', ListenersHandler),
    ('/voice/listeners/(\d{10,18})', ListenerVoicesHandler)
], debug=True)
