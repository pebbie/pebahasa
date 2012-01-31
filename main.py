#!/usr/bin/env python
from bottle import *
try:
    from google.appengine.ext import webapp
    from google.appengine.ext.webapp import util
    isGAE = True
except:
    isGAE = False
    pass
import os

import suku
from hmmtagger import MainTagger
from tokenization import *
from html2text import *
from termextract import *
from summary import *
from capschunking import *

mt = None

@route('favicon.ico')
def favicon():
    return static_file('favicon.ico', root='static/')

@route('/')
@view('newindex')
def index():
    return { 'apptitle':'pebahasa', 'root':request.environ.get('SCRIPT_NAME') }
    
@post('/handler')
def default_handler():
    task = request.forms.get('task', '')
    if task=='htmltext':
        return do_html2text()
    elif task=='extractterm':
        return do_terms()
    elif task=='summary':
        return do_summary()
    elif task=='postag':
        return do_tag()
    elif task=='capschunk':
        return do_caps()
    elif task=='sents':
        return do_sents()    
    response.content_type = 'text/plain'
    return "NotImplemented"

@post('/sents')    
def do_sents():
    response.content_type = 'text/plain'
    lines = request.forms.get('teks', '').strip().split("\n")
    result = []
    for l in lines:
        if len(l) == 0: continue
        out = sentence_extraction(cleaning(l))
        for o in out:
            result.append(o)
    return "<br/><br/>".join(result)
    
@post('/capschunk')    
def do_caps():
    response.content_type = 'text/plain'
    lines = request.forms.get('teks', '').strip().split("\n")
    result = []
    for l in lines:
        if len(l) == 0: continue
        out = sentence_extraction(cleaning(l))
        for o in out:
            tmp = group_caps(o)
            tmp = [" ".join(g) for g in tmp]
            strtmp = "<br/>".join(tmp)
            result.append(strtmp)
    return "<br/><br/>".join(result)

@post('/terms')
def do_terms():
    response.content_type = 'text/plain'
    lines = request.forms.get('teks', '').strip()
    return "<br/>".join(extract_terms(lines))
    
@post('/summary')
def do_summary():
    response.content_type = 'text/plain'
    lines = request.forms.get('teks', '').strip()
    return make_summary(lines)
    
@post('/html2text')
def do_html2text():
    response.content_type = 'text/plain'
    lines = request.forms.get('teks', '').strip()
    return get_text(lines)
    
@post('/penggal')
@view('index')
def penggal():
    kata = request.forms.get('word', '').strip()
    fon = suku.pecah(kata)
    return { 'apptitle':'pebahasa', 'content':'<div class="formsection">'+kata+" : <strong>"+"-".join(fon)+"</strong></div>", 'root':request.environ.get('SCRIPT_NAME') }
    
@route('/tag')
@route('sentence_tagging')
def postag():
    return { 'apptitle':'pebahasa', 'root':request.environ.get('SCRIPT_NAME') }

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
        run(port=8088, reloader=True)

if __name__ == '__main__':
    main()
