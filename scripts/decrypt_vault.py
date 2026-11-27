"""
Decrypt the Aurora vault to get UI strings.
The vault is in field[391] (1181 bytes), encrypted with ChaCha20.
Key is derived via SHA256 KDF from field[163] (64 bytes).
"""
import struct
import hashlib
from pathlib import Path

sys_path = r'C:\Users\J\Desktop\SRC CODE ASSEMBLY PROXY'
import sys
sys.path.insert(0, sys_path)
from ifix_codec import parse_ifix

SRC = Path(r'C:\Users\J\Desktop\MI PROJECT\SOURCE_EXTRACTED\assembly-csharp-patch.T0mFTHJhcvgBJrIRhg8bEapnUTM~3D')
IFIX_OFFSET = 2795

# ChaCha20 constants (from method[182])
SIGMA = b'expand 32-byte k'

def rotl(v, n):
    return ((v << n) & 0xffffffff) | (v >> (32 - n))

def quarter_round(a, b, c, d):
    a = (a + b) & 0xffffffff; d ^= a; d = rotl(d, 16)
    c = (c + d) & 0xffffffff; b ^= c; b = rotl(b, 12)
    a = (a + b) & 0xffffffff; d ^= a; d = rotl(d, 8)
    c = (c + d) & 0xffffffff; b ^= c; b = rotl(b, 7)
    return a, b, c, d

def chacha20_block(key, counter, nonce):
    # Setup state
    state = list(struct.unpack('<16I', SIGMA + key + nonce + struct.pack('<I', counter)))
    working_state = state[:]

    # 20 rounds (10 double rounds)
    for _ in range(10):
        # Column rounds
        for i in range(0, 16, 4):
            working_state[i], working_state[i+1], working_state[i+2], working_state[i+3] = \
                quarter_round(working_state[i], working_state[i+1], working_state[i+2], working_state[i+3])
        # Diagonal rounds
        working_state[0], working_state[5], working_state[10], working_state[15] = \
            quarter_round(working_state[0], working_state[5], working_state[10], working_state[15])
        working_state[1], working_state[6], working_state[11], working_state[12] = \
            quarter_round(working_state[1], working_state[6], working_state[11], working_state[12])
        working_state[2], working_state[7], working_state[12], working_state[13] = \
            quarter_round(working_state[2], working_state[7], working_state[12], working_state[13])
        working_state[3], working_state[8], working_state[13], working_state[14] = \
            quarter_round(working_state[3], working_state[8], working_state[13], working_state[14])

    # Add original state
    for i in range(16):
        state[i] = (state[i] + working_state[i]) & 0xffffffff

    return struct.pack('<16I', *state)

def chacha20_xor(key, nonce, ciphertext):
    plaintext = bytearray(len(ciphertext))
    blocks = (len(ciphertext) + 63) // 64

    for i in range(blocks):
        keystream = chacha20_block(key, i, nonce)
        block_start = i * 64
        block_end = min((i + 1) * 64, len(ciphertext))
        for j in range(block_end - block_start):
            plaintext[block_start + j] = ciphertext[block_start + j] ^ keystream[j]

    return bytes(plaintext)

def kdf_hkdf_sha256(master_key, salt, info, length):
    # Simplified HKDF-like KDF from method[165]
    # The actual method does a custom XOR-based KDF with SHA256
    # For now, we'll try direct SHA256 of key + salt
    h = hashlib.sha256()
    h.update(master_key)
    h.update(salt)
    if info:
        h.update(info)
    return h.digest()[:length]

def main():
    data = SRC.read_bytes()
    p = parse_ifix(data, IFIX_OFFSET)

    # Find field[163] (64-byte key) and field[391] (vault blob)
    print(f"Total fields: {len(p['fields'])}")
    for i, f in enumerate(p['fields']):
        if f['name'] == 'Mzb27d1c7eb31782':  # field[163]
            print(f"Found key field at index {i}: {f['name']}")
        if f['name'] == 'Mz8212c38779179f':  # field[391]
            print(f"Found vault field at index {i}: {f['name']}")

    # The vault blob is in the bytecode as immediate data
    # Need to extract from the raw IFix binary
    # For now, let's just extract and try to find the pattern

    raw = data[IFIX_OFFSET:]
    print(f"Raw IFix size: {len(raw)}")
    print(f"Searching for vault pattern...")

    # The vault is 1181 bytes, let's look for that size in bytecode
    # Actually, let's just dump the raw IFix and analyze manually first
    Path('C:/Users/J/Desktop/MI PROJECT/raw_ifix.bin').write_bytes(raw)
    print("Dumped raw IFix to raw_ifix.bin")

if __name__ == '__main__':
    main()
