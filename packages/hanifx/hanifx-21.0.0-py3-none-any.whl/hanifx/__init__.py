from .otp import OTP
from .utils import generate_secret, generate_qr
from .version import __version__

def otp_secret():
    return generate_secret()

def otp_generate(secret):
    return OTP(secret).get_totp()

def otp_verify(secret, otp):
    return OTP(secret).verify(otp)

def otp_backup(secret):
    return OTP(secret).backup_codes()

def otp_qr(secret, account="user", issuer="hanifx"):
    return generate_qr(secret, account, issuer)
