import hashlib
from .base60 import b60_encode_int, b60_decode_int
from .primes import _gen_prime, _modinv
import math

# ===== Key Generation =====
def generate_keypair(bits: int = 1024):
    half = bits // 2
    p = _gen_prime(half)
    q = _gen_prime(bits - half)
    while p == q:
        q = _gen_prime(bits - half)
    n = p * q
    phi = (p-1) * (q-1)
    e = 65537
    if math.gcd(e, phi) != 1:
        e = 3
        while math.gcd(e, phi) != 1:
            e += 2
    d = _modinv(e, phi)
    return {"e": e, "n": n}, {"d": d, "n": n}

# ===== Export/Import Base60 =====
def export_public_key_b60(pub): 
    return {"e": b60_encode_int(pub["e"]), "n": b60_encode_int(pub["n"])}
def import_public_key_b60(data):
    return {"e": b60_decode_int(data["e"]), "n": b60_decode_int(data["n"])}
def export_private_key_b60(priv):
    return {"d": b60_encode_int(priv["d"]), "n": b60_encode_int(priv["n"])}
def import_private_key_b60(data):
    return {"d": b60_decode_int(data["d"]), "n": b60_decode_int(data["n"])}

# ===== Padding =====
def _pad_block(m_bytes: bytes, block_len: int) -> bytes:
    tag = hashlib.sha256(m_bytes).digest()[:16]
    core = b"\x00" + tag + m_bytes + b"\x01"
    if len(core) >= block_len:
        raise ValueError("message too long")
    return core + b"\x00"*(block_len - len(core))

def _unpad_block(p_bytes: bytes) -> bytes:
    if len(p_bytes) < 18 or p_bytes[0] != 0x00: 
        raise ValueError("bad padding")
    i = len(p_bytes)-1
    while i>=0 and p_bytes[i]==0x00: i -= 1
    if p_bytes[i]!=0x01: raise ValueError("bad padding")
    body = p_bytes[1:i]
    tag, msg = body[:16], body[16:]
    if hashlib.sha256(msg).digest()[:16]!=tag:
        raise ValueError("bad tag")
    return msg

# ===== Encrypt/Decrypt =====
def encrypt_b60(plaintext: bytes, pub: dict) -> str:
    e, n = pub["e"], pub["n"]
    k = (n.bit_length()+7)//8
    max_msg = max(1, k-20)
    blocks = []
    for i in range(0, len(plaintext), max_msg):
        chunk = plaintext[i:i+max_msg]
        padded = _pad_block(chunk, k-1)
        c = pow(int.from_bytes(padded,"big"), e, n)
        blocks.append(b60_encode_int(c))
    return "~".join(blocks)

def decrypt_b60(ciphertext: str, priv: dict) -> bytes:
    d, n = priv["d"], priv["n"]
    k = (n.bit_length()+7)//8
    out = bytearray()
    for token in ciphertext.split("~"):
        c = b60_decode_int(token)
        m_int = pow(c, d, n)
        m_bytes = m_int.to_bytes(k-1, "big")
        out.extend(_unpad_block(m_bytes))
    return bytes(out)
