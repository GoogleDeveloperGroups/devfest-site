#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
from apiclient.discovery import build_from_document, build
import httplib2

from oauth2client.client import OAuth2WebServerFlow

from flask import Flask, render_template, session, request, redirect, url_for, abort

APPLICATION_ID = "CLIENT_ID"
CLIENT_SECRET = 'CLIENT_SECRET'

app = Flask(__name__)

@app.route('/')
def index():
  if not 'state' in session:
    session['state'] = 0

  person = None
  if 'credentials' in session:
    credentials = session['credentials']

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build("plus", "v1", http=http)
    person = service.people().get(userId='me').execute(http)

  redirecturi = request.base_url + "oauth2callback"

  return render_template('index.html', person=person,
    redirecturi=redirecturi, APPLICATION_ID=APPLICATION_ID)


@app.route('/writemoment', methods=['POST'])
def writemoment():
  if request.method == 'POST' and 'credentials' in session:
    credentials = session['credentials']

    http = httplib2.Http()
    http = credentials.authorize(http)

    discoveryDoc = open('./discovery.json', 'r').read()

    service = build_from_document(
      discoveryDoc, 'https://www.googleapis.com/plus/v1moments/', http=http)

    moments = service.moments()
    body = json.loads(request.form['activity-json'])

    req = moments.insert(userId='me', collection='vault', body=body)
    resp = req.execute()

    session['message'] = "Moment rendered!"
  return redirect(url_for('index'))


@app.route('/signout')
def signout():
  del session['credentials']
  session['message'] = "You have logged out"

  return redirect(url_for('index'))


@app.route('/oauth2callback')
def oauth2callback():
  code = request.args.get('code')

  #  TODO: uncomment once the state parameter works
  state = request.args.get('state')
  if not checkChangeState(state):
    abort(403)

  if code:
    #TODO: update the scopes to include moments.write when it works
    # exchange the authorization code for user credentials
    flow = OAuth2WebServerFlow(APPLICATION_ID,
      CLIENT_SECRET,
      "https://www.googleapis.com/auth/plus.me " +
      "https://www.googleapis.com/auth/plus.moments.write")
    flow.redirect_uri = request.base_url
    credentials = flow.step2_exchange(code)

    # store these credentials for the current user in the session
    session['credentials'] = credentials

  return render_template('complete.html', credentials=credentials)


def checkChangeState(state):
  if session['state'] == int(state):
    session['state'] += 1
    return True
  else:
    return False

if __name__ == '__main__':
  app.secret_key = 'hello world'
  app.run(host='0.0.0.0')
