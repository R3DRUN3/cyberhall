# Letter Dispair

## Abstract
*Category* : **web challenge**<br/>
*Challenge name* : **Letter Dispair**<br/>
*Host* : `206.189.24.232:32529`<br/>
*Description* : A high-profile political individual was a victim of a spear-phishing attack.<br/>
*Status* : *UNSOLVED*<br/>
<br/> 
The email came from a legitimate government entity in a nation we don't have jurisdiction. 
<br/>
However, we have traced the originating mail to a government webserver. 
<br/>
Further enumeration revealed an open directory index containing a PHP mailer script we think was used to send the email.
<br/> 
We need access to the server to read the logs and find out the actual perpetrator. Can you help?

## Walktrough
Let's check the home page:
<br/>
<div style="width: 65%; height: 65%">

  ![](images/homepage.png)
  
</div>  

If we click on `mailer.zip` this file is downloaded on our local machine.<br/>
if we extract it, we see a `mailer.php` file that, most likely, is the source of the `mailer` part of the website <br/>
that we can access by clicking on the `mailer.php` link in the homepage of the website,



# To be completed, not yet resolved


