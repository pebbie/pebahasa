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
try:
    from google.appengine.ext import webapp
    from google.appengine.ext.webapp import util
    isGAE = True
except:
    isGAE = False
    pass
import suku
import os
from hmmtagger import MainTagger
from tokenization import sentence_extraction, tokenisasi_kalimat, cleaning

mt = None

@route('favicon.ico')
def favicon():
    return static_file('favicon.ico', root='static/')

@route('/')
def index():
    return template('index', apptitle='pebahasa', content=template('word_entry'))
    
@post('/penggal')
def penggal():
    kata = request.forms.get('word', '').strip()
    fon = suku.pecah(kata)
    return template('index', apptitle='pebahasa', content='<div class="formsection">'+kata+" : <strong>"+"-".join(fon)+"</strong></div>")
    
@route('/tag')
def postag():
    return template('index', apptitle='pebahasa', content=template('sentence_tagging'))

def init_tag():
    global mt
    if mt is None:
        mt = MainTagger("resource/Lexicon.trn", "resource/Ngram.trn", 0, 3, 3, 0, 0, False, 0.2, 0, 500.0, 1)
    
@post('/tag')
def do_tag():
    response.content_type = 'text/plain'
    lines = request.forms.get('teks', '').strip().split("\n")
    result = []
    try:
        init_tag()
        for l in lines:
            if len(l) == 0: continue
            out = sentence_extraction(cleaning(l))
            for o in out:
                strtag = " ".join(tokenisasi_kalimat(o)).strip()
                result += [" ".join(mt.taggingStr(strtag))]
    except:
        return "Error Exception"
    return "\n".join(result)
    
@route('/static/:fname#.+#')
def servestatic(fname):
    return static_file(fname, root='static/')

def main():
    if isGAE:
        util.run_wsgi_app(default_app())
    else:
        init_tag()
        run(port=8088)

if __name__ == '__main__':
    main()
