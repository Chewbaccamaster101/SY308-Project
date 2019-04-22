from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt(data,key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return [cipher.nonce,tag,ciphertext]

def decrypt(nonce,tag,ciphertext,key):
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return data

def main():
    key = get_random_bytes(16)
    file_out = open("key.bin", "wb")
    file_out.write(key)
    file_out.close()


if __name__ == "__main__":
    main()
