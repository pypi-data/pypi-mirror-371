import qrcode
import io
import secrets
import string

def generate_secret(length=32):
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def generate_qr(secret, account="user", issuer="hanifx"):
    uri = f"otpauth://totp/{issuer}:{account}?secret={secret}&issuer={issuer}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bytes_io = io.BytesIO()
    img.save(bytes_io, format="PNG")
    return bytes_io.getvalue()
