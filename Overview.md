DuetMonitor

This program allows monitoring of Duet status codes and display messages.
It runs in the background and periodically polls Duet looking for changes to the specifid status calues and / or display messages.
When it detects a change - it sends an email to an email recipient.

The main capabilities include:
1.  Sends emails using your google mail account From: with your google email address.
2.  Can send to any legitimate email recipient.
3.  Is controllable via a browser (or other http) interface (e.g. curl)
4   Is dynamically configurable for the status values that it monitors.

DuetMonitor is intended to run constantly (if you wish) in the background.  From http interface (browser) you can perform the following:
1.  Start / Stop monitoring
2.  Change the To: and Subject:
3.  Change the status values being monitored
4.  Send an email independently of monitoring

The ability to send an email, independently of the monitoring function, with a http request makes it useful in conjunction with other programs such as DueUI and ????

I chose google mail as the delivery mechanism because:
1.  It is widely used and reliable.
2.  Is secure and avoids many possible miss-use situations.
3.  You can easily get an account if you do not already have one.
4.  You can easily revoke permission to send emails if you need to.
5.  It is free - unless you want to send 1000's of emails per day :-) 

A full set of instructions for creating credentials and initial setup is here:
????????