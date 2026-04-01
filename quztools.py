import os
import zipfile
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# =========================
# 🔑 INTERNALS
# =========================

def _derive_key(password, salt):
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    return kdf.derive(password.encode())

def _shift(data, n):
    return bytes([(b + n) % 256 for b in data])

def _unshift(data, n):
    return bytes([(b - n) % 256 for b in data])

def _reverse(data):
    return data[::-1]

# =========================
# 🔐 CORE
# =========================

def encrypt_bytes(data: bytes, password: str) -> bytes:
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    iv = os.urandom(16)

    padder = padding.PKCS7(128).padder()
    padded = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    enc = cipher.encryptor()
    encrypted = enc.update(padded) + enc.finalize()

    # custom layers
    encrypted = _shift(encrypted, len(password))
    encrypted = _reverse(encrypted)

    header = b"@QUZ{AES+SHIFT+REV}:"
    return header + salt + iv + encrypted


def decrypt_bytes(blob: bytes, password: str) -> bytes:
    header = b"@QUZ{AES+SHIFT+REV}:"

    if not blob.startswith(header):
        raise ValueError("Invalid QUZ file")

    data = blob[len(header):]

    salt = data[:16]
    iv = data[16:32]
    encrypted = data[32:]

    encrypted = _reverse(encrypted)
    encrypted = _unshift(encrypted, len(password))

    key = _derive_key(password, salt)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    dec = cipher.decryptor()
    padded = dec.update(encrypted) + dec.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()

# =========================
# 📦 FILE API
# =========================

def encrypt_file(input_path, output_path, password):
    with open(input_path, "rb") as f:
        data = f.read()

    blob = encrypt_bytes(data, password)

    temp = "reztm.pccb"
    with open(temp, "wb") as f:
        f.write(blob)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(temp)

    os.remove(temp)


def decrypt_file(input_path, output_path, password):
    with zipfile.ZipFile(input_path, "r") as z:
        z.extract("reztm.pccb")

    with open("reztm.pccb", "rb") as f:
        blob = f.read()

    os.remove("reztm.pccb")

    data = decrypt_bytes(blob, password)

    with open(output_path, "wb") as f:
        f.write(data)