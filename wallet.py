import binascii
# Imports from pycryptodome
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random


class Wallet:
    def __init__(self) -> None:
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        self.private_key, self.public_key = self.generate_keys()

    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open('wallet.txt', mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
            except (IOError, IndexError):
                print('Saving wallet failed...')

    def load_keys(self):
        try:
            with open('wallet.txt', mode='r') as f:
                keys = f.readlines()
                self.public_key = keys[0][:-1]
                self.private_key = keys[1]
        except (IOError, IndexError):
            print('Loading wallet failed...')

    def generate_keys(self):
        private_key = RSA.generate(2048, Crypto.Random.new().read)
        public_key = private_key.public_key()
        return (binascii.hexlify(private_key.export_key(format='DER')).decode('ascii'), binascii.hexlify(public_key.export_key(format='DER')).decode('ascii'))

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.import_key(
            binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) +
                       str(amount)).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

# wallet = Wallet()
# print(wallet.private_key+'\n'+wallet.public_key)