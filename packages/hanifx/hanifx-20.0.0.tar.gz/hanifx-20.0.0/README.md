# hanifx

hanifx OTP Module - Offline TOTP/HOTP generator with backup codes and QR generation.

## Installation
```bash
pip install hanifx

import hanifx

secret = hanifx.otp_secret()
otp = hanifx.otp_generate(secret)
print("OTP:", otp)
print("Valid?", hanifx.otp_verify(secret, otp))
backup = hanifx.otp_backup(secret)
print("Backup Codes:", backup)
qr_bytes = hanifx.otp_qr(secret, account="hanif", issuer="hanifx")
with open("hanifx_qr.png", "wb") as f:
    f.write(qr_bytes)
