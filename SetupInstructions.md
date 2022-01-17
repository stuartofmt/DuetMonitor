### This document guides you through the initial (or a new) setup of DuetMonitor


From the directory where you installed DuetMonitor.py start it using the following commands.

```
rm ./DuetMonitor.conf
python3 ./DuetMonitor.py
```
The program will ask you to enter the credentials you created by following the instructions here:<br>
https://github.com/stuartofmt/DuetMonitor/blob/master/GettingCredentials.md

As part of this process you will need to use a browser.  It does NOT have to be on the same machine that you have installed DuetMonitor.<br>
To avoid typo's it is best to cut and paste the credentials (using right mouse click for paste to avoid an accidental control characters)

**In a terminal**

1.  The Google Client ID 
```
Setting up Credentials

Enter you google client id
    The one you got from google console:
```
2.  The Google Client Secret
```
Enter you google client secret
    The one you got from google console:
```    

3.  Your gmail address
```
Enter you gmail address
    The one you use to log into google:
```    

4. You will now be asked to navigate to an url in a browser in order to get a verification code.  Copy the link and paste it in a browser (highlighting the link performs a copy in many terminals.  Don't Ctl+C) 
Note the link below is not a real link
```
 Navigate to the following URL to auth:
 https://accounts.google.com/o/oauth2/auth?client_id=112345678907-321abcdef0b6bs0a9x2efgh8bh4ab3cp.apps.googleusercontent.com&redirect_uri=urn%3Aabcd%5Xyz%3Aoauth%3A2.0%3Aabc&response_type=code&scope=https%3A%2F%2Fmail.google.com%2F

 Enter verification code:
```

**In the Browser**

1.  Sign in using the same gmail account as step 3 above( i.e. the one you used to create the credentials)
   <p align="center">  
   <img src="https://github.com/stuartofmt/DuetMonitor/blob/master/images/Setup1.PNG">
   </p>
2.  You may be presented with a screen like this. It will look different depending on your browser (this is Chrome)<br>
    Ignore the warnings and select the necessary options to proceed **even if it says it is unsafe to do so**.  The link you are using is unique to the credentials you are setting up - so it is both safe and necessary to proceed.
   <p align="center">  
   <img src="https://github.com/stuartofmt/DuetMonitor/blob/master/images/Setup2.PNG">
   </p>
3.  Select Allow from the popup
   <p align="center">  
   <img src="https://github.com/stuartofmt/DuetMonitor/blob/master/images/Setup3.PNG">
   </p>
1.  Select Allow from the Confirmation screen
   <p align="center">  
   <img src="https://github.com/stuartofmt/DuetMonitor/blob/master/images/Setup4.PNG">
   </p>
1. On the Sign IN screen - click on the icon to copy the verification code
   <p align="center">  
   <img src="https://github.com/stuartofmt/DuetMonitor/blob/master/images/Setup5.PNG">
   </p>

**In a terminal**

1.  Paste the verification code.
```
 Navigate to the following URL to auth:
 https://accounts.google.com/o/oauth2/auth?client_id=112345678907-321abcdef0b6bs0a9x2efgh8bh4ab3cp.apps.googleusercontent.com&redirect_uri=urn%3Aabcd%5Xyz%3Aoauth%3A2.0%3Aabc&response_type=code&scope=https%3A%2F%2Fmail.google.com%2F

 Enter verification code:
```
2.  DuetMonitor will now attempt to send an email, to you (from you).  It will look like this:
   <p align="center">  
   <img src="https://github.com/stuartofmt/DuetMonitor/blob/master/images/Setup5.PNG">
   </p>
3.  When you have received the email answer **y** to this prompt.

```
A confirmation email has been sent to you. Did you get it (y/n):
```
4.  You will now get an on screen confirmation
```
Success! Your credentials are all set.
```

###### You can now go start DuetMonitor in the normal manner
