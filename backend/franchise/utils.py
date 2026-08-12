import secrets
import string


def generate_temp_code():

    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))


def generate_otp():

    return ''.join(str(secrets.randbelow(10)) for _ in range(8))