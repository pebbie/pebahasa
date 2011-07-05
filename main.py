#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from bottle import *
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import suku
import os

@route('favicon.ico')
def favicon():
	return static_file('favicon.ico', root='static/')

@route('/')
def index():
    return template('index', apptitle='pebahasa', content=template('word_entry'))
    
@post('/penggal')
def query():
	kata = request.forms.get('word', '').strip()
	fon = suku.pecah(kata)
	return template('index', apptitle='pebahasa', content='<div class="formsection">'+kata+" : <strong>"+"-".join(fon)+"</strong></div>")
	
@route('/static/:fname#.+#')
def servestatic(fname):
	return static_file(fname, root='static/')

def main():
    util.run_wsgi_app(default_app())

if __name__ == '__main__':
    main()
