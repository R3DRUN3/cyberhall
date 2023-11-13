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
> for which a customer has requested a black box **Vulnerability Assessment & Penetration Testing (VAPT)**.  
> In this approach, we will have no prior information beyond the target domain, making the engagement more challenging and realistic.  

<br/>

> **Note**
> All challenges are dependent on one another so proceed in order.  

<details>
<summary>CHALLENGE 1</summary>

L'ets begin.  
As we are aware, the only information available to us is that the service is exposed at the URL http://flaws.cloud:  

<img src="images/flaws-website.png" alt="flaws.cloud" width="3000" height="290">  


The initial step we can take is to perform a DNS lookup (*forward lookup*) on the domain in order to gather additional information:  
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
Let's take a random IP address from the list and try to execute a DNS lookup (*reverse lookup*) on that:  
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
> In this case, flaws.cloud can also be visited by going to http://flaws.cloud.s3-website-us-west-2.amazonaws.com.  
> That is the reason why S3 bucket names must be unique world-wide and they must follow DNS naming conventions.  

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
```html
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

**Security Mitigations**:  
We need to explain to our customer that on AWS you can set up S3 buckets with all sorts of permissions and functionality including using them to host static files.  
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
<summary>CHALLENGE 2</summary>

Now we can procede with the second challenge.  

> **Note**
> This challenge is similar to the first one but you will need an aws accout.  


We know that the link to the new bucket is http://level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud.  
Once you have your aws cli configured with keys from your aws account, let's try to list all the files in the bucket:  
```console
aws s3 ls s3://level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud

2017-02-27 03:02:15      80751 everyone.png
2017-03-03 04:47:17       1433 hint1.html
2017-02-27 03:04:39       1035 hint2.html
2017-02-27 03:02:14       2786 index.html
2017-02-27 03:02:14         26 robots.txt
2017-02-27 03:02:15       1051 secret-e4443fc.html
```  

Once again we notice that there is a *secret* html file, let's cat is content:  

aws s3 cp s3://level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud/secret-e4443fc.html -  
```html
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


Level 3 is at <a href="http://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud">http://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud</a>%
```   

The content of the file displays the link to the next challenge. Well done!  

**Security Mitigations**:  
We need to explain to our customer that similar to opening permissions to `Everyone` in the previous bucket/challenge, people accidentally open permissions to `Any Authenticated AWS User`.  

> **Warning**
> They might mistakenly think this will only be users of their account, when in fact it means anyone that has an AWS account!



</details>

<br/>

<details>
<summary>CHALLENGE 3</summary>

Now we can procede with the third challenge.  
We know that the link to the new bucket is http://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud.  
Once you have your aws cli configured with keys from your aws account, let's try to list all the files in the bucket:  
```console
aws s3 ls s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud  

                           PRE .git/
2017-02-27 01:14:33     123637 authenticated_users.png
2017-02-27 01:14:34       1552 hint1.html
2017-02-27 01:14:34       1426 hint2.html
2017-02-27 01:14:35       1247 hint3.html
2017-02-27 01:14:33       1035 hint4.html
2020-05-22 20:21:10       1861 index.html
2017-02-27 01:14:33         26 robots.txt
```  
This time we notice something different: there is a `.git` folder!  
A `.git` folder within a directory typically indicates that the directory is a Git repository.  
`Git` is a distributed version control system commonly used for tracking changes in source code and managing collaborative software development projects.  
The `.git` folder contains all the information and data necessary for Git to manage version control for the files and directories within that repository.  
It includes information about commits, branches, history, configuration settings, and more.  
There are probably interesting things in this folder...let's download the full bucket content with the following command:  
```console
aws s3 sync s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/ . --region us-west-2

