#!/usr/bin/env python

from Crypto.Cipher import AES
import hashlib

def pad(data):
    length = 16 - (len(data) % 16)
    data += chr(length)*length
    return data

def encrypt(plainText, workingKey):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    plainText = pad(plainText).encode('utf-8')
    encDigest = hashlib.md5()
    encDigest.update(workingKey.encode('utf-8'))
    enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv)
    encryptedText = enc_cipher.encrypt(plainText).hex()
    return encryptedText

def decrypt(cipherText, workingKey):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    decDigest = hashlib.md5()
    decDigest.update(workingKey.encode('utf-8'))
    encryptedText = bytes.fromhex(cipherText)
    dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
    
    decryptedBytes = dec_cipher.decrypt(encryptedText)
    
    return decryptedBytes




from urllib.parse import parse_qs
encRep = 'ef45d436ff52c096982b1475d703ef1066c317b544cc9d7192ee08368b6ffcc3d6cf441f4043889f68d3495d8434f06ed5d475c0616ef8a824852d6fc3e01061ada631bd771aa1c51dc0e6f6f52a67b447818f6629be2f59ffd4a1192067147b1810276ce1e70fb4d4710cbb6eeb37294a62926cd62e6de126d3dd43b16d4b06effca0e1981e15f6809d90306c64c3d0ccfdedd87afb4912db7c114c1c31d2a1328f7d9506078c8ee5108a4fdf1c406b2accbe03c8e1ff181d8ed29160012c69e2b1311f05af7fc9eeae6a139235b022b3af3af1ac40967226d9c109eeba2f1d27d88b5e5f5ff7326da49b6572638e3dc1cd1933b95c5c11868a4fbe826842054f1d7d3aaa08ccfab331a8875c955dff6091b2299d03f04421742c3c3a164a1fdb301f7d2bc39034c22b115ef5254894352de9e806238859836840b44ccec52f67dc07c433bc6c7bb476e13aad66473facf7e70ee8a44eec18c893dc4f1659522278e28c51eab4868ee5d102da84460dbb068a116fb30f9b50a6fa9b5740f76a6af4a92259be9a959057730d9b0717ea0d9a556b59e6e43072c2cc7e92585efae9ca84feef2e70ae63503893992ff35bec76e67870bf4858c88cec63e20690570386d9921b9d639390b069ef7c8a7812c665779b8cfc8611c02877ef2cdb16d4d5d3bb02bde6cca0efb5261e91cb13296a52139cf550bc99d6612f6f00922ec8895dcf1d1b6828683e2fe2dc31f998f1e8c17e8307d09affb93b8065cb2f5a57957f181185ffe671c501c614960898e00529829d0f206d2809b1a770f8688e7fbb0f284bc39d90ee20f6e7c73671cbc6786dcf3f8ec7e66e33166b942dad3e57375ef1b0bad6c6fc85b77ae688468b0ad9671caf5fe7e64a3b12fc2038bc0742f969f87a2ccc24411f260a4efa710c2c9571923480cca71832c5154c33286ec59ff0b5739ef8c0b4d0008acad926591d9376de15bad262b93ceabe6867e119cba099752ca1f7aa86b3414c4ee324532242d5862c43394e9b020e7c2966d6feea'


encryption = decrypt(encRep,'33BA817A5AB3463BFDEF2658EC1ADC0A')
parsed_data = parse_qs(encryption.decode('latin-1'))

print(parsed_data)

