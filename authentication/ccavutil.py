#!/usr/bin/env python

import hashlib
from Crypto.Cipher import AES
from binascii import hexlify

def encrypt(plainText, workingKey):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    encDigest = hashlib.md5()
    encDigest.update(workingKey.encode())
    cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv)
    encryptedText = cipher.encrypt(pad(plainText.encode()))
    return hexlify(encryptedText).decode()

def pad(data):
    length = 16 - (len(data) % 16)
    data += bytes([length]) * length
    return data

def decrypt(cipherText,workingKey):
    iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    decDigest = hashlib.md5()
    decDigest.update(workingKey.encode())
    decryptedText = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
    return decryptedText.decrypt(bytes.fromhex(cipherText))
