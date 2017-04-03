#!/usr/bin/python
import flask
import flask_debugtoolbar
import json
import time, datetime
import sys
import logging
import os.path
import os
import base64
import sha
import random
import dateutil.parser
#import codecs
import re
import binascii
import glob
import io

curdir=os.path.dirname(sys.argv[0])
if not curdir:
    curdir='.'
sys.path.append(curdir+'/lib')

import Config
import DB

app = flask.Flask(__name__)

CONFIG=Config.Config("web.config")
CONFIG['alea']=random.getrandbits(32)

COOKIES={}
SESSIONS={}

DEBUG=0

log = logging.getLogger(__name__)
LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}

def getRoot():
    root=CONFIG.get('http.root','')
    return root
def mkURL(url):
    u=getRoot()
    if len(u)==0:
        return url
    while len(u) and u[-1]=='/':
        u=u[:-1]
    while len(url) and url[0]=='/':
        url=url[1:]
    return u+'/'+url
    

def isLogged():
    #if DEBUG>1:
    #    return
    cookie=flask.request.cookies.get(__name__)
    if not cookie or not cookie in COOKIES:
        return flask.redirect(mkURL('/login.html'))

def getUser():
    cookie=flask.request.cookies.get(__name__)
    userKey=COOKIES[cookie]
    
    log.debug("getUser: Cookie: %s = user:%s" % (cookie,userKey))
    
    return userKey
    
def getsessionid():
    return flask.request.cookies.get(__name__)

def store(key,value):
    sessid=getsessionid()
    if not SESSIONS.has_key(sessid):
        SESSIONS[sessid]={}
    SESSIONS[sessid][key]=value

def get(key,default=None):
    sessid=getsessionid()
    if default!=None:
        return SESSIONS[sessid].get(key,default)
    return SESSIONS[sessid].get(key)

def deleteSession():
    sessid=getsessionid()
    if sessid and SESSIONS.has_key(sessid):
        del SESSIONS[sessid]

def buildCookieValue(userKey):
    if not 'alea' in CONFIG:
        alea=random.getrandbits(32)
        CONFIG['alea']=alea
    else:
        alea=CONFIG['alea']
    
    data=str(alea)+userKey
    s=sha.new(data)
    val=base64.b64encode(s.digest())
    return val
    
@app.route('/')
@app.route('/login.html')
@app.route('/logout')
def loginHTML():
    resp=flask.make_response(flask.render_template('login.html', title=CONFIG['title'], root=CONFIG.get('http.root','')))
    resp.set_cookie(__name__,expires=0)
    return resp
    

@app.route('/login', methods=['POST'])
def login():
    nom=flask.request.form['nom']
    prenom=flask.request.form['prenom']
    id=flask.request.form['id']
    data={}
    
    deleteSession()
    
    key="%s.%s" % (prenom.lower(),nom.lower())
    if key not in CONFIG['users']:
        key="%s.%s" % (nom.lower(),prenom.lower())
    try:
        if (key not in CONFIG['users'] or CONFIG['users'][key]['password']!=id):
            data["error"]="Login invalide"
            log.error("%s.%s=%s / %s : %s" % (nom,prenom,id,key,json.dumps(data)))
            return json.dumps(data)
    except:
        data["error"]="Login invalide"
        log.error("%s.%s=%s / %s : %s" % (nom,prenom,id,key,json.dumps(data)))
        return json.dumps(data)
            
    data["message"]="Welcome "+key
    resp=flask.make_response(json.dumps(data))
    cookieValue=buildCookieValue(key)
    CONFIG['users'][key]['cookie']=cookieValue
    COOKIES[cookieValue]=key
    log.info("%s.%s=%s / %s : COOKIE:%s, %s" % (nom,prenom,id,key,cookieValue,json.dumps(data)))
    resp.set_cookie(__name__,cookieValue,path='/')
    return resp

@app.route('/index.html')
def index():
    resp=isLogged()
    if resp:
        return resp
    userKey=getUser()
    
    return flask.render_template('index.html', title=CONFIG['title'], root=CONFIG.get('http.root',''), user=userKey)

@app.route('/js/<file>')
def getfileJS(file):
    return flask.send_from_directory('www/js',file)
@app.route('/css/<file>')
def getfileCSS(file):
    return flask.send_from_directory('www/css',file)
@app.route('/css/images/<file>')
def getfileCSSImages(file):
    return flask.send_from_directory('www/css/images',file)
@app.route('/fonts/<file>')
def getfileFONTS(file):
    return flask.send_from_directory('www/fonts',file)

    
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='univoice filters')
    parser.add_argument('-l', '--listen-tcp', action='append',
            help='Define a TCP listener port. --listen-tcp=port[/topic]')
    parser.add_argument('--logging-level', default='info',
            help='Logging level '+','.join(LOGGING_LEVELS.keys()))
    parser.add_argument('-d', '--debug', action='count',
            help='Activate flask debugtoolbar')
    parser.add_argument('-r', '--root', 
            help='Define/override the URI ROOT path, config: http.root')
    parser.add_argument('-H', '--host', default='127.0.0.1',
            help='Define/override the host to bind to, config: http.host')
    parser.add_argument('-b', '--broker-url', default='redis://localhost:6379',
            help='Define the broker url: redis://localhost:6379')
    parser.add_argument('-R', '--result-backend',
            help='Define the result_backend, default to broker-url')

    args = parser.parse_args()
    logging_level = LOGGING_LEVELS.get(args.logging_level, logging.NOTSET)
    logging.basicConfig(level=logging_level,
                      format='%(asctime)s %(levelname)s: %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')

    if args.broker_url:
        #imap.app.conf.broker_url = args.broker_url
        #imap.app.conf['CELERY_REDIS_HOST']='redis'
        pass
                      
    if args.host:
        CONFIG['http.host']=args.host
    log.info("http.host = '%s'" % CONFIG.get('http.host',''))
    if args.root!=None:
        CONFIG['http.root']=args.root
    log.info("http.root = '%s'" % CONFIG.get('http.root',''))
                      
    if args.debug:
        app.debug=True
        app.config['SECRET_KEY'] = buildCookieValue('secret')
        toolbar=flask_debugtoolbar.DebugToolbarExtension(app)
        
    app.run(CONFIG['http.host'])

