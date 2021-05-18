DuetMonitor

This program allows monitoring of Duet status codes and display messages.
It runs in the background and periodically polls Duet looking for changes to the specified status values.  It can also monitor changes in display messages.
When it detects a change - it sends an email.  Changes are detected when entering AND leaving a status.  In this way - you can monitor a single status and detect changes to that status.  You can, of course, monitor multiple status.

The main capabilities include:
1.  Sends emails using your google mail address.
2.  Can send to any legitimate email recipient.
3.  Is controllable via a browser (or other http) interface (e.g. curl)
4.  Is dynamically configurable for the status values that it monitors.
5.  Reports if disconnected (> 2 sec) from Duet and stops monitoring.    


Because it can also monitor display messages - you can embed M117 Messages in your gcode and macros (e.g. at the start and end of printing, at key points in a calibration macro) and receive an email in a customizable manner.

DuetMonitor is intended to run constantly (if you wish) in the background.  From a http interface (e.g. browser) you can perform the following:
1.  Start / Stop monitoring
2.  Change the To: and Subject:
3.  Change the status values being monitored
4.  Send an email independently of monitoring

The ability to just send an email (does not need to be monitoring) makes it useful in conjunction with other programs such as DueUI and BtnCmd and ....<br><br>


I selected gmail as the delivery mechanism because:
1.  It is widely used and reliable.
2.  Is secure and avoids many possible miss-use situations.
3.  You can easily get an account if you do not already have one (even if you only use it for DuetMonitor).
4.  You can easily revoke and re-enable permission to send emails if you need to.
5.  It is free - unless you want to send 1000's of emails per day :-) 

A full set of instructions for installing, creating credentials and initial setup is here:
https://github.com/stuartofmt/DuetMonitor