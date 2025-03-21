# Digital Forensics Challenge: Flag Fragment Hunt

## Overview

This writeup details a digital forensics challenge where the objective was to locate five hidden fragments of a flag within a compromised Linux system. Each fragment was concealed using different encoding techniques and hidden in various system locations that an attacker might use for persistence.

## Tools Used

- Base64 decoder
- Hexadecimal decoder
- Linux command line utilities
- System file inspection techniques

## Flag Hunt Methodology

### Fragment 1: Cron Job Analysis

The first fragment was hidden within a suspicious cron job:

1. Examined the system's scheduled tasks
   ```bash
   cat /etc/crontab
   ```

2. Discovered a process written in Base64
3. The process contained a hexadecimal-encoded string
4. Decoded the hex string to reveal the first fragment: `THM{y0`

### Fragment 2: SSH Key Investigation

The second fragment was concealed in an SSH authorization key:

1. Systematically searched through user directories for SSH configurations
   ```bash
   find /home -name ".ssh" -type d
   ```

2. Located a suspicious authorization key in the user "zeroday" directory
3. Identified an unusual section at the end of the key
4. Decoded the hexadecimal string to reveal the second fragment: `u_g0t`

### Fragment 3: Bash Profile Examination

The third fragment was hidden in a user's bash configuration:

1. Investigated the home directory of user "specter"
   ```bash
   cat /home/specter/.bashrc
   ```

2. Found a Base64-encoded string within the .bashrc file
3. Decoded the string to reveal the third fragment: `3v3ryt`

### Fragment 4: Service Analysis

The fourth fragment was embedded in a suspicious system service:

1. Analyzed running services on the system
   ```bash
   systemctl list-units --type=service
   ```

2. Identified an unusual service named "chiper.service"
3. Examined the service configuration files
   ```bash
   cat /etc/systemd/system/chiper.service
   ```

4. Found a Base64-encoded string within the service file
5. Decoded the string to reveal the fourth fragment: `h1ng`

### Fragment 5: Login Message Investigation

The final fragment was hidden in the system's login message configuration:

1. Examined the dynamic message of the day (MOTD) directory
   ```bash
   ls -la /etc/update-motd.d/
   ```

2. Analyzed the "00-header" file that generates the welcome message
3. Discovered a Python script that connects to a site with a hexadecimal-encoded URL
4. Decoded the hexadecimal string to reveal the final fragment: `d0wn}`

## Complete Flag

By combining all five fragments in the order they were discovered, the complete flag was reconstructed:

`THM{y0u_g0t_3v3ryth1ng_d0wn}`

## Conclusion

This challenge demonstrated the importance of thorough system examination during forensic investigations. The flag fragments were strategically hidden in locations commonly used for persistence by attackers, including cron jobs, SSH configurations, user profiles, system services, and login scripts. The use of various encoding techniques (Base64 and hexadecimal) added an additional layer of obfuscation that had to be overcome to retrieve the complete flag.
