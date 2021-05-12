
### This document guides you through the steps required to get the necessary google credentials.


###### You need to have already established a google account before proceeding

Note: The following steps assume a new Google Console user.  Some steps may not be neccessry if you already have settings in use.

Open Google Cloud Console and log in using your google account.
    https://console.cloud.google.com/

**Create a Project and enable Gmail APIs**

1. Click on the Projects dropdown and in the popup select New Project
   <p align="center">   
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Project1.PNG">
   </p>   
1. Enter a Project Name e.g. sendwithgmail and click Create
   <p align="center">  
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Project2.PNG">
   </p>
1. Click Go to APIs overview
   <p align="center">  
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Project3.PNG">
   </p>
1. Click on Enable APIs and Services
   <p align="center">  
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Project4.PNG">
   </p>
1. Scroll down and select Gmail APIs
   <p align="center">  
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Project5.PNG">
   </p>
1. Select Enable
   <p align="center">  
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Project6.PNG">
   </p>
1. On the Project Dropdown - select the project you just created.
   <p align="center">  
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Project7.PNG">
   </p>
   
**Enable OAuth Consent**    
1.  On the left hand menu select Oauth Consent Screen.
    <p align="center"> 
    <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/OAuth1.PNG">
    </p>
2. Click on External and then Create
   <p align="center"> 
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/OAuth2.PNG">
   </p>
3. Enter the mandatory information on the first consent screen.<br>
   App Name e.g. sendwithgmail<br>
   User Support Email (your gmail address)<br>
   and further down the screen - Developer Contact Information (your gmail address)<br>
   Click Save and Continue
   <p align="center"> 
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/OAuth3.PNG">
   </p>
   <p align="center"> 
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/OAuth4.PNG">
   </p>
4. On the Scopes and Test User Screens click Save and Continue.<br>
   
5.  On the Next screen Click on Publish App<br>
   <p align="center"> 
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/OAuth5.PNG">
   </p>
6. On the popup Click on Confirm<br>
   <p align="center"> 
   <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/OAuth6.PNG">
   </p>

7. On the Summary Screen click Back to Dashboard<br>

**Get Credentials**
   
1.  On the left hand menu select  Credentials.
    <p align="center"> 
    <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Creds1.PNG">
    </p>
1.  Click on Create Credentials and in the dropdown select OAuth Client ID
    <p align="center"> 
    <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Creds2.PNG">
    </p>
1.  Click on Application Type and in the dropdown select Desktop App
    <p align="center"> 
    <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Creds3.PNG">
    </p>
1.  Click on Name and enter a name for these credentials e.g. sendwithgmail. Click on Create.
    <p align="center"> 
    <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Creds4.PNG">
    </p>
1.  A popup will appear.  Copy the ClientID and the Client Secret using the icons provided.<br>
    **It is HIGHLY recommended that you paste these in a text editor until Setup is complete.**<br>
    When Done - click OK.
    <p align="center"> 
    <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Creds5.PNG">
    </p>
1.  You should now have a screen that looks like this:
    <p align="center"> 
    <img src="https://github.com/stuartofmt/Send-With-Gmail/blob/main/images/Creds6.PNG">
    </p>


###### Congratulations - you now have the credentials necessary to setup your application


