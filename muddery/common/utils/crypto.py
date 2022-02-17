
from Crypto.PublicKey import RSA as CryptoRSA
from Crypto.Cipher import PKCS1_v1_5


class RSA(object):
    """
    Deal with crypto.
    """
    def __init__(self):
        self.key = None
        self.cipher = None

    def generate_key(self, length=1024):
        """
        Generate RSA's key.
        :param length:
        :return:
        """
        self.key = CryptoRSA.generate(length)

    def export_private_key(self, format="PEM"):
        return self.key.export_key(format=format)

    def export_public_key(self, format="PEM"):
        return self.key.public_key().export_key(format=format)

    def load_private_key_file(self, private_key_path):
        """
        Load private key from a PEM file.
        """
        with open(private_key_path, "rb") as fp:
            self.key = CryptoRSA.import_key(fp.read())
            self.cipher = PKCS1_v1_5.new(self.key)

    def load_public_key_file(self, public_key_path):
        """
        Load public key from a PEM file.
        """
        with open(public_key_path, "rb") as fp:
            self.key = CryptoRSA.import_key(fp.read())
            self.cipher = PKCS1_v1_5.new(self.key)

    def encrypt(self, data):
        if self.cipher:
            return self.cipher.encrypt(data)

    def decrypt(self, data):
        if self.cipher:
            return self.cipher.decrypt(data, None)
