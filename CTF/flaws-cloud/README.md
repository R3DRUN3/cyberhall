# AWS S3 Security Challenges

## Abstract
*Amazon Simple Storage Service* (Amazon `S3`) is a highly scalable and versatile cloud storage service offered by Amazon Web Services (`AWS`).  
It allows organizations to store and retrieve vast amounts of data, making it an integral component of modern cloud computing infrastructures.  
*Security* is of paramount importance when it comes to S3, as it stores critical data for businesses and individuals alike.  
S3 security measures are crucial to protect sensitive information from unauthorized access, data breaches, and accidental exposure.  
AWS offers a range of security features, such as access control lists, bucket policies, and encryption, to ensure that data stored  
in S3 remains confidential, integrity is maintained, and accessibility is well-controlled.  
Establishing robust S3 security practices is essential for safeguarding valuable digital assets in the cloud.  

<br/>

In this repository, we will explore a series of challenges related to S3 by leveraging [flaws.cloud](http://flaws.cloud).  

## Prerequisites
- [aws cli](https://aws.amazon.com/cli/)
- [aws account](https://aws.amazon.com/free/?trk=94cafeff-9d62-4c32-8799-45290b4f160b&sc_channel=ps&ef_id=EAIaIQobChMIrtnukMWxggMVVIVoCR1cRgT0EAAYASAAEgJfl_D_BwE:G:s&s_kwcid=AL!4422!3!566381912849!p!!g!!account%20aws!15451025651!135687769812&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all) (you can leverage a free trial account)  


## Challenges  
> **Note**
> To add depth and realism to the scenario, we will structure our challenge by assuming that flaws.cloud is a web service  
> for which a client has requested a black box Vulnerability Assessment & Penetration Testing (VAPT).  
> In this approach, we will have no prior information beyond the target domain, making the engagement more challenging and realistic.

<details>
<summary>Challenge 1</summary>

L'ets begin.  
As we are aware, the only information available to us is that the service is exposed at the URL http://flaws.cloud.  
The initial step we can take is to perform a DNS lookup to gather additional information:  
```console
nslookup flaws.cloud

Server:		192.168.1.1
Address:	192.168.1.1#53

Non-authoritative answer:
Name:	flaws.cloud
Address: 52.218.251.58
Name:	flaws.cloud
Address: 52.92.164.35
Name:	flaws.cloud
Address: 52.218.183.19
Name:	flaws.cloud
Address: 52.92.229.67
Name:	flaws.cloud
Address: 52.218.179.83
Name:	flaws.cloud
Address: 52.92.148.203
Name:	flaws.cloud
Address: 52.92.250.3
Name:	flaws.cloud
Address: 52.92.177.187
```  
The reason why the `nslookup` command returns multiple IP addresses for a domain is because many websites  
and services are hosted on multiple servers for redundancy and load balancing.  
This means that the same domain name (in this case, "flaws.cloud") can resolve to multiple IP addresses.  

The purpose of this approach is to ensure high availability and better distribution of traffic.  
Let's take a random IP address from the list and try to execute a DNS lookup on that:  
```console
nslookup 52.92.148.203

Server:		192.168.1.1
Address:	192.168.1.1#53

Non-authoritative answer:
203.148.92.52.in-addr.arpa	name = s3-website-us-west-2.amazonaws.com.
```  

This is an interesting information.  
`name = s3-website-us-west-2.amazonaws.com`: This line provides the result of the reverse DNS lookup.  
It reveals that the IP address `52.92.148.203` is associated with the domain name `s3-website-us-west-2.amazonaws.com`.  
This means that if you were to access the URL associated with this IP address, it would likely lead you to an Amazon Web Services (AWS) `S3`  
website hosted in the US West (Oregon) region.  
The same DNS lookup result applies to every other IP addresses taken from the above output.  


> **Note**
> All S3 buckets, when configured for web hosting, are given an AWS domain you can use to browse to it without setting up your own DNS.  
> In this case, flaws.cloud can also be visited by going to http://flaws.cloud.s3-website-us-west-2.amazonaws.com/  

Let's do a recap of what we know so far:  
We know that we have a bucket named `flaws.cloud` in `us-west-2`  
<br/>

Given that, we can attempt to browse the bucket by using the aws cli by running:  
```console
aws s3 ls s3://flaws.cloud

2017-03-14 04:00:38       2575 hint1.html
2017-03-03 05:05:17       1707 hint2.html
2017-03-03 05:05:11       1101 hint3.html
2020-05-22 20:16:45       3162 index.html
2018-07-10 18:47:16      15979 logo.png
2017-02-27 02:59:28         46 robots.txt
2017-02-27 02:59:30       1051 secret-dd02c7c.html
```  
Very good, we are able to list this bucket contents!  
Feel free to take a look at all the files in the bucket...  
the most interesting one seems to be `secret-dd02c7c.html`, let's inspect this:  
```console
aws s3 cp s3://flaws.cloud/secret-dd02c7c.html -

<html>
    <head>
        <title>flAWS</title>
        <META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">
        <style>
            body { font-family: Andale Mono, monospace; }
            :not(center) > pre { background-color: #202020; padding: 4px; border-radius: 5px; border-color:#00d000;
            border-width: 1px; border-style: solid;}
        </style>
    </head>
<body
  text="#00d000"
  bgcolor="#000000"
  style="max-width:800px; margin-left:auto ;margin-right:auto"
  vlink="#00ff00" link="#00ff00">

<center>
<pre >
 _____  _       ____  __    __  _____
|     || |     /    ||  |__|  |/ ___/
|   __|| |    |  o  ||  |  |  (   \_
|  |_  | |___ |     ||  |  |  |\__  |
|   _] |     ||  _  ||  `  '  |/  \ |
|  |   |     ||  |  | \      / \    |
|__|   |_____||__|__|  \_/\_/   \___|
</pre>

<h1>Congrats! You found the secret file!</h1>
</center>


Level 2 is at <a href="http://level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud">http://level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud</a>%
```  

The content of the file displays the link to the next challenge. Well done!  

*Security Mitigations*:  
On AWS you can set up S3 buckets with all sorts of permissions and functionality including using them to host static files.  
A number of people accidentally open them up with permissions that are too loose.  
By default, S3 buckets are private and secure when they are created.  
To allow it to be accessed as a web page, you have to turn on `Static Website Hosting` and changed the aws  
bucket policy to allow everyone `s3:GetObject` privileges, which is fine if you plan to publicly host the bucket as a web page.  
But then you can introduce the flaw if you change the permissions to add `Everyone` to have `List` permissions.

> **Warning**
> "Everyone" means everyone on the Internet!




</details>

<br/>

<details>
<summary>Challenge 2</summary>


</details>

<br/>

<details>
<summary>Challenge 3</summary>


</details>

<br/>

<details>
<summary>Challenge 4</summary>


</details>

<br/>