download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/HEAD to .git/HEAD
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/description to .git/description
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/config to .git/config
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/COMMIT_EDITMSG to .git/COMMIT_EDITMSG
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/hooks/applypatch-msg.sample to .git/hooks/applypatch-msg.sample
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/hooks/pre-applypatch.sample to .git/hooks/pre-applypatch.sample
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/hooks/post-update.sample to .git/hooks/post-update.sample
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/hooks/commit-msg.sample to .git/hooks/commit-msg.sample
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/hooks/pre-commit.sample to .git/hooks/pre-commit.sample
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/hooks/pre-rebase.sample to .git/hooks/pre-rebase.sample
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/hooks/prepare-commit-msg.sample to .git/hooks/prepare-commit-msg.sample
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/hooks/update.sample to .git/hooks/update.sample
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/2f/c08f72c2135bb3af7af5803abb77b3e240b6df to .git/objects/2f/c08f72c2135bb3af7af5803abb77b3e240b6df
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/index to .git/index
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/info/exclude to .git/info/exclude
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/0e/aa50ae75709eb4d25f07195dc74c7f3dca3e25 to .git/objects/0e/aa50ae75709eb4d25f07195dc74c7f3dca3e25
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/61/a5ff2913c522d4cf4397f2500201ce5a8e097b to .git/objects/61/a5ff2913c522d4cf4397f2500201ce5a8e097b
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/b6/4c8dcfa8a39af06521cf4cb7cdce5f0ca9e526 to .git/objects/b6/4c8dcfa8a39af06521cf4cb7cdce5f0ca9e526
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/logs/HEAD to .git/logs/HEAD
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/logs/refs/heads/master to .git/logs/refs/heads/master
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/53/23d77d2d914c89b220be9291439e3da9dada3c to .git/objects/53/23d77d2d914c89b220be9291439e3da9dada3c
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/db/932236a95ebf8c8a7226432cf1880e4b4017f2 to .git/objects/db/932236a95ebf8c8a7226432cf1880e4b4017f2
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/92/d5a82ef553aae51d7a2f86ea0a5b1617fafa0c to .git/objects/92/d5a82ef553aae51d7a2f86ea0a5b1617fafa0c
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/f5/2ec03b227ea6094b04e43f475fb0126edb5a61 to .git/objects/f5/2ec03b227ea6094b04e43f475fb0126edb5a61
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/hint2.html to ./hint2.html
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/hint1.html to ./hint1.html
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/hint3.html to ./hint3.html
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/c2/aab7e03933a858d1765090928dca4013fe2526 to .git/objects/c2/aab7e03933a858d1765090928dca4013fe2526
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/index.html to ./index.html
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/robots.txt to ./robots.txt
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/76/e4934c9de40e36f09b4e5538236551529f723c to .git/objects/76/e4934c9de40e36f09b4e5538236551529f723c
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/hint4.html to ./hint4.html
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/refs/heads/master to .git/refs/heads/master
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/e3/ae6dd991f0352cc307f82389d354c65f1874a2 to .git/objects/e3/ae6dd991f0352cc307f82389d354c65f1874a2
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git/objects/f2/a144957997f15729d4491f251c3615d508b16a to .git/objects/f2/a144957997f15729d4491f251c3615d508b16a
download: s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/authenticated_users.png to ./authenticated_users.png
```  
Now we are inside the git folder and we can inspect git logs:  
```console
git log

commit b64c8dcfa8a39af06521cf4cb7cdce5f0ca9e526 (HEAD -> master)
Author: 0xdabbad00 <scott@summitroute.com>
Date:   Sun Sep 17 09:10:43 2017 -0600

    Oops, accidentally added something I shouldn't have

commit f52ec03b227ea6094b04e43f475fb0126edb5a61
Author: 0xdabbad00 <scott@summitroute.com>
Date:   Sun Sep 17 09:10:07 2017 -0600

    first commit
```  
The log shows 2 commit and one have a suspicious message associated with it: `Oops, accidentally added something I shouldn't have`.  
Let's checkout the commit before that and take a look around at that point in the git history:  
```console
git checkout f52ec03b227ea6094b04e43f475fb0126edb5a61 && ls

M	index.html
Note: switching to 'f52ec03b227ea6094b04e43f475fb0126edb5a61'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

Or undo this operation with:

  git switch -

Turn off this advice by setting config variable advice.detachedHead to false

HEAD is now at f52ec03 first commit

access_keys.txt         authenticated_users.png hint1.html              hint2.html              hint3.html              hint4.html              index.html              robots.txt
```  

Interesting...there is an `access_keys.txt` file in the repository!  
Let's inspect that:  
```console
cat access_keys.txt

access_key AKIAJ366LIPB4IJKT7SA
secret_access_key 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
```  
It's a good day to be a pentester, we found a set of aws [keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)!  

let's use them to see if we can do something!  
```console
export AWS_ACCESS_KEY_ID=AKIAJ366LIPB4IJKT7SA
export AWS_SECRET_ACCESS_KEY=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
aws sts get-caller-identity

{
    "UserId": "AIDAJQ3H5DC3LEG2BKSLC",
    "Account": "975426262029",
    "Arn": "arn:aws:iam::975426262029:user/backup"
}

```  

