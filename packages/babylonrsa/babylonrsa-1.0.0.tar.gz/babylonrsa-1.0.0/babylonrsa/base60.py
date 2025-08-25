# Base60 Encoding/Decoding
B60_ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"[:60]
B60_IDX = {ch: i for i, ch in enumerate(B60_ALPH)}

def b60_encode_int(n: int) -> str:
    if n == 0: return "0"
    s = []
    while n > 0:
        n, r = divmod(n, 60)
        s.append(B60_ALPH[r])
    return "".join(reversed(s))

def b60_decode_int(s: str) -> int:
    n = 0
    for ch in s:
        n = n * 60 + B60_IDX[ch]
    return n

def b60_encode_bytes(b: bytes) -> str:
    return b60_encode_int(int.from_bytes(b, "big"))

def b60_decode_bytes(s: str) -> bytes:
    n = b60_decode_int(s)
    length = (n.bit_length() + 7) // 8
    return n.to_bytes(length or 1, "big")
