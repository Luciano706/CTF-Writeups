# Repeating-Key XOR Cipher Challenge Writeup

1. **Basic XOR Operation**: XOR (exclusive OR) is a bitwise operation that takes two equal-length bit patterns and produces a third where the resulting bit is set to 1 if the corresponding bits of the two operands are different, and 0 if they are the same.

2. **Repeating-Key Mechanism**: In a repeating-key XOR cipher:
   - A key of arbitrary length is used
   - The plaintext is XORed byte-by-byte with the key
   - When the end of the key is reached, it repeats from the beginning
   - This continues until the entire plaintext is encrypted

3. **Mathematical Representation**:
   ```
   C[i] = P[i] ⊕ K[i mod len(K)]
   ```
   Where:
   - C[i] is the i-th byte of ciphertext
   - P[i] is the i-th byte of plaintext
   - K[i mod len(K)] is the corresponding byte of the repeating key
   - ⊕ represents the XOR operation

4. **Key Properties of XOR**:
   - XOR is its own inverse: A ⊕ B ⊕ B = A
   - This property is crucial for both encryption and decryption

## Vulnerability Analysis

Despite its simplicity, repeating-key XOR has a critical vulnerability: if you know part of the plaintext, you can recover the corresponding part of the key. This is due to the mathematical properties of XOR:

```
If C = P ⊕ K, then K = P ⊕ C
```

Where:
- C is the ciphertext
- P is the plaintext
- K is the key

This vulnerability allows for a technique known as "crib dragging" or a known-plaintext attack.

## Solution Approach

### 1. Initial Analysis

After studying the properties of repeating-key XOR ciphers, I identified that the challenge could be solved using a known-plaintext attack. The challenge description indicated that all messages began with the text "ORDER:", providing the critical known plaintext needed for the attack.

### 2. Crib Dragging Implementation

Knowing that "ORDER:" appeared at the beginning of the plaintext, I could recover the first 6 bytes of the key by XORing the known plaintext with the corresponding ciphertext:

```
Key[0...5] = "ORDER:" ⊕ Ciphertext[0...5]
```

This technique, known as crib dragging, leverages the XOR property that:

```
Ciphertext ⊕ Plaintext = Key
```

### 3. Key Recovery

I implemented a Python script to perform this operation:

```python
def decrypt_xor_repeating_key(cipher_text, known_plain_text):
    cipher = bytes.fromhex(cipher_text)  # Convert hex ciphertext to bytes
    bytes_known_plain = known_plain_text.encode()  # Convert known plaintext to bytes
    
    # XOR the first N bytes of ciphertext with known plaintext to get key bytes
    key_part = [c ^ p for c, p in zip(cipher[:len(bytes_known_plain)], bytes_known_plain)]
    
    return key_part
```

By applying this function with the ciphertext and the known plaintext "ORDER:", I was able to recover part of the key.

### 4. Complete Key Discovery

After recovering the first part of the key, two scenarios were possible:
- If the key length was less than or equal to the known plaintext length, I would have the complete key
- If the key was longer, I would only have part of it and would need additional techniques

In this case, I discovered that the recovered key was "Sneaky", which was the complete key. This was fortunate as the key was relatively short (6 characters).

### 5. Message Decryption

With the complete key recovered, I could decrypt the entire message by XORing the ciphertext with the repeating key:

```python
def decrypt_message_given_key(cipher_text, key):
    cipher = bytes.fromhex(cipher_text)  # Convert hex ciphertext to bytes
    key = bytes(key)  # Ensure key is in bytes format
    
    # XOR each byte of ciphertext with corresponding byte of repeating key
    plain_text = bytes([c ^ key[i % len(key)] for i, c in enumerate(cipher)])
    
    return plain_text
```

## Conclusion

This challenge demonstrated the fundamental vulnerability of repeating-key XOR ciphers to known-plaintext attacks. By knowing just a small portion of the plaintext ("ORDER:"), I was able to recover the encryption key "Sneaky" and subsequently decrypt the entire message.

The key insights from this challenge are:

1. Repeating-key XOR ciphers are vulnerable when any portion of the plaintext is known
2. The XOR operation's properties make it possible to extract the key directly
3. Once part of the key is known, the repeating nature makes it possible to decrypt the entire message

This type of cryptographic vulnerability highlights why modern encryption systems use much more sophisticated algorithms with proper key management practices.

## Tools Used

- Python for implementing the XOR operations and key recovery
- Basic understanding of cryptographic principles and XOR properties

## References

- [XOR Cipher on Wikipedia](https://en.wikipedia.org/wiki/XOR_cipher)
- [Known-plaintext attack](https://en.wikipedia.org/wiki/Known-plaintext_attack)
