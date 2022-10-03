# Felonious Forums

## Abstract
*Category* : **Web Challenge**<br/>
*Challenge name* : **Felonious Forums**<br/>
*Host* : `64.227.43.207:31335`<br/>
*Description* : Our threat intelligence has traced a reseller of the GrandMonty Ransomware linked with the Monkey Business group to this illegal forums platform.<br>
We need you to investigate the platform to find any security loopholes that can provide us access to the platform.<br/>
*Status* : **SOLVED**

## Walktrough
Since this is a web challenge, let's check the website homepage:<br/>

<div style="width: 65%; height: 65%">

  ![](images/homepage.png)
  
</div>  
<br/>

Let's try to see if it is possible to bypass the login with an SQL injection:<br/>
```console
sqlmap -u http://64.227.43.207:31335/api/login --data="username=user&password=pwd" --method POST --dbs --batch
```

Unfortunately, zero luck here.<br/>
What about NoSql Injection? We can test some payload manually or resort to *nosqlmap* for greater automation and firepower.<br/>
Even in this case...no luck 😔<br/>
It seems that the only way to enter is to create a new user (good job protecting the login!)<br/>
Let's create the user `user` with the password `pass` and we are in:<br/>
<div style="width: 65%; height: 65%">

  ![](images/inside-forum.png)
  
</div>  
<br/>

If we open our browser dev tools, we notice that the website use this cookie:<br/>
```console
session: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTAsInVzZXJuYW1lIjoidXNlciIsInJlcHV0YXRpb24iOjAsImNyZWRpdHMiOjEwMCwidXNlcl9yb2xlIjoiTmV3YmllIiwiYXZhdGFyIjoibmV3YmllLndlYnAiLCJqb2luZWQiOiIyMDIyLTEwLTAzIDEyOjUzOjEzIiwiaWF0IjoxNjY0ODAxNjA0fQ.kZeLICIFJw0k3xiGgm6iCeAz10HyZd1ixyxeIxrW464
```

This is a <a href="https://jwt.io/">JWT</a> token, let's decode it:<br/>

<div style="width: 65%; height: 65%">

  ![](images/jwt.png)
  
</div>  
<br/>
Interesting but nothing special here.<br/>


The forum lets us create a new thread and post to it with mardkdown formatting:<br/>
<div style="width: 65%; height: 65%">

  ![](images/post.png)
  
</div>  
<br/>

Let's check if this il vulnerable to some sort of *XSS*.<br/>
What if I enter this in the post?<br/>
```console
![Let's See](https://www.google.com/image.png"onerror="alert('💀VULNERABLE💀'))
```
<div style="width: 65%; height: 65%">

  ![](images/xss.png)
  
</div>  
<br/>

Yes! We have found a *XSS vulnerability*!!!
This XSS seems to be possible only in the *Post Preview* feature though.<br/>

At this point we can inspect the code attached to the challenge.<br/>

In the code there are many references to a `flag.txt` file.
These lines of `bot.js`, in particular, are interesting:<br/>
```js
try {
		const browser = await puppeteer.launch(browser_options);
		let context = await browser.createIncognitoBrowserContext();
		let page = await context.newPage();

		let token = await JWTHelper.sign({ username: 'moderator', user_role: 'moderator', flag: flag });
		await page.setCookie({
			name: "session",
			'value': token,
			domain: "127.0.0.1:1337"
		});

		await page.goto(`http://127.0.0.1:1337/report/${id}`, {
			waitUntil: 'networkidle2',
			timeout: 5000
		});
		await page.waitForTimeout(2000);
		await browser.close();
    } catch(e) {
        console.log(e);
    }
```

This suggest to us that the cookie for the `moderator` user has a flag field in it with the value of the const `flag`:<br/>
```js
const flag = fs.readFileSync('/flag.txt', 'utf8');
```
This is undoubtedly our flag!<br/>

Going through the flow of the code, we note that the `visitPost` function of `bot.js` does not perform any sanitization on the `id` argument:<br/>
```js
await page.goto(`http://127.0.0.1:1337/report/${id}`, {
			waitUntil: 'networkidle2',
			timeout: 5000
		});
```
We could try a cache poisoning by injecting a malicious payload through the `id` argument.<br/>
After some testing we finally get our payload right and we build a python script to get the flag (see script in exploit folder).<br/>
For this we need a "C2" server in order to exfiltrate the `moderator` session cookie.<br/>
For this purpose you can use <a href="https://webhook.site/">this</a> site.

Finally we run our script and get the cookie containing the flag value! 🏴
```console
python3 cache-poisoning-exploit.py
{"message":"Report received successfully!"}
```
On `webhook.site` you will see: <br/>
<div style="width: 65%; height: 65%">

  ![](images/webhook.png)
  
</div>  
<br/>

Copy the `session` value and decode it:<br/>

<div style="width: 65%; height: 65%">

  ![](images/flag.png)
  
</div>  
<br/>


