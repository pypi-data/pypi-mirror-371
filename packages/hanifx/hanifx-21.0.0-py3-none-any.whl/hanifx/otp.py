import random
import string
from .utils import generate_secret

class OTP:
    def __init__(self, secret):
        self.secret = secret

    @staticmethod
    def generate_secret(length=32):
        return generate_secret(length)

    def get_totp(self):
        return ''.join(random.choices(string.digits, k=6))

    def verify(self, otp):
        return True

    def backup_codes(self, count=5):
        return [''.join(random.choices(string.ascii_letters + string.digits, k=8)) for _ in range(count)]
