# DuetMonitor

This program allows monitoring of Duet status codes and display messages.<br>

It runs in the background and periodically polls Duet looking for changes to the specified status values.  It can also monitor changes in display messages.<br>

When it detects a change - it sends an email.  Changes are detected when entering AND leaving a status.  In this way - you can monitor a single status and detect changes to that status.  You can, of course, monitor multiple status.

<br>DuetMonitor is designed to run continuously and can accept http commands to change settings.  Typically, you would use a browser but curl or other means of sending http can be used.<br>

emails are sent from your gmail account to any recipient with a legal email address.  It is intended for short messages.

###Version 1.0.0

[1]  Initial version

###Version 1.0.1

[1]  Added monitoring of error messages

[2]  Added additional Controls

[3]  Provided additional information in browser UI


## General Description

The main capabilities include:
1.  Send emails using your gmail address.
2.  Can send to any legitimate email recipient.
3.  Is controllable via a browser (or other http) interface (e.g. curl)
4.  Is dynamically configurable for the values that it monitors.
5.  Reports if disconnected (for more than 2 polling intervals) from Duet and stops monitoring.    

Because it can also monitor display messages - you can embed M117 Messages in your gcode and macros (e.g. at the start and end of printing, at key points in a calibration macro) and receive an email in a customizable manner.

DuetMonitor is intended to run constantly (if you wish) in the background.
<br>From a http interface (e.g. browser) you can perform the following:
1.  Start / Stop monitoring
2.  Change the To: and Subject:
3.  Change which values (status, display messages, error messages) are being monitored
4.  Send an email independently of monitoring

The ability to just send an email (does not need to be monitoring) makes it useful in conjunction with other programs such as DueUI and BtnCmd and ....<br><br>

## Requirements 

* Python3 (must be accessible without specifying the path)
* Linux OS,  Windows 10, Windows Subsystem Linux (WSL) tested
* You MUST have a gmail email account
* You MUST have gathered additional credentials by following the instructions here:<br>
https://github.com/stuartofmt/DuetMonitor/blob/master/GettingCredentials.md
<br>**It is recommended that you do this before proceeding further.  There are several steps. It is important to follow them closely.  Screenshots have been provided but may change if google changes its process.**
  

## Installation

For Linux:<br>

cd to a directory of your choice.  It is usually simpler if this directory is only used for DuetMonitor.

```
wget https://github.com/stuartofmt/DuetMonitor/raw/master/DuetMonitor.py

chmod 744 DuetMonitor.py
```


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
Other options for startup are described in the ##Startup Options## section below.

DuetMonitor can be started from the command line or, more usually using systemctl (not available on Win10 or WSL) or equivalent
.<br>
It is usually run in the background.<br>
A sample service file for use with systemctl is included  here:<br>
https://github.com/stuartofmt/DuetMonitor/blob/master/DuetMonitor.service
<br>Instructions for using are here:<br>
https://github.com/stuartofmt/DuetMonitor/blob/master/system-unit-file.md


**Note that the program will send an email when it starts.**

Example command line for running DuetMonitor in the background (linux)
```
python3 ./DuetMonitor.py -port 8090 &
```
or if you plan to close the command console - use nohup

```
nohup python3 ./DuetMonitor.py -port 8090 &
```

On Windows things are slightly different - note the use of pythonw
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

DuetMonitor is used by sending html - therefore it can be controlled using a browser.  The normal use is intended to allow programs to send simple email messaged by invoking html.
The general form is as follows:
```
http://<ipaddress>:<port>/[?{instruction}][&{instruction}]
```
**Note** simply sending http://<ipaddress>:<port> with no instructions will display the current settings.


---

Command instructions can be used to start and stop monitoring and terminate DuetMonitor.
If used with other instructions - the other instructions are ignored.

Command options are:
command=start
command=stop
command=terminate  - causes DuetMonitor to terminate<br>
Examples:
```
http://localhost:8090/?command=start         # Starts monitoring from DuetMonitor on port 8090
http://localhost:8090/?command=stop          # Stops monitoring from DuetMonitor on port 8090
http://localhost:8090/?command=terminate     # Terminates DuetMonitor on port 8090
```
---
**Note that the program will send an email message when these commands are used.**


The main instructions are:
- monitors={a list of valid Duet status}<br>
The list is comma separated, no quotes.<br>
Valid status values are:  all, none, halted,idle,busy,processing,paused,pausing,resuming,cancelled
Note: You can also use 'all' to include all status values or 'none' to stop monitoring of status values.<br>
  
Examples:
```
http://localhost:8090/?monitors=all                # Send email on all status changes
http://localhost:8090/?monitors= idle,processing   # Send email when printing starts / stops
http://localhost:8090/?monitors=pause              # Only send email if the printer pauses.
```
---
- displaymessages={instructions}<br>
Examples:
```
http://localhost:8090/?displaymessages=True   # Send email on display message changes
http://localhost:8090/?displaymessages=False  # Ignore display message changes
```
If displaymessages  is True - you can (for example) send an email using M117.

---

- errormessages={instructions}<br>
Examples:
```
http://localhost:8090/?errormessages=True   # Send email on error message changes
http://localhost:8090/?errormessages=False  # Ignore error message changes
```


---


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


### Startup Options

Options can be viewed with
```
python3 DuetMonitor.py -h
```
The response will give the version number at the top.

The options are described here.  Each option is preceded by a dash -. Some options have parameters described in the square brackets.   The square brackets are NOT used in entering the options. If an option is not specified, the default used.


#### -host [ip address]
If omitted the default is 0.0.0.0<br>
Generally this can be left out (default) as it will allow connection to the http listener from localhost:<port> (locally) or from another machine with network access using <actual-ip-address-of-server-running-DuetLapse3><port>.

Example
```
-host 192.168.86.10      #Causes internal http listener (if active) to listen at ip address 192.168.86.10<br>
```

#### -port [port number]
**Mandatory - This is a required option.** <br>
If the selected port is already in use the program will not start

Example
```
-port 8090      #Causes internal http listener to start and listen on port 8090<br>
```

#### -duet [ip address]
**Mandatory - This is a required option.**<br>
The parameter is the network location of your duet printer. It can be given as a hostname, or an explicit ip address.
As a simple test - a browser should be able to access the Duet Web Controller using http://[ip address] from the same computer that is running DuetMonitor.py.

  
Example
```
-duet 192.168.1.10     #Connect to the printer at 192.168.86.10

-duet localhost        #Connect to the printer at localhost
```

#### -poll [number]
If omitted - the default is 60 seconds
Sets the interval between polling Duet.

Example
```
-poll  120   #polls for status every 2 minutes
```

#### -To [valid email address]
If omitted - the default is your gmail email address (used during setup). 

Example
```
-To myotheremail@notmygoogle.com
```

#### -Subject [String]
If omitted - the default is 'DuetMonitor:'
This sets the Subject prefix for messages.

Example
```
-Subject A message from my Duet
```

#### -monitors [(list if strings)]
If omitted - the default is: all

Example
```
-monitors idle busy processing  # will monitor only these status
                                # Not that these values are not quoted
                                
- monitors none                 # Status will not be monitored                                
```

#### -dontstart
If omitted - the default is False

Example
```
-dontstart    # does NOT start monitoring when DuetMonitor.py is started
              # if omitted will start monitoring when program starts
```

#### -nodisplaymessages
If omitted - the default is False

Example
```
-nodisplay  # Does not monitor display Messages
```

#### -noerrormessages
If omitted - the default is False

Example
```
-noerrormessages  # Does not monitor error Messages
```