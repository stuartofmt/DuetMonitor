#!python3

"""
Simple HTTP server for monitoring Duet Status and sending change notifications emails via gmail.
Copyright (C) 2021 Stuart Strolin all rights reserved.
Released under The MIT License. Full text available via https://opensource.org/licenses/MIT

Developed on WSL with Debian Buster. Tested on Raspberry pi, Windows 10 and WSL.
SHOULD work on most other linux distributions.

Some code downloaded from the following sources:
https://blog.macuyiko.com/post/2016/how-to-send-html-mails-with-oauth2-and-gmail-in-python.html
<Add in Duetlapse3 reference>

"""

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
import requests


DuetMonitorVersion = '1.0.1'
validStatusValues = ('all', 'none', 'halted', 'idle', 'busy', 'processing', 'paused', 'pausing', 'resuming')

GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


def init():
    # parse command line arguments
    parser = argparse.ArgumentParser(
            description='Web Server for DuetMonitor V' + DuetMonitorVersion,
            allow_abbrev=False)
    # Environment
    parser.add_argument('-host', type=str, nargs=1, default=['0.0.0.0'],
                        help='The ip address this service listens on. Default = 0.0.0.0')
    parser.add_argument('-port', type=int, nargs=1, default=[0],
                        help='Specify the port on which the server listens. Default = 0')
    parser.add_argument('-To', type=str, nargs=1, default=[''],
                        help='To: email address. Default = Your gmail')
    parser.add_argument('-Subject', type=str, nargs=1, default=['DuetMonitor:  Message'],
                        help='email Subject:. Default = Message from DuetMonitor')
    parser.add_argument('-duet', type=str, nargs=1, default=['localhost'],
                        help='Name of duet or ip address. Default = localhost')
    parser.add_argument('-poll', type=float, nargs=1, default=[60])
    parser.add_argument('-monitors', nargs='+', default=['all'],
                        help='Status to monitor. Default = all')
    parser.add_argument('-dontstart', action='store_true', help='Default = start monitoring')
    parser.add_argument('-nodisplaymessages', action='store_true', help='Default = display Messages')
    parser.add_argument('-noinfomessages', action='store_true', help='Default = display info messages')
    args = vars(parser.parse_args())

    global host, port, TO_ADDRESS, SUBJECT, duet, poll, monitors, startmonitor, displaymessages, infomessages

    host = args['host'][0]
    port = args['port'][0]  
    TO_ADDRESS = args['To'][0]
    SUBJECT = args['Subject'][0]
    duet = args['duet'][0]
    poll = args['poll'][0]
    monitors = args['monitors']
    startmonitor = not args['dontstart']
    displaymessages = not args['nodisplaymessages']
    infomessages = not args['noinfomessages']

    if infomessages and poll > 6:  # Reporting on (info) message so must poll at least every 8 sec
        poll = 6                  # Use 6 sec to be safe and allow for syn delays e.g. calling gmail

    validvalue = True
    for item in monitors:
        if item not in validStatusValues:
            print('\nInvalid Status used: ' + item)
            validvalue = False
        if item == 'none':
            monitors = item
            print('Status changes will NOT be monitored')
            break

    if not validvalue:
        print('\nOne or more invalid values in : ' + ','.join(monitors))
        print('\nValid values are: : ' + ','.join(validStatusValues))
        print('\nStatus changes will NOT be monitored')
        monitors = 'none'

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
        global TO_ADDRESS, SUBJECTPRE, monitoring, monitors, displaymessages, infomessages, DuetMonitorVersion
        validoptions = ('command', 'monitors', 'displaymessages', 'infomessages', 'To', 'Subject', 'Message')
        if 'favicon.ico' in self.path:
            return

        MESSAGE = tochange = subjectchange = cmdmsg = ''
        
        query_components = parse_qs(urlparse(self.path).query)
        invalidoptions = ''
        if query_components:
            for option in query_components:
                if not option in validoptions:
                    invalidoptions = invalidoptions + option + ','
            if invalidoptions != '':
                invalidoptions = invalidoptions.rstrip(',')
                txt = []
                txt.append('<br>One or more invalid options were detected:  ' + invalidoptions + '<br>')
                txt.append('<br>Valid options are:  ' + ','.join(validoptions))
                txt.append('<br>Request was ignored')
                response = ''.join(txt)
                self._set_headers()
                self.wfile.write(self._html(response))
                return

        if query_components.get('command'):
            cmd = query_components['command'][0].lower()
            if (cmd == 'terminate'):
                shut_down()
                return
            elif cmd == 'start':
                if not monitoring:
                    startMonitoring()
                    txt = []
                    txt.append('<br>Monitoring has been started<br>')
                    cmdmsg = cmdmsg + ''.join(txt)
                else:
                    txt = []
                    txt.append('<br>Command was ignored because Monitoring is already started<br>')
                    cmdmsg = cmdmsg + ''.join(txt)
            elif cmd == 'stop':
                monitoring = False
                txt = []
                txt.append('<br>Monitoring has been Stopped')
                cmdmsg = cmdmsg + ''.join(txt)
            else:
                # only used if invalid command
                txt = []
                txt.append('<br>Invalid command :  ')
                txt.append(cmd + '<br>')
                cmdmsg = cmdmsg + ''.join(txt)

        if query_components.get('monitors'):
            value = query_components['monitors'][0].lower()
            value = value.replace(' ','') #get rid of spaces
            value = value.split(',')
            validvalue = True
            invalid = ''
            for item in value:
                print(item)
                if not item in validStatusValues:
                    invalid = invalid + item + ' , '   # will always have trailing comma - get rid of if used later
                    validvalue = False
                if item == 'none':
                    value = item  # Over-ride of variable value - will be ok because of break
                    validvalue = True
                    break

            if validvalue:
                monitors = value
                txt = []
                txt.append('<br>Monitors have been set to: ' + ','.join(monitors))
                cmdmsg = cmdmsg + ''.join(txt)
            else:
                invalid = invalid.rstrip(',')
                txt = []
                txt.append('<br>The following invalid values were detected:  ' + invalid+ '<br>')
                txt.append('<br>Valid values are:  ' + ','.join(validStatusValues))
                txt.append('<br>monitors were not changed')
                cmdmsg = cmdmsg + ''.join(txt)

        if query_components.get('displaymessages'):
            value = query_components['displaymessages'][0].lower()
            print('displaymessages = ' + value)
            if value == 'true':
                displaymessages = True
                txt = []
                txt.append('<br>display Messages will NOT  be monitored')
                cmdmsg = cmdmsg + ''.join(txt)
            elif value == 'false':
                displaymessages = False
                txt = []
                txt.append('<br>display Messages WILL be monitored')
                cmdmsg = cmdmsg + ''.join(txt)
            else:
                txt = []
                txt.append('<br>Invalid value for displaymessages :  ')
                txt.append('<br>Can be either True or False)')
                cmdmsg = cmdmsg + ''.join(txt)

        if query_components.get('infomessages'):
            value = query_components['infomessages'][0].lower()
            if value == 'true':
                infomessages = True
                txt = []
                txt.append('<br>info Messages will NOT be monitored')
                cmdmsg = cmdmsg + ''.join(txt)
            elif value == 'false':
                infomessages = False
                txt = []
                txt.append('<br>info Messages WILL be monitored')
                cmdmsg = cmdmsg + ''.join(txt)
            else:
                txt = []
                txt.append('<br>Invalid value for infomessages :  ')
                txt.append('<br>Can be either True or False)')
                cmdmsg = cmdmsg + ''.join(txt)

        if query_components.get('To'):
            TO_ADDRESS = query_components['To'][0]
            #only used if no message
            txt = []
            txt.append('<br>To address was changed to:  ')
            txt.append(TO_ADDRESS+'<br>')
            cmdmsg = cmdmsg + ''.join(txt)

        if query_components.get('Subject'):
            SUBJECTPRE = query_components['Subject'][0]+''
            #only used if no message
            txt = []
            txt.append('<br>Subject prefix was changed to:  ')
            txt.append(SUBJECTPRE+'<br>')
            cmdmsg = cmdmsg + ''.join(txt)

        if query_components.get('Message'):
            MESSAGE = query_components['Message'][0]

            if MESSAGE != '':
                txt = []
                txt.append('<br>Message was sent. <br>')
                txt.append('To: ' + TO_ADDRESS + '<br>')
                txt.append('From: ' + FROM_ADDRESS + '<br>')
                txt.append('Subject: ' + SUBJECTPRE + '<br>')
                txt.append('Message: ' + MESSAGE + '<br>')
                cmdmsg = cmdmsg + ''.join(txt)

                SUBJECT = SUBJECTPRE
                MESSAGE = '<br>' + MESSAGE
                send_mail(FROM_ADDRESS, TO_ADDRESS, SUBJECT, MESSAGE)
            else:
                txt = []
                txt.append('<br>Cannot send a blank message. <br>')
                cmdmsg = cmdmsg + ''.join(txt)

        txt = []
        txt.append('Information Message.<br> DuetMonitor Version:  ' + DuetMonitorVersion + '<br>')
        txt.append('<br>Email Settings')
        txt.append('<br>Subject prefix =&nbsp; &nbsp;' + SUBJECTPRE)
        txt.append('<br>To =&nbsp;&nbsp;' + TO_ADDRESS)
        txt.append('<br>General Settings')
        txt.append('<br>Monitoring =&nbsp;&nbsp;' + str(monitoring))
        txt.append('<br>Monitors =&nbsp;&nbsp;' + ','.join(monitors))
        txt.append('<br>Monitor display messages =&nbsp;&nbsp;' + str(displaymessages))
        txt.append('<br>Monitor info messages =&nbsp;&nbsp;' + str(infomessages))
        txt.append('<br>Polling interval (sec) =&nbsp;&nbsp;' + str(poll))
        txt.append('<br><br><br><br>')
        response = ''.join(txt)


        self._set_headers()
        self.wfile.write(self._html(response+cmdmsg))

        return
    """
    End of do_Get
    """

    def log_request(self, code=None, size=None):
        pass

    def log_message(self, format, *args):
        pass
