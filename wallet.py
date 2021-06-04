import binascii
# Imports from pycryptodome
from Crypto.PublicKey import RSA
import Crypto.Random


class Wallet:
    def __init__(self) -> None:
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        self.private_key, self.public_key = self.generate_keys()

    def load_keys(self):
        pass

    def generate_keys(self):
        private_key = RSA.generate(2048, Crypto.Random.new().read)
        public_key = private_key.public_key()
        return (binascii.hexlify(private_key.export_key(format='DER')).decode('ascii'), binascii.hexlify(public_key.export_key(format='DER')).decode('ascii'))


# wallet = Wallet()
# print(wallet.private_key+'\n'+wallet.public_key)
