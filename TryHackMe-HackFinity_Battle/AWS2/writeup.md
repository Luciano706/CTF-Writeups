# AWS S3 Bucket Vulnerability Writeup

## Challenge Description

**Challenge Name**: AWS S3 Bucket Analysis  
**Description**: "DarkInjector has been using a Cmail phishing website to try to steal our credentials. We believe some of our users may have fallen for his trap. Can you retrieve the list of victim users"  
**Target**: `http://darkinjector-phish.s3-website-us-west-2.amazonaws.com`

## Initial Reconnaissance

The first step was to access the provided URL to examine the phishing site. Navigating to the URL, I found a login page mimicking a webmail service called "Cmail".

![Cmail Phishing Page](https://i.imgur.com/placeholder.png)

The page contained a simple login form with fields for email and password, designed to steal credentials from unsuspecting users.

## Site Structure Analysis

Examining the source code of the page, I identified that it was a static site hosted on an AWS S3 bucket:

```html
<div class="login-container">
    <h1>Cmail Login</h1>
    <form action="/login" method="POST">
        <label for="email">Email Address</label>
        <input type="text" id="email" name="email" placeholder="Enter your email" required>
        
        <label for="password">Password</label>
        <input type="password" id="password" name="password" placeholder="Enter your password" required>
        
        <button type="submit">Login</button>
    </form>

    <div class="footer">
        <p>Forgot your password? <a href="/reset-password">Reset it here</a></p>
    </div>
</div>
```

The form was configured to send data to `/login` with the POST method. However, since the site was hosted on a static S3 bucket, it couldn't process POST requests. This suggested that the attacker might have used another service to collect credentials, or that the form was intentionally non-functional and served only as bait.

## Vulnerability Identification

I attempted to access the `/login` and `/reset-password` endpoints mentioned in the HTML code, but both returned 404 errors with details confirming it was an S3 bucket:

```
404 Not Found

Code: NoSuchKey
Message: The specified key does not exist.
Key: login
RequestId: GD0AQB0PWM3ARAH4
HostId: qtQSahDYZMxRRXvlE16hXOIwsr8GJf7hOHAZGgZCI8jAfWBnKx+Ca6D2FGCfjw96iXMqT4Kiguk=
```

The main vulnerability was identified when I tried to access the S3 bucket directly without the "website" prefix:

```
http://darkinjector-phish.s3.amazonaws.com
```

This revealed that the bucket was configured to allow public listing of its contents, a serious security flaw.

## Exploiting the Vulnerability

By accessing the bucket URL directly, I obtained an XML listing of the contents:

```xml
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Name>darkinjector-phish</Name>
  <Prefix/>
  <Marker/>
  <MaxKeys>1000</MaxKeys>
  <IsTruncated>false</IsTruncated>
  <Contents>
    <Key>captured-logins-093582390</Key>
    <LastModified>2025-03-17T06:46:17.000Z</LastModified>
    <ETag>"923e89c3ff247c768368b0d486484af4"</ETag>
    <Size>132</Size>
    <Owner>
      <ID>903215f2913d2f3026c35e300c621d0ccd51f13f578c37051b846ee8287567de</ID>
      <DisplayName>ariz</DisplayName>
    </Owner>
    <StorageClass>STANDARD</StorageClass>
  </Contents>
  <Contents>
    <Key>index.html</Key>
    <LastModified>2025-03-17T06:25:33.000Z</LastModified>
    <ETag>"3b392b5fc343b899cc3d67b6ecb2d025"</ETag>
    <Size>2300</Size>
    <Owner>
      <ID>903215f2913d2f3026c35e300c621d0ccd51f13f578c37051b846ee8287567de</ID>
      <DisplayName>ariz</DisplayName>
    </Owner>
    <StorageClass>STANDARD</StorageClass>
  </Contents>
</ListBucketResult>
```

This revealed two files:
1. `index.html` - The phishing page
2. `captured-logins-093582390` - A file likely containing the stolen credentials

I then accessed the credentials file directly:

```
http://darkinjector-phish.s3.amazonaws.com/captured-logins-093582390
```

The file contained the victims' credentials in CSV format:

```
user,pass
munra@thm.thm,Password123
test@thm.thm,123456
mario@thm.thm,Mario123
flag@thm.thm,THM{this_is_not_what_i_meant_by_public}
```

The last credential contained the CTF challenge flag: `THM{this_is_not_what_i_meant_by_public}`

## Identified Vulnerabilities

1. **Misconfigured S3 Bucket Permissions**
   - The bucket was configured to allow public read access and listing of contents
   - Anyone could view and download all files in the bucket

2. **Exposure of Sensitive Data**
   - User credentials stored in plaintext in a publicly accessible file
   - No encryption or protection of sensitive data

3. **Active Phishing Site**
   - The bucket hosted an active phishing site mimicking a webmail service
   - The site was designed to deceive users and steal their credentials

## Impact

The impact of these vulnerabilities is significant:

1. **Confidentiality Breach**: Unauthorized access to sensitive information, violating user data confidentiality
2. **Credential Theft**: Stolen credentials could be used for unauthorized access
3. **Potential Identity Theft**: The information obtained could be used for identity theft
4. **Credential Stuffing Attacks**: If users reuse passwords, the credentials could be used for attacks on other services



