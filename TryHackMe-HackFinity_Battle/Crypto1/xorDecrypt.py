import argparse

def decryptXorRepeatingKey(cypherText, knownPlainText):
	cypher=bytes.fromhex(cypherText) #Get the bytes from the exadecimal text
	bytesKnownPlain=knownPlainText.encode() #Get the bytes from the ASCII text

	key_part=[c^p for c,p in zip(cypher[:len(bytesKnownPlain)],bytesKnownPlain)] #Get part of the key by XORing the first N bytes of the cypher text with the known plain text, with N being the byte length of the known plain text

	return key_part


def decryptMessageGivenKey(cypherText, key):
	cypher=bytes.fromhex(cypherText) #Get they bytes from the hexadecimal text
	key=bytes(key) 
	plainText=bytes([c^key[i % len(key)] for i,c in enumerate(cypher)]) #Enumerate the cypher bytes, having i as a counter and c as the data for that istance of the counter, XORing the bytes from the cypher text with the key, taking i%len(key) to keep repeating the key
	return plainText


def encrtyptMessageXorRepeatingKey(plainText, key):
	plainBytes=plainText.encode() #Get the bytes from the plain text ASCII
	keyBytes=key.encode()
	cypherText=bytes([p^keyBytes[i % len(keyBytes)] for i,p in enumerate(plainBytes)]) #Repeat the XOR operation for the entire length of the array, each plainByte get XORed withe each byte from the key; the modulus let you restart the counter when going over the key length
	return cypherText

parser = argparse.ArgumentParser("xorDecrypt.py")
#Flags to encrypot o decrypt
parser.add_argument("-d", "--decrypt", action="store_true", help="Decrypt a message")
parser.add_argument("-e", "--encrypt", action="store_true", help="Encrypt a message")

#Arguments with the text to cypher/decypher and key/known plain text
parser.add_argument("text", type=str, help="The text you want to encrypt/decrypt, based on the specified flag (must be in hexadecimal format if it's cypher text)")
parser.add_argument("key_knownText", type=str, help="Either The key if you want to encrypt/decrypt with it, or the known plainText you knoiw it is at the start of the plainText to get part of the key")


CRED = '\033[91m'
CEND = '\033[0m'
print(CRED+r"""
 _____                                                        _____ 
( ___ )------------------------------------------------------( ___ )
 |   |                                                        |   | 
 |   |  _   ,   __  _ __                                      |   | 
 |   | ' \ /   / ')' )  )      /                    _/_       |   | 
 |   |    X   /  /  /--'    __/ _  _. __  __  , _   /  __ __  |   | 
 |   |   / \_(__/  /  \_   (_/_</_(__/ (_/ (_/_/_)_<__(_)/ (_ |   | 
 |   |                                      / /               |   | 
 |   |                                     ' '                |   | 
 |___|                                                        |___| 
(_____)------------------------------------------------------(_____)
"""+CEND)


args=parser.parse_args()
#if args.operation == "encrypt":

if args.decrypt:
	choice=input("Do you want to decrypt the cypher text using the key or using a plain text you know it's at the start ot the plain text?(key/known): ")

	if choice.lower()=="known":
		key_part=decryptXorRepeatingKey(args.text, args.key_knownText)


		print(CRED+r"""
         _______
        |.-----.|
        ||x . x||
        ||_.-._||		GOT A KEY!
        `--)-(--`
       __[=== o]___
      |:::::::::::|\
      `-=========-`
			"""+CEND)


		print("Hex key: ",bytes(key_part).hex())
		print("ASCII key: ",bytes(key_part))

		choice=input(CRED+"\nDo you wanna try to decrypt the message with the found key?(Y/n): "+CEND)
		if choice.lower()=="y":
			plainText=decryptMessageGivenKey(args.text, key_part)
			print(CRED,"ASCII Message: ",plainText.decode(errors="ignore"),CEND)

	elif choice.lower()=="key":
		plainText=decryptMessageGivenKey(args.text, args.key_knownText.encode())
		print(CRED,"ASCII Message: ",plainText.decode(errors="ignore"),CEND)
elif args.encrypt:
	cypherText=encrtyptMessageXorRepeatingKey(args.text, args.key_knownText)
	print("Hex cypherText: ",bytes(cypherText).hex())