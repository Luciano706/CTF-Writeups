# Web Application Vulnerability Assessment Writeup

## Initial Reconnaissance: File Upload Vulnerability Testing

My first approach was to test for unrestricted file upload vulnerabilities in the application. This is a common security weakness where applications fail to properly validate uploaded files, potentially allowing attackers to upload and execute malicious code on the server.

I attempted to bypass the file type restrictions by manipulating the filename. After several attempts, I discovered that using a null byte character (`%00`) in the filename successfully bypassed the initial validation. Specifically, by naming the file with the pattern `<filename>.py%00.txt`, the application accepted the upload, interpreting it as a harmless text file while potentially allowing Python code execution.

```
Filename used: exploit.py%00.txt
```

However, this initial success was limited as I discovered the application was implementing content sanitization on the uploaded files. This meant that even though I could upload files with potentially dangerous extensions, the server was stripping or neutralizing any harmful content within the files, rendering this attack vector ineffective for achieving code execution.

## Information Disclosure through Error Messages

After the initial file upload attempts proved unsuccessful, I shifted my approach to test for other vulnerabilities. I attempted to submit a file with an excessively long filename, which triggered an unexpected server error.

This error proved to be highly valuable as it revealed critical information about the application's backend:

1. The application was using the Werkzeug debugger console
2. The server's secret key was exposed in the error message
3. Details about the functions used to encrypt file content were disclosed

This information disclosure vulnerability provided significant insights into the application's architecture and security mechanisms. The exposed Werkzeug debugger could potentially allow for interactive debugging and code execution, while the secret key could be used to forge session tokens or decrypt sensitive data.

Despite having access to this valuable information, direct exploitation of the Werkzeug debugger wasn't immediately possible. I continued gathering information from various error messages while searching for additional attack vectors.

## Command Injection Discovery

After thorough testing of different input fields, I discovered that the recipient data field was vulnerable to manipulation. By adding a newline character to the input, I observed a distinct server response:

```
"Encryption attempt registered but may have failed."
```

This unusual response suggested potential command injection vulnerability. Command injection occurs when user input is incorrectly passed to system commands without proper sanitization, allowing attackers to execute arbitrary commands on the host system.

To confirm this vulnerability, I attempted to execute various system commands through this input field. The commands appeared to execute successfully, but no output was displayed on the page - indicating a blind command injection vulnerability where command execution occurs but results aren't returned to the attacker.

## Data Exfiltration Setup

Since the command injection was blind (no direct output visible), I needed to establish a method to exfiltrate data from the target system. I set up an HTTP server to receive POST requests containing the results of executed commands.

This exfiltration technique allowed me to:
1. Execute commands on the target system
2. Have those commands send their output to my controlled server
3. Retrieve sensitive information from the target system despite the blind nature of the vulnerability

By leveraging this command injection with data exfiltration, I was able to successfully complete the challenge and demonstrate the security weaknesses present in the application.

## Conclusion

This CTF challenge demonstrated a realistic attack progression:

1. Initial testing of common vulnerabilities (file upload)
2. Pivoting based on information disclosure (error messages revealing backend details)
3. Discovery of a more serious vulnerability (command injection)
4. Establishing exfiltration channels to overcome limitations (blind execution)

The vulnerabilities identified highlight the importance of proper input validation, error handling, and command execution safeguards in web applications. Particularly, the command injection vulnerability represents a critical security risk that could lead to complete system compromise in a real-world scenario.
