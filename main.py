
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

from google.appengine.api import app_identity

#-----------------------------------------------------------
#Helpers

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
    user = User()
    user.name = u_name
    user.user_id = u_id
    user.email = u_email
    user.picture_url = u_profile_url
    userKey = ndb.Key(User, u_id)
    print userKey
    user.key = userKey
    print u_name, user.key
    user.put()
    return userKey

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
        try:
            upload = self.get_uploads()[0]
            print upload.key()
            voice_url = upload.key()
            user_id = mydict['user_id']
            # create unique key for voice_id
            user_key = ndb.Key(User, user_id)
            voice_id = Voice.allocate_ids(size=1, parent=user_key)[0]
            voice_key = ndb.Key(Voice, voice_id, parent=user_key)
            userVoice = Voice()
            userVoice.title = mydict['title']
            userVoice.url = voice_url
            userVoice.v_id = voice_id
            userVoice.privacy = mydict['privacy']
            userVoice.tag = mydict['tag']
            userVoice.key = voice_key
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

class LoginUserHandler(MainHelperClass):
    def post(self):
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


class GetUserInformation(MainHelperClass):
    def get(self, user_id):
        userKey = ndb.Key(User, user_id)
        userProfile = userKey.get()
        user_voices = Voice.query(ancestor=userKey).fetch()
        # for voice in user_voices:
        #     print voice.url
        if userProfile:
            user_info = { "response" : "Sucess",
            "userdata" :  {   "name" : userProfile.name,
                                "email" : userProfile.email,
                                "user_id" : userProfile.user_id,
                                "picture_url" : userProfile.picture_url
                },
            "voices" : {
                   #implement voice recieving 
                }
            }
            self.writeJson(user_info)
        else:
            self.writeResponse("Error, user not found")


app = webapp2.WSGIApplication([
    ('/upload_form', VoiceUploadFormHandler),
    ('/upload_voice', VoiceUploadHandler),
    ('/view_voice/([^/]+)?', ViewVoiceHandler),
    ('/newuser', LoginUserHandler),
    ('/user/(\d{16})', GetUserInformation) # ADD REGEX EXPRESSION TO GET INFO.
], debug=True)
