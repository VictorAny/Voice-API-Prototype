
import webapp2
import os
import cloudstorage as gcs
import json
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from models.py import User

from google.appengine.api import app_identity

def create_file(self, filename, bucketName):
	#write_retry_params = gcs.RetryParams(backoff_factor=1.1)
	BUCKET = "/victor-helloworldtest.appspot.com"
	newfile_name = BUCKET + filename
	gcs_file = gcs.open(newfile_name,'w')
	gcs_file.write('abcde\n')
	gcs_file.write('WOO! IT WORKS!')
	gcs_file.close()
	#self.tmp_filenames_to_clean_up.append(filename)

def createUserWithUserInformation():
    u_name = self.request.get('name')
    u_email = self.request.get('email')
    u_id = self.request.get('id')
    u_profile_url = self.request.get('picture')
    user = User(name=u_name, email=u_email, user_id=u_id, picture_url=u_profile_url)



class PhotoUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload_voice')
        myDict = {"blob_url" : upload_url }
        self.response.write(json.dumps(myDict))
      

class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()[0]
            print upload.key()
            # mynewDict = {"blob_view_url" : '/view_photo/%s' % upload.key()}
            # self.response.write(json.dumps(mynewDict))
             self.redirect('/view_photo/%s' % upload.key())
        except:
            self.response.write('Failure')
        

class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)

class LoginUserHandler(webapp2.RequestHandler):
    def post(self):
        # createUserWithUserInformation()
        try:
            u_name = self.request.get('name')
            u_email = self.request.get('email')
            u_id = self.request.get('id')
            u_profile_url = self.request.get('picture')
            user = User(name=u_name, email=u_email, user_id=u_id, picture_url=u_profile_url)
            user.put()
            responseDict = {"response": "Success"}
            self.response.write(json.dumps(responseDict))
        except:
            errorDict = {"response" : "Error setting up user"}
            self.response.write(json.dumps(errorDict))



app = webapp2.WSGIApplication([
    ('/upload_form', PhotoUploadFormHandler),
    ('/upload_voice', PhotoUploadHandler),
    ('/view_voice/([^/]+)?', ViewPhotoHandler),
    ('/newuser', LoginUserHandler)
], debug=True)
