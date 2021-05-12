# DuetMonitor

A monitor of Duet Status which sends change notifications emails via gmail.
Can also be called with http (e.g. from a browser) to end an arbitrary message and to change subject and To address,




###Version 1.0.0
[1]  Initial version


## General Description

**DuetMonitor** designed to run continuously and accept http commands either from a browser, curl or other means of sending http get commands.<br>
It is used to send an email from your gmail account to a recipient and intended for short messages.<br>


## Requirements 

* Python3 (must be accessible without specifying the path)
* Linux OS,  Windows 10, Windows Subsystem Linux (WSL) tested
* You MUST have a gmail email account
* You MUST have gathered additional credentials by following the instructions here:<br>
https://github.com/stuartofmt/DuetMonitor/blob/master/GettingCredentials.md
  

## Installation

For Linux:<br>

cd to the a directory of your choice (It is usually simpler if this directory is only used for DuetMonitor

`wget https://github.com/stuartofmt/DuetMonitor/raw/main/DuetMonitor.py
chmod 744 DuetMonitor.py
`

For windows<br>
Follow the instructions from one of the web sources to install python3 - for example:<br>
https://docs.python.org/3/using/windows.html 

Take note of editing the path variable(s) so that python3 and its libraries / modules can be found during execution.

## Setup
There is an initial setup stage to input and validate credentials.  If the credentials are changed - this initial setup must be done again.
Setup results in a file DuetMonitor.conf being created.  This file contains validated credentials and is used when the program starts normally.
If the file NOT present - the setup process is used.  In this way - if credentials change - the file DuetMonitor.conf can be recreated by first deleting it and then rerunning the setup.

Follow the instructions here for setting up DuetMonitor:<br>
https://github.com/stuartofmt/DuetMonitor/blob/master/SetupInstructions.md

  
## Starting
Once setup is complete - you will normally start DuetMonitor in one of the following ways.

DuetMonitor requires a port number using the -port option  This is mandatory.<br>
Other options for startup are described in the ##Options## section below.

DuetMonitor can be started from the command line or, more usually using systemctl (not available on Win10 or WSL) or equivalent
.<br>
It is usually run in the background.<br>
Sample instructions for setting up using systemctl are here:<br>
https://github.com/stuartofmt/DuetMonitor/blob/master/SetupInstructions.md

**Note that the program will send a system email confirming startup.**

Example command line for running DuetMonitor in the background (linux)
```
python3 ./DuetMonitor.py -port 8090 &
```
or if you plan to close the command console - use nohup

```
nohup python3 ./DuetMonitor.py -port 8090 &
```

On windows things are slightly different - note the use of pythonw
which will run python in the background (tested with python 3.9)

Note the use of pythonw and the output files to check if everything was successful

```
pythonw DuetMonitor.py -port 8090 > DuetMonitor.log 2>&1

```

If the program is run in foreground it can be shutdown using CTRL+C (on linux) or CTRL+Break (on Windows).<br>
If the program is run in background it can be stopped using http with command=terminate (see the section on **Usage** below).<br>
**Note that the program will send a system email confirming that the program is terminated.**

**Note that the http listener will stop responding if DuetMonitor is run from a command console that is then closed.
This will happen even if started in background.<br>
To avoid this - use nohup (linux) or start with pythonw (on Windows)<br>
An alternative if you are on Win10 is to use  Windows Subsystem for Linux (WSL) and run DuetMonitor as a linux application inside WSL.<br>**

### Usage

DuetMonitor is used by sending html - therefore it can be tested using a browser.  The normal use is intended to allow programs to send simple email messaged by invoking html.
The general form is as follows:
```
http://<ipaddress>:<port>/?{instruction}[&{instruction}]
```
The main instructions are:

- To={a valid email address}

- Subject={The email subject}

- Message={The email message}

These are all optional. **The only time an email is sent is if the Message instruction is used**<br>
If To and / or Subject are used they change the current settings until another change is made.
This means that emails can be sent by only using the Message instruction.<br><br>
When DuetMonitor starts - it uses default setting as specified in the **Options** section.<br><br>
Example - send an email using the current settings of To and Subject:
```
http://localhost:8090/?Message=I just sent an email
```
Example - send an email changing the Subject:
```
http://localhost:8090/?Subject=A new Subject&Message=I just sent an email
```
Example - just change the To (no email is sent):
```
http://localhost:8090/?To=someone@somewhere.com
```
Example - send an email changing the To and Subject:
```
http://localhost:8090/?To=someone@somewhere.com$Subject=New&Message=An email for you
```
---
The following cn be used to remotely terminate DuetMonitor.  If used with other instructions - they are ignored (i.e. you cannot send an email and terminate in one instruction).
**Note thatthe program will send a system email confirming that the program is terminated.**

command=terminate  - causes DuetMonitor to terminate<br>
Example:
```
http://localhost:8090/?command=terminate     #Will cause the instance of DuetMonitor on port 8090 to terminate
```
---

### Options

Options can be viewed with
```
python3 DuetMonitor.py -h
```
The response will give the version number at the top.

The options are described here.  Each option is preceded by a dash -. Some options have parameters described in the square brackets (the square brackets are NOT used in entering the options. If an option is not specified the default used.


#### -host [ip address]
If omitted the default is 0.0.0.0<br>
Generally this can be left out (default) as it will allow connection to the http listener from localhost:<port> (locally) or from another machine with network access using <actual-ip-address-of-server-running-DuetLapse3><port>.

Example
```
-host 192.168.86.10      #Causes internal http listener (if active) to listen at ip address 192.168.86.10<br>
```

#### -port [port number]
This option is mandatory.<br>
If the selected port is already in use the program will not start

Example
```
-port 8082      #Causes internal http listener to start and listen on port 8082<br>
```

#### -To [valid email address]
If omitted - the default is your gmail email address (used during setup). 

Example
```
-To myotheremail@notmygoogle.com
```

#### -Subject [String]
If omitted - the default is 'Message from DuetMonitor'

Example
```
-Subject A message from my Duet
```