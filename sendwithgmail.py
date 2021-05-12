#!python3
"""
Simple HTTP server for sending emails via gmail
Copyright (C) 2021 Stuart Strolin all rights reserved.
Released under The MIT License. Full text available via https://opensource.org/licenses/MIT

Developed on WSL with Debian Buster. Tested on Raspberry pi, Windows 10 and WSL.
SHOULD work on most other linux distributions.

Code downloaded from the following sources:
https://blog.macuyiko.com/post/2016/how-to-send-html-mails-with-oauth2-and-gmail-in-python.html

"""

DuetMonitorVersion = '1.0.0'


import base64
import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
import smtplib
import urllib.parse
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import lxml.html
import json
import os.path
from os import path
import sys
import argparse
import socket
import threading
import time

GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


def init():
    # parse command line arguments
    parser = argparse.ArgumentParser(
            description='Web Server for sendwithgmail V' + DuetMonitorVersion,
            allow_abbrev=False)
    # Environment
    parser.add_argument('-host', type=str, nargs=1, default=['0.0.0.0'],
                        help='The ip address this service listens on. Default = 0.0.0.0')
    parser.add_argument('-port', type=int, nargs=1, default=[0],
                        help='Specify the port on which the server listens. Default = 0')
    parser.add_argument('-To', type=str, nargs=1, default=[''],
                        help='To: email address. Default = Your gmail')
    parser.add_argument('-Subject', type=str, nargs=1, default=['Message from sendwithgmail'],
                        help='email Subject:. Default = Message from sendwithgmail')
    args = vars(parser.parse_args())

    global host, port, TO_ADDRESS, SUBJECT

    host = args['host'][0]
    port = args['port'][0]  
    TO_ADDRESS = args['To'][0]
    SUBJECT = args['Subject'][0]


"""
Auth and google related functions adapted from:
https://github.com/google/gmail-oauth2-tools/blob/master/python/oauth2.py
https://developers.google.com/identity/protocols/OAuth2

1. Generate and authorize an OAuth2 (generate_oauth2_token)
2. Generate a new access tokens using a refresh token(refresh_token)
3. Generate an OAuth2 string to use for login (access_token)
"""


def command_to_url(command):
    return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)


def url_escape(text):
    return urllib.parse.quote(text, safe='~-._')


def url_unescape(text):
    return urllib.parse.unquote(text)


def url_format_params(params):
    param_fragments = []
    for param in sorted(params.items(), key=lambda x: x[0]):
        param_fragments.append('%s=%s' % (param[0], url_escape(param[1])))
    return '&'.join(param_fragments)


def generate_permission_url(client_id, scope='https://mail.google.com/'):
    params = {}
    params['client_id'] = client_id
    params['redirect_uri'] = REDIRECT_URI
    params['scope'] = scope
    params['response_type'] = 'code'
    return '%s?%s' % (command_to_url('o/oauth2/auth'), url_format_params(params))


def call_authorize_tokens(client_id, client_secret, authorization_code):
    params = {}
    params['client_id'] = client_id
    params['client_secret'] = client_secret
    params['code'] = authorization_code
    params['redirect_uri'] = REDIRECT_URI
    params['grant_type'] = 'authorization_code'
    request_url = command_to_url('o/oauth2/token')
    response = urllib.request.urlopen(request_url, urllib.parse.urlencode(params).encode('UTF-8')).read().decode('UTF-8')
    return json.loads(response)


def call_refresh_token(client_id, client_secret, refresh_token):
    params = {}
    params['client_id'] = client_id
    params['client_secret'] = client_secret
    params['refresh_token'] = refresh_token
    params['grant_type'] = 'refresh_token'
    request_url = command_to_url('o/oauth2/token')
    response = urllib.request.urlopen(request_url, urllib.parse.urlencode(params).encode('UTF-8')).read().decode('UTF-8')
    return json.loads(response)


def generate_oauth2_string(username, access_token, as_base64=False):
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (username, access_token)
    if as_base64:
        auth_string = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
    return auth_string

"""
def test_imap(user, auth_string):
    imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_conn.debug = 4
    imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
    imap_conn.select('INBOX')


def test_smpt(user, base64_auth_string):
    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.set_debuglevel(True)
    smtp_conn.ehlo('test')
    smtp_conn.starttls()
    smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64_auth_string)
"""

def get_authorization(google_client_id, google_client_secret):
    scope = "https://mail.google.com/"
    print('\n Navigate to the following URL to auth:\n', generate_permission_url(google_client_id, scope))
    authorization_code = input('\n Enter verification code: ')
    response = call_authorize_tokens(google_client_id, google_client_secret, authorization_code)
    return response['refresh_token'], response['access_token'], response['expires_in']


def refresh_authorization(google_client_id, google_client_secret, refresh_token):
    response = call_refresh_token(google_client_id, google_client_secret, refresh_token)
    return response['access_token'], response['expires_in']


def send_mail(fromaddr, toaddr, subject, message):
    access_token, expires_in = refresh_authorization(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN)
    auth_string = generate_oauth2_string(fromaddr, access_token, as_base64=True)

    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg.preamble = 'This is a multi-part message in MIME format.'
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)
    part_text = MIMEText(lxml.html.fromstring(message).text_content().encode('utf-8'), 'plain', _charset='utf-8')
    part_html = MIMEText(message.encode('utf-8'), 'html', _charset='utf-8')
    msg_alternative.attach(part_text)
    msg_alternative.attach(part_html)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo(GOOGLE_CLIENT_ID)
    server.starttls()
    server.docmd('AUTH', 'XOAUTH2 ' + auth_string)
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()
    
    
    
###########################
# Integral Web Server
###########################

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import urllib
from urllib.parse import urlparse, parse_qs


class MyHandler(SimpleHTTPRequestHandler):
    #global sendwithgmailVersion
    
    def redirect_url(self, url):
        self.send_response(303)
        self.send_header('Location', url)
        self.end_headers()

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        content = f'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"><html><head></head><body><h2>{message}</h2></body></html>'
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        global TO_ADDRESS, SUBJECT

        if ('favicon.ico' in self.path):
            return
        MESSAGE = False
        tochange = subjectchange = cmderror = ''
        
        query_components = parse_qs(urlparse(self.path).query)
        
        
        
        if query_components.get('command'):
            cmd = query_components['command'][0]
                                    
            if (cmd == 'terminate'):
                shut_down()

            
            #only used if invalid command
            txt = []
            txt.append('Invalid command :  ')
            txt.append(cmd+'<br>')
            cmderror=''.join(txt)

        if (query_components.get('To')):
            TO_ADDRESS = query_components['To'][0]
            #only used if no message
            txt = []
            txt.append('To address was changed to:  ')
            txt.append(TO_ADDRESS+'<br>')
            tochange=''.join(txt)

        if (query_components.get('Subject')):
            SUBJECT = query_components['Subject'][0]
            #only used if no message
            txt = []
            txt.append('Subject was changed to:  ')
            txt.append(SUBJECT+'<br>')
            subjectchange=''.join(txt)          

        if (query_components.get('Message')):
            MESSAGE = query_components['Message'][0]

        if MESSAGE:
            txt = []
            txt.append('sendwithgmail Version: ' + sendwithgmailVersion + '<br>')
            txt.append('To: ' + TO_ADDRESS + '<br>')
            txt.append('From: ' + FROM_ADDRESS + '<br>')
            txt.append('Subject: ' + SUBJECT + '<br>')
            txt.append('Message: ' + MESSAGE + '<br>')
            response = ''.join(txt)
            
            send_mail(FROM_ADDRESS,TO_ADDRESS,
                     SUBJECT,
                     '<b>'+MESSAGE
                     )
         
        else:
            txt = []
            txt.append('Info Message. <br>')
            txt.append('No email was sent<br>')
            response=''.join(txt)
            
        self._set_headers()
        self.wfile.write(self._html(response+tochange+subjectchange+cmderror))

        return
    """
    End of do_Get
    """

    def log_request(self, code=None, size=None):
        pass

    def log_message(self, format, *args):
        pass
    
    
    
    
"""
Utility Functions    
"""    
    
    
    

def savecredentials(thislist):
    enclist = []
    for item in thislist:
        item = item.encode('utf8')  # needs to be byte for compression
        #encitem = b64e(item)
        encitem = b64e(zlib.compress(item, 9))
        encitem = str(encitem, 'utf8') # needs to be string to save as json
        enclist.append(encitem)

    with open("sendwithgmail.conf", "w") as f:
        json.dump(enclist, f)
        f.close()
            

def loadcredentials():
    with open("sendwithgmail.conf", "r") as f:
        enclist = json.load(f)
        f.close()

    thislist = []
    for encitem in enclist:
        encitem = bytes(encitem, 'utf8')
        item = zlib.decompress(b64d(encitem))
        #item = b64d(encitem)
        item = item.decode('utf8') # get back the original string
        thislist.append(item)
        
    return thislist
    

def createHttpListener():
    global listener
    listener = ThreadingHTTPServer((host, port), MyHandler)
    daemon_threads = True
    listener.serve_forever()

def closeHttpListener():
    global listener
    print('!!!!! Stop requested by http listener !!!!!')
    listener.shutdown()
    listener.server_close()
    print('Shutdown')
    sys.exit(0)


def shut_down():
    global httpthread
    send_mail(FROM_ADDRESS,TO_ADDRESS,
              'sendwithgmail has been shut down',
              '<b>This email confirms that sendwithgmail has been shut down.')
    time.sleep(1)  # give pending actions a chance to finish
    try:  # this should close this thread
        httpthread.join(10)
    except:
        pass
    os.kill(thisinstancepid, 9)


# Allows process running in background or foreground to be gracefully
# shutdown with SIGINT (kill -2 <pid> also handles KeyboardInterupt
import signal


def quit_gracefully(*args):
    print('!!!!!! Stopped by SIGINT or CTL+C  !!!!!!')
    shut_down()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit_gracefully)    
    
    global GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN, FROM_ADDRESS, TO_ADDRESS, SUBJECT, MESSAGE
    global thisinstancepid, httpthread
    
    init()  # get the command line inputs
    
    # Check to see if a config file exists
    nocredentials = True
    if path.exists('sendwithgmail.conf'): 
        try:
            creds = loadcredentials()
            GOOGLE_CLIENT_ID = creds[0]
            GOOGLE_CLIENT_SECRET = creds[1]
            GOOGLE_REFRESH_TOKEN = creds[2]
            FROM_ADDRESS = creds[3]
            if TO_ADDRESS == '': TO_ADDRESS = FROM_ADDRESS
            nocredentials = False
        except:
            print('\n***The credentials file - sendwithgmail.conf - may be missing or have incorrect data***\n')
            nocredentials = True
            

    
    if nocredentials:
        print('Setting up Credentials \n')
        GOOGLE_CLIENT_ID = input('\nEnter you google client id\n    The one you got from google console:  ')
        GOOGLE_CLIENT_SECRET = input ('\nEnter you google client secret\n    The one you got from google console:  ')
        FROM_ADDRESS = input ('\nEnter you google email Id\n    The one you use to log into google:  ')
        if TO_ADDRESS == '': TO_ADDRESS = FROM_ADDRESS
        refresh_token, access_token, expires_in = get_authorization(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)

        if not (refresh_token is None):
            GOOGLE_REFRESH_TOKEN = refresh_token
            send_mail(FROM_ADDRESS,TO_ADDRESS,
              'A confirmation email from you for sendwithgmail',
              '<b>This email confirms that the credentials for sendwithgmail are correct</b><br><br>' +
              'So happy to hear from you!')
            confirm = input('\nA confirmation email has been sent to you. Did you get it (y/n):  ')
            if confirm == 'y':
                try:
                    credentials = [GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN, FROM_ADDRESS]
                    savecredentials(credentials)
                except:
                    print('\n***There was a problem saving credentials***')
                    sys.exit(2)
            print('\nSuccess! Your credentials are all set')
            sys.exit(0)
        else:
            print('\nThere was a problem getting tokens.  Please  check your inputs and try again')
            sys.exit(2)
            
    else:
        print('\nUsing Credentials File') 
   
    thisinstancepid = os.getpid()  #Get the pid for later use in shutdown

    if (port != 0):
        try:
            sock = socket.socket()
            if sock.connect_ex((host, port)) == 0:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print('Sorry, port ' + str(port) + ' is already in use.')
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                sys.exit(2)
            # Does this need to be threaded with ThreadingHTTPServer ?
            # or just call createHttpListener()
            httpthread = threading.Thread(target=createHttpListener, args=()).start()
            # httpthread.start()
            send_mail(FROM_ADDRESS,TO_ADDRESS,
              'sendwithgmail has started',
              '<b>This email confirms that sendwithgmail is running on port  '+str(port))
            
            print('***** Started http listener on port:  '+str(port)+'  *****')   

        except KeyboardInterrupt:
            pass  # This is handled as SIGINT
    else:
        print('No port number was provided or port is already in use')
        sys.exit(2)

    

