from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

def generate_hash_from(raw_password: str):

    hasher = PasswordHasher()
    return hasher.hash(raw_password)


def verify_hash(hashed: str, raw: str):

    hasher = PasswordHasher()
    message = ''
    verified = False
    try:
        verified = hasher.verify(hashed, raw)
    except VerifyMismatchError:
        message = 'Incorrect password!'
    except Exception as error:
        message = f'Unspected error: {error}'

    return verified, message
