# Google+ Python App Engine Starter #

VITAL!

For installation, you also need the Google API Python Client, found at:

http://code.google.com/p/google-api-python-client

We suggest using easy_install to install the python client and related
libraries.

% easy_install --upgrade google-api-python-client

You can find more help with installation here:

http://code.google.com/p/google-api-python-client/wiki/Installation

You then need to install appengines libraries in this directory using
enable-app-engine-project, a command installed by the python client.

% cd appengines/
% enable-app-engine-project .

See further instructions here:

http://code.google.com/p/google-api-python-client/wiki/GoogleAppEngine

## Setup Authentication ##

Visit https://code.google.com/apis/console/ to register your application.
 - From the "Project Home" screen, activate access to "Google+ API".
 - Click on "API Access" in the left column
 - Click the button labeled "Create an OAuth2 client ID"
 - Give your application a name and click "Next"
 - Select "Web Application" as the "Application type"
 - Under "Your Site or Hostname" select http:// as the protocol and enter
   "localhost" for the domain name
 - click "Create client ID"
 - click "Edit..." for your new client ID 
 - Add "http://localhost:8080/oauth2callback" as one of the permitted
   callback URLs on a separate line (or whichever port number the
   Google App Engine app assigns to it)

[If you already have something running on 8080, you may get a callback
error when authenticating, as the CLI will attempt to run a server on
port 8080, then 8090, etc.]

Edit the settings.py file and enter the values for the following
properties that you retrieved from the API Console:

- CLIENT_ID
- CLIENT_SECRET
- API_KEY 

## Set up App Engine project ##

If you are on Windows or the Mac, you can use the Google App Engine
Launcher, which you can find at:

http://code.google.com/appengine/downloads.html

Then, you create a new project and choose as its directory the default, then 
click "Play" to try it.  Surf to:

http://localhost:8080 [or whatever port you're on]

to test it.

On Linux or by command-line, use this to start your test server on
your local machine:

% dev_appserver.py [checkout dir]/appengine/

You will need to update the app.yaml file with your own app if you wish to
deploy this.  There's a lot of detail beyond the scope of this document;
see:

http://code.google.com/appengine/
