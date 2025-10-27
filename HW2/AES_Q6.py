# https://www.pycryptodome.org/src/examples#encrypt-data-with-aes
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util import Padding

data = 'secret data to transmit'.encode()

print('-'*20, 'ECB', '-'*20)
print('plain text: ', data)

aes_key = get_random_bytes(16)

cipher = AES.new(aes_key, AES.MODE_ECB)
ciphertext = cipher.encrypt(Padding.pad(data, AES.block_size))
print(f'cipher text: {' '.join([hex(i) for i in ciphertext])}')

cipher = AES.new(aes_key, AES.MODE_ECB)
decrepted = Padding.unpad(cipher.decrypt(ciphertext), AES.block_size)
print('decrepted text: ', decrepted)

print('-'*20, 'CBC', '-'*20)
print('plain text: ', data)

aes_key = get_random_bytes(16)
aes_IV = get_random_bytes(16)
print(f'IV: {' '.join([hex(i) for i in aes_IV])}')

cipher = AES.new(aes_key, AES.MODE_CBC, aes_IV)
ciphertext = cipher.encrypt(Padding.pad(data, AES.block_size))
print(f'cipher text: {' '.join([hex(i) for i in ciphertext])}')

cipher = AES.new(aes_key, AES.MODE_CBC, aes_IV)
decrepted = Padding.unpad(cipher.decrypt(ciphertext), AES.block_size)
print('decrepted text: ', decrepted)