
import hashlib
import random
import string


def make_salt(length=32):
    """
    Get a salt for password.
    """
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def hash_password(raw_password, salt):
    """
    Get the hash of the password.
    """
    hash_obj = hashlib.sha1()
    hash_obj.update(raw_password.encode())
    hash_obj.update(salt.encode())
    return hash_obj.hexdigest()


def check_password(raw_password, password, salt):
    """
    Check if the password is correct.
    """
    return password == hash_password(raw_password, salt)
