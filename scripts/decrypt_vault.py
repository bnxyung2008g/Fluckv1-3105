"""
FLUCK V1.0.0 — decrypt_vault.py
================================
EXPERIMENTAL — no es un descifrador funcional completo.

Este script intenta localizar y descifrar el vault de strings dentro del
binario IFix del paquete .3105. El vault (campo[391], ~1181 bytes) está
cifrado con ChaCha20; la clave se deriva via SHA-256 desde el campo[163].

Estado actual: el script vuelca el IFix raw a disco para análisis manual.
No produce strings descifradas hasta que se complete el análisis del KDF
exacto y los parámetros de nonce usados en el bytecode.

Requisitos:
  - ifix_codec  (no incluido en este repositorio)
  - El binario extraído del .3105 en la ruta configurada en SRC

Configura SRC con la ruta al binario extraído antes de ejecutar.
"""

import struct
import hashlib
from pathlib import Path
import sys

# ---------------------------------------------------------------------------
# RUTA — ajusta al binario extraído de tu .3105
# ---------------------------------------------------------------------------
SRC = Path('assembly-csharp-patch.T0mFTHJhcvgBJrIRhg8bEapnUTM~3D')
IFIX_OFFSET = 2795

# ifix_codec no está incluido en este repositorio.
# Descomenta y ajusta la línea de abajo si lo tienes disponible:
# sys.path.insert(0, r'/ruta/a/ifix_codec')
# from ifix_codec import parse_ifix

# ChaCha20 constants
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
    state = list(struct.unpack('<16I', SIGMA + key + nonce + struct.pack('<I', counter)))
    working_state = state[:]
    for _ in range(10):
        for i in range(0, 16, 4):
            working_state[i], working_state[i+1], working_state[i+2], working_state[i+3] = \
                quarter_round(working_state[i], working_state[i+1], working_state[i+2], working_state[i+3])
        working_state[0], working_state[5], working_state[10], working_state[15] = \
            quarter_round(working_state[0], working_state[5], working_state[10], working_state[15])
        working_state[1], working_state[6], working_state[11], working_state[12] = \
            quarter_round(working_state[1], working_state[6], working_state[11], working_state[12])
        working_state[2], working_state[7], working_state[12], working_state[13] = \
            quarter_round(working_state[2], working_state[7], working_state[12], working_state[13])
        working_state[3], working_state[8], working_state[13], working_state[14] = \
            quarter_round(working_state[3], working_state[8], working_state[13], working_state[14])
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

def main():
    if not SRC.exists():
        sys.exit(
            f'ERROR: No se encuentra el binario fuente:\n  {SRC}\n'
            f'Extrae primero el archivo del .3105 y configura SRC en este script.'
        )

    data = SRC.read_bytes()
    raw  = data[IFIX_OFFSET:]
    print(f'Binario cargado: {len(data):,} bytes')
    print(f'IFix raw size:   {len(raw):,} bytes')
    print()
    print('NOTA: Este script está incompleto.')
    print('  El KDF exacto y los parámetros de nonce no han sido')
    print('  completamente verificados. El vault permanece cifrado.')
    print()

    out = Path('raw_ifix.bin')
    out.write_bytes(raw)
    print(f'IFix raw volcado a: {out}')
    print('Usa un analizador de bytecode IFix para inspeccionar manualmente.')

if __name__ == '__main__':
    main()
