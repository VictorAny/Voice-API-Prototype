
import webapp2
import os
import cloudstorage as gcs
import json
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

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



# class MainHandler(webapp2.RequestHandler):
#     def get(self):
#         upload_url = blobstore.create_upload_url('/upload_photo')
#         # The method must be "POST" and enctype must be set to "multipart/form-data".
#         self.response.write('<html><body>')
#         self.response.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
#         self.response.write('''Upload File: <input type="file" name="file"><br> <input type="submit"
#             name="submit" value="Submit"> </form></body></html>''')

class UserPhoto(ndb.Model):
  user = ndb.StringProperty()
  blob_key = ndb.BlobKeyProperty()

class PhotoUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload_photo')
        myDict = {"blob_url" : upload_url }
        self.response.write(json.dumps(myDict))
        # self.response.write('<html><body>')
        # self.response.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        # self.response.write('''Upload File: <input type="file" name="file"><br> <input type="submit"
        #     name="submit" value="Submit"> </form></body></html>''')
      

class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()[0]
            print upload.key()
            # user_photo = UserPhoto(user=users.get_current_user().user_id(),
            #                        blob_key=upload.key())
            # user_photo.put()

            # self.redirect('/view_photo/%s' % upload.key())
            mynewDict = {"blob_view_url" : '/view_photo/%s' % upload.key()}
            self.response.write(json.dumps(mynewDict))
        except:
            self.response.write('Failure')
        

        # create_file(self,"/yo.txt")
     #    bucket_name = os.environ.get('victor-helloworldtest.appspot.com',
     #                             app_identity.get_default_gcs_bucket_name())

    	# self.response.headers['Content-Type'] = 'text/plain'
    	# self.response.write('Demo GCS Application running from Version: '
     #                    + os.environ['CURRENT_VERSION_ID'] + '\n')
    	# self.response.write('Using bucket name: ' + bucket_name + '\n\n')

    	# bucket = '/' + bucket_name
    	# self.response.write(bucket)
    	# create_file(self, "/hey.txt", bucket)
    

    # def post(self):
    #     print(self.request)
    #     name = self.request.get('feel')
    #     print name


class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        # print self.request
        # print photo_key
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)

class LoginUserHandler(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('name')
        email = self.request.get('email')
        u_id = self.request.get('id')
        profile_pic = self.request.get('picture')



app = webapp2.WSGIApplication([
    ('/upload_form', PhotoUploadFormHandler),
    ('/upload_photo', PhotoUploadHandler),
    ('/view_photo/([^/]+)?', ViewPhotoHandler),
    ('/newuser', LoginUserHandler)
], debug=True)