"""
Duet APIs
"""


def getDuetVersion():
    # Used to get the status information from Duet
    try:
        model = 'rr_model'
        URL = ('http://' + duet + '/rr_model?key=boards')
        r = urlCall(URL, 5)
        j = json.loads(r.text)
        version = j['result'][0]['firmwareVersion']
        return 'rr_model', version
    except:
        try:
            model = '/machine/system'
            URL = ('http://' + duet + '/machine/status')
            r = urlCall(URL, 5)
            j = json.loads(r.text)
            version = j['boards'][0]['firmwareVersion']
            return 'SBC', version
        except:
            return 'none', '0'

def connectDuet():
    connected = False
    # Get connected to the printer.

    apimodel, printerVersion = getDuetVersion()

    if apimodel == 'none':
        print('')
        print('###############################################################')
        print('The printer at ' + duet + ' did not respond')
        print('Check the ip address or logical printer name is correct')
        print('Duet software must support rr_model or /machine/status')
        print('###############################################################')
        print('')
        connected = False
        message =  ('The printer at ' + duet + ' did not respond')
        return apimodel, connected

    majorVersion = int(printerVersion[0])

    if majorVersion >= 3:
        message = 'Connected to printer at ' + duet + ' using Duet version ' + printerVersion + '\nand using API access method ' + apimodel
        print('')
        print('###############################################################')
        print( message)
        print('###############################################################')
        print('')
        connected = True
        return apimodel, connected
    else:
        print('')
        print('###############################################################')
        print('The printer at ' + duet + ' needs to be at version 3 or above')
        print('The version on this printer is ' + printerVersion)
        print('###############################################################')
        print('')
        connected = False
        message =  ('The printer at ' + duet + ' needs to be at version 3 or above')
        return apimodel, connected

def urlCall(url, timelimit):
    loop = 0
    limit = 2  # Started at 2 - seems good enough to catch transients
    while loop < limit:
        try:
            r = requests.get(url, timeout=timelimit)
            break
        except requests.ConnectionError as e:
            print('')
            print(
                    '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('There was a network failure: ' + str(e))
            print(
                    '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('')
            loop += 1
            error = 'Connection Error'
        except requests.exceptions.Timeout as e:
            print('')
            print(
                    '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('There was a timeout failure: ' + str(e))
            print(
                    '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('')
            loop += 1
            error = 'Timed Out'
        time.sleep(poll)

    if loop >= limit:  # Create dummy response
        class r:
            ok = False
            status_code = 9999
            reason = error

    return r


def getDuetStatus(model):
    global lastseqsreply, infomessages, displaymessages
    status = display = msg = ''
    # Used to get the status information from Duet
    if model == 'rr_model':
        if (not 'none' in monitors) or (displaymessages):  # we need to check
            URL = ('http://' + duet + '/rr_model?key=state')
            r = urlCall(URL, 5)
            if r.ok:
                try:
                    j = json.loads(r.text)
                    status = j['result']['status']
                    display = j['result']['displayMessage']
                    #return status, display, msg
                except:
                    pass

        if infomessages:   # Do not make unnecessary calls
            try:
                URL = ('http://' + duet + '/rr_model?flags=f&key=seqs.reply')
                r = urlCall(URL, 5)
                if r.ok:
                    j = json.loads(r.text)
                    seqsreply = j['result']
                    if seqsreply == 0:
                       lastseqsreply = seqsreply
                    if seqsreply > lastseqsreply:
                        URL = ('http://' + duet + '/rr_reply')
                        r = urlCall(URL, 5)
                        if r.ok:
                            msg = r.text
                            if msg == '\n':  # No Message
                                msg = ''
                            lastseqsreply = seqsreply
            except:
                msg = 'There was an problem getting the info message'
                print(msg)

        return status, display, msg
    else:
        URL = ('http://' + duet + '/machine/status/')
        r = urlCall(URL, 5)
        if r.ok:
            try:
                j = json.loads(r.text)
                status = j['state']['status']
                display = j['state']['displayMessage']
                msg = j['messages']
                if msg == '\n':   # No Message
                    msg = ''
                return status, display, msg
            except:
                pass
    print('getDuetStatus failed to get data. Code: ' + str(r.status_code) + ' Reason: ' + str(r.reason))
    return 'disconnected', '', ''

"""
Monitor
"""
def startMonitoring():
    global connected
    apimodel, connected = connectDuet()

    if connected:  # Monitor Loop will send Message
        monitorthread = threading.Thread(target=monitorLoop, args=(apimodel,)).start()
    else:
        return False
    return True


def monitorLoop(apimodel):  # Run as a thread
    global monitoring, duetStatus
    monitoring = True
    disconnected = 0
    lastDuetStatus = 'Not Monitoring'
    lastdisplayMessage = ''
    lastinfoMessage = ''

    while monitoring:  # action can be changed by httpListener or SIGINT or CTL+C

        duetStatus, displayMessage, infoMessage = getDuetStatus(apimodel)

        if duetStatus == 'disconnected':  # provide some resiliency for temporary disconnects
            disconnected += 1
            print('Printer is disconnected - Trying to reconnect')
            if disconnected > 10:  # keep trying for a while just in case it was a transient issue
                print('')
                print(
                        '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print('Printer was disconnected from Duet for too long')
                print('Monitoring has been stopped')
                print(
                        '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print('')
                monitoring = False   # Maybe this needs to be a selectable action
                SUBJECT = SUBJECTPRE + 'Duet has disconnected'
                MESSAGE = 'The printer at ' +duet + 'was disconnected from DuetMonitor for too long <br>Monitoring has been stopped<br>'
                MESSAGE = MESSAGE + 'To restart monitoring you need to send http://[your DuetMonitor ip:port]/?command=start'
                send_mail(FROM_ADDRESS,TO_ADDRESS,SUBJECT,MESSAGE)
                return

        SUBJECT = SUBJECTPRE
        MESSAGE =  ''

        duetStatusChange = False
        if (duetStatus != lastDuetStatus) and (duetStatus != ''):
            if ('all' in monitors) or (duetStatus in monitors) or (lastDuetStatus in monitors):  #triggers on entering and leaving state
                SUBJECT = SUBJECT + '  Status is ' + duetStatus
                MESSAGE = ('<br>DuetMonitor is watching the following status changes:  ' + ','.join(monitors) + '<br><br>Duet status changed from:  ' + lastDuetStatus + '  to:  ' + duetStatus)
                lastDuetStatus = duetStatus
                duetStatusChange = True

        displayMessageChange = False
        if (lastdisplayMessage != displayMessage) and (displayMessage != ''):
            if displaymessages:
                SUBJECT = SUBJECT + '  Display Message changed'
                MESSAGE = MESSAGE + '<br><br>Display Message is:  ' + displayMessage
                lastdisplayMessage = displayMessage
                displayMessageChange = True

        infoMessageChange = False
        if (lastinfoMessage != infoMessage) and (infoMessage != ''):
            if infomessages:
                SUBJECT = SUBJECT + '  info Message changed'
                MESSAGE = MESSAGE + '<br><br>Info Message is:  ' + infoMessage
                lastinfoMessage = infoMessage
                infoMessageChange = True

        if duetStatusChange or displayMessageChange or infoMessageChange :  # Send a message
            print(MESSAGE.replace('<br>','\n'))
            send_mail(FROM_ADDRESS, TO_ADDRESS, SUBJECT, MESSAGE)

        if monitoring:  # If no longer monitoring - sleep is by-passed for speedier exit response
            time.sleep(poll)  # poll every n seconds - placed here to speed startup

    SUBJECT = SUBJECTPRE + ' Monitoring has ben suspended'
    MESSAGE = 'Monitoring has been suspended as a result of a user request <br>DuetMonitor is still running'
    monitoring = False
    print(MESSAGE.replace('<br>','\n'))
    send_mail(FROM_ADDRESS, TO_ADDRESS, SUBJECT, MESSAGE)
    return  # The return ends the thread
    
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

    with open("DuetMonitor.conf", "w") as f:
        json.dump(enclist, f)
        f.close()
            

def loadcredentials():
    with open("DuetMonitor.conf", "r") as f:
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
    SUBJECT = SUBJECTPRE + ' Has been Shutdown'
    MESSAGE = '<br>This message confirms that DuetMonitor has been shut down.'
    send_mail(FROM_ADDRESS,TO_ADDRESS,SUBJECT,MESSAGE)
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
    
    global GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN, FROM_ADDRESS, TO_ADDRESS, SUBJECT, SUBJECTPRE
    global thisinstancepid, httpthread, monitoring, connected
    global lastseqsreply
    lastseqsreply= 0 #reply counter
    SUBJECTPRE = 'DuetMonitor: '

    monitoring = False
    connected = False
    
    init()  # get the command line inputs
    
    # Check to see if a config file exists
    nocredentials = True
    if path.exists('DuetMonitor.conf'): 
        try:
            creds = loadcredentials()
            GOOGLE_CLIENT_ID = creds[0]
            GOOGLE_CLIENT_SECRET = creds[1]
            GOOGLE_REFRESH_TOKEN = creds[2]
            FROM_ADDRESS = creds[3]
            if TO_ADDRESS == '': TO_ADDRESS = FROM_ADDRESS
            nocredentials = False
        except:
            print('\n***The credentials file - DuetMonitor.conf - may be missing or have incorrect data***\n')
            nocredentials = True
            

    
    if nocredentials:
        print('Setting up Credentials \n')
        GOOGLE_CLIENT_ID = input('\nEnter you google client id\n    The one you got from google console:  ')
        GOOGLE_CLIENT_SECRET = input ('\nEnter you google client secret\n    The one you got from google console:  ')
        FROM_ADDRESS = input ('\nEnter you gmail address\n    The one you use to log into google:  ')
        if TO_ADDRESS == '': TO_ADDRESS = FROM_ADDRESS
        refresh_token, access_token, expires_in = get_authorization(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)

        if not (refresh_token is None):
            GOOGLE_REFRESH_TOKEN = refresh_token
            SUBJECT = SUBJECTPRE + ' Confirmation Email'
            MESSAGE = '<b>This email confirms that the credentials for DuetMonitor are correct</b><br>Congratulations!'
            send_mail(FROM_ADDRESS,TO_ADDRESS,SUBJECT,MESSAGE)
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

    #Start the http Listener
    if (port != 0):
        try:
            sock = socket.socket()
            if sock.connect_ex((host, port)) == 0:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print('Sorry, port ' + str(port) + ' is already in use.')
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                sys.exit(2)
            httpthread = threading.Thread(target=createHttpListener, args=()).start()
            if startmonitor:
                print('\n Will start monitoring')
                startMonitoring()
            else:
                print('\nStarted but not yet monitoring')
                print('\nTo start monitoring send command=start')
                SUBJECT = SUBJECTPRE + 'Has started but is not monitoring'
                MESSAGE = '<br>This message confirms that DuetMonitor is running on port  ' + str(port)
                MESSAGE = MESSAGE + '<br>To start monitoring send command=start'
                send_mail(FROM_ADDRESS, TO_ADDRESS, SUBJECT, MESSAGE)
        except KeyboardInterrupt:
            pass  # This is handled as SIGINT
    else:
        print('No port number was provided or port is already in use')
        sys.exit(2)