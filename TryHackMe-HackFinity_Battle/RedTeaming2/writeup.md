# Pass the Hash Attack: Gaining Administrative Access

## Overview

This writeup details the process of exploiting a Windows system using the Pass the Hash (PtH) attack technique. By leveraging extracted password hashes from a memory dump and identifying open ports, we were able to gain administrative access to the target system.

## Tools Used

- Nmap (port scanning)
- NetExec (formerly CrackMapExec) 
- Evil-WinRM
- Various PtH tools (psexec.py, wmiexec.py, smbexec.py, atexec.py, dcomexec.py)
- xfreerdp

## Attack Methodology

### 1. Initial Reconnaissance

- Performed a comprehensive analysis of the memory dump
- Extracted critical information including usernames and NTLM password hashes
- Conducted port scanning with Nmap to identify open services
- Discovered that ports 445 (SMB) and 3389 (RDP) were open

### 2. Initial Pass the Hash Attempts

With the extracted hashes and open ports identified, we proceeded with Pass the Hash attack attempts:

- Used NetExec to enumerate available SMB shares
  ```
  netexec smb <target_ip> -u <username> -H <hash>
  ```
- Discovered that while shares were accessible, they were non-writable, preventing command execution

### 3. Expanded Attack Vectors

We attempted multiple Pass the Hash techniques to gain system access:

- Tried RDP access using xfreerdp with the extracted hashes since port 3389 was open
  ```
  xfreerdp /v:<target_ip> /u:<username> /pth:<hash>
  ```
- Attempted various Impacket tools for remote command execution:
  - psexec.py
  - wmiexec.py
  - smbexec.py
  - atexec.py
  - dcomexec.py

### 4. Breakthrough with Evil-WinRM

After multiple failed attempts, we tried Evil-WinRM:

- Discovered that one of the user accounts from the dump was accessible via WinRM
  ```
  evil-winrm -i <target_ip> -u <username> -H <hash>
  ```
- Successfully established a PowerShell session on the target system
- Gained access to the file system but lacked permissions to access the Administrator directory

### 5. Privilege Escalation

- Methodically tested each extracted user account with Evil-WinRM
- Successfully identified that the "DarkInjector" account had sufficient privileges
- Used the "DarkInjector" account to access the Administrator directory and retrieve the flag

## Conclusion

This attack demonstrates the effectiveness of Pass the Hash techniques when valid NTLM hashes are available. While initial attempts with common tools were unsuccessful, persistence with alternative methods (Evil-WinRM) eventually led to successful system compromise. The key insight was to systematically try different user accounts, as the "DarkInjector" account had the necessary privileges to access the Administrator directory.
