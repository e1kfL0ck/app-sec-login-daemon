# Black box report

#### From Theo GAILLARD & Emile QUIVRON

## Scope

The project available at https://bitbucket.org/crane_4/appsecurity.git, made by group 6.

Only the web application has been tested. Therefore any other part of the project (databases calls, access, configuration files, etc.) is out of the scope of this report.

## Reported Vulnerabilities

1. **Stored XSS in the title of post**

   - **Description**: The application does not properly sanitize user input in the title field when creating a new post, allowing for stored Cross-Site Scripting (XSS) attacks. An attacker can inject malicious JavaScript code that will be executed in the context of other users viewing the posts list.
   - **Impact**: This vulnerability can lead to session hijacking, defacement, or redirection to malicious sites.
   - **Recommendation**: Implement proper input validation and output encoding to prevent XSS attacks.
   - **Used payload** :

```
POST /api/posts HTTP/1.1
Host: localhost
Cookie: session_id=ddc24b35616672863e66066cd25e5174bdc5dab6fbd0419a3ca400d1f7650319
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0
Accept: */*
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Referer: https://localhost/
Content-Type: multipart/form-data; boundary=----geckoformboundary9c3c45e0868a181c89e4de4af82f54b5
Content-Length: 321811
Origin: https://localhost
Sec-Gpc: 1
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Priority: u=0
Te: trailers
Connection: keep-alive

------geckoformboundary9c3c45e0868a181c89e4de4af82f54b5
Content-Disposition: form-data; name="title"

<img src='x' onerror=alert(document.location)>
------geckoformboundary9c3c45e0868a181c89e4de4af82f54b5
Content-Disposition: form-data; name="image"; filename="slide1_lahoud.png"
Content-Type: image/png

PNG
```
[Screenshot of the alert](./xss.png)
  
2. **Unproper verification of sessions for post deletions**

    - **Description**: The application does not make a proper verification of post owner prior to deletions resulting in the possibility for a user to delete the post of an other user.

3. **Panel admin template preview possible**

    - **Description** : Any visitor of the website can preview the admin panel template by accessing the URL /admin/ directly, the user is redirected to the login page, but after the preview of the page. Even tought the user cannot perform any action, or see any metrics without being logged in as an admin
    - **Recommendation** : Load the page and HTML/CSS/JS ressources only after a successful check of the user session as an admin.

[Screenshot of the admin panel preview](./admin.png)

4. **Inconsistant post name and image preview**
   
    - **Description** : At some time, the name of the post no matter the id asked with `/post.html?id=$id` will always return the last one. However, this issue does not seems to happen for comments. 
    - The route `/api/posts?id=$id` always return all the posts, no matter the id asked.b
## Observed good practices 

1. We did not manage to find any files with directory enumeration.
   [File enumeration](./ffuf.png)

2. No SSTI, SQLi or XSS found in other inputs than the one mentioned above.

3. No secrets disovered in the frontend code.
1. We did not manage to find SSTI, SQLInjection, RCE, Security flaws in the file upload
2. No secrets disovered


## TLS tester run

Obsoleted CBC ciphers (AES, ARIA etc.) offered by the server.
TLS v1.3 is not supported by the server.
LUCKY13 (CVE-2013-0169), experimental, potentially VULNERABLE, uses cipher block chaining (CBC) ciphers with TLS.