The output of the above command shows that we are now impersonating the `arn:aws:iam::975426262029:user/backup` [IAM](https://aws.amazon.com/iam/?trk=e7f9b09d-7bd6-4855-9dba-72c6bc2af630&sc_channel=ps&ef_id=EAIaIQobChMI6M_L-dKxggMVblBBAh1FEw9aEAAYASAAEgL2Z_D_BwE:G:s&s_kwcid=AL!4422!3!651510173475!e!!g!!amazon%20iam!19828210056!146491523705) identity.  
This is a user from the customer's aws account!  
Let's check the user attached policies:  
```console

aws iam list-attached-user-policies --user-name backup

An error occurred (AccessDenied) when calling the ListAttachedUserPolicies operation: User: arn:aws:iam::975426262029:user/backup is not authorized to perform: iam:ListAttachedUserPolicies on resource: user backup because no identity-based policy allows the iam:ListAttachedUserPolicies action
```  
We are not lucky this time but maybe with can list more bucket with the current identity:  
```console
aws s3 ls

2020-06-25 19:43:56 2f4e53154c0a7fd086a04a12a452c2a4caed8da0.flaws.cloud
2020-06-27 01:06:07 config-bucket-975426262029
2020-06-27 12:46:15 flaws-logs
2020-06-27 12:46:15 flaws.cloud
2020-06-27 17:27:14 level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud
2020-06-27 17:27:14 level3-9afd3927f195e10225021a578e6f78df.flaws.cloud
2020-06-27 17:27:14 level4-1156739cfb264ced6de514971a4bef68.flaws.cloud
2020-06-27 17:27:15 level5-d2891f604d2061b6977c2481b0c8333e.flaws.cloud
2020-06-27 17:27:15 level6-cc4c404a8a8b876167f5e70a7d8c9880.flaws.cloud
2020-06-28 04:29:47 theend-797237e8ada164bf9f12cebf93b282cf.flaws.cloud
```  
Yes! We can list buckets that we couldn't before!  
Now we know where `level4` is located.  

**Security Mitigations**:  
We need to explain to our customer that People often leak AWS keys and then try to cover up their mistakes without revoking the keys.  
You should always revoke any AWS keys (or any secrets) that could have been leaked or were misplaced.  
Roll your secrets early and often and [use roles instead of keys whenever possible](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html).  

> **Warning**
> If sensitive information or secrets are accidentally leaked and committed to a Git repository, simply removing them in a new commit is not sufficient.  
> These secrets can still exist in the repository's history, and they may be accessible to anyone with access to that repository.  
> If you accidentally committed a secret, consider rewriting your Git history to remove any traces of it.  
> Tools like git-filter-branch and git-rebase can help, but use them with caution as they can be complex and have implications on collaboration.  



</details>

<br/>

<details>
<summary>CHALLENGE 4</summary>

Now we can procede with challenge 4.  
We know that the link to the new bucket is http://level4-1156739cfb264ced6de514971a4bef68.flaws.cloud.  

> **Note**
> For the next level, you need to get access to the web page running on an EC2 at 4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud  
> It'll be useful to know that a snapshot was made of that EC2 shortly after nginx was setup on it.  
> Also you need the aws keys retrieved in the previous challenge.  

If we open a browser to `4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud` we are presented with a login page:  
<img src="images/challenge4-login-page.png" alt="flaws.cloud" width="3000" height="290">  

We need to retrieve the right credentials in order to sign-in.  
The challenge tip informs us that we are dealing with a backup of an [EC2](https://aws.amazon.com/ec2/) instance, and if we recall from the previous challenge, the username was indeed `backup`.  
Let's see if we can list the backups/snapshots of the EC2 instance using the AWS CLI:  
```console
 aws  ec2 describe-snapshots --owner-ids 975426262029

{
    "Snapshots": []
}
```  

Mmmm it seems that, as of 07/11/2023, there are no snapshots.  
Maybe we can describe instances?  
```console
aws ec2 describe-instances

{
    "Reservations": []
}
```  
No luck either 😞  
Maybe the maker of flaws.cloud deleted them...no much else we can do here.  
Our customer can sleep peaceful dreams... for now.  




</details>

<br/>


