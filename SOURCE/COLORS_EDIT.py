"""
=============================================================================
  FLUCK V1.0.0 — EDITOR DE COLORES DEL PANEL
  Basado en análisis real del binario IFix extraído del paquete .3105

  INSTRUCCIONES:
  1. Configura SRC_BYTES y OUT_BYTES abajo para que apunten a tu equipo
  2. Cambia las tuplas de color en la sección "COLORES DEL PANEL"
  3. Ejecuta:   python COLORS_EDIT.py
  4. Se genera:  assembly-csharp-patch-RECOLORED.bytes
  5. Usa ese archivo como payload para empaquetar un nuevo .3105

  FORMATO DE COLOR:
    Cada color es una tupla (R_int, G_int, B_int, A_int)
    donde cada int es el float del canal codificado en IEEE-754.

  CONVERTIR HEX → INT:
      import struct
      def to_int(f): return struct.unpack('<i', struct.pack('<f', f))[0]
      # Ejemplo: canal R de #FF7700 = 255/255 = 1.0
      to_int(1.0)   = 1065353216
      to_int(0.47)  = 1055131975
      to_int(0.0)   = 0

  COLORES RÁPIDOS (R, G, B, A) ya convertidos a ints:
    Rojo         (1,0,0,1)        1065353216, 0, 0, 1065353216
    Verde        (0,1,0,1)        0, 1065353216, 0, 1065353216
    Azul         (0,0.5,1,1)      0, 1056964608, 1065353216, 1065353216
    Naranja      (1,0.47,0,1)     1065353216, 1055131975, 0, 1065353216
    Morado       (0.5,0,1,1)      1056964608, 0, 1065353216, 1065353216
    Cian         (0,0.85,1,1)     0, 1062836634, 1065353216, 1065353216
    Rosa         (1,0.2,0.6,1)    1065353216, 1045220557, 1058642330, 1065353216
    Dorado       (1,0.76,0.3,1)   1065353216, 1061326684, 1050253722, 1065353216
    Blanco       (1,1,1,1)        1065353216, 1065353216, 1065353216, 1065353216
    Negro        (0,0,0,1)        0, 0, 0, 1065353216
=============================================================================
"""

import struct
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# RUTAS — ajusta estas dos líneas a tu equipo
# ---------------------------------------------------------------------------
SRC_BYTES = Path(r'assembly-csharp-patch.T0mFTHJhcvgBJrIRhg8bEapnUTM~3D')
OUT_BYTES = Path(r'assembly-csharp-patch-RECOLORED.bytes')

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def i2b(i):
    return struct.pack('<i', i)

def seq_bytes(t):
    return b''.join(i2b(v) for v in t)

# Para cada instruccion IFix el stream es: (op:i32, val:i32) = 8 bytes
# op=3 es Ldc_R4. Las 4 instrucciones de un Color(r,g,b,a) forman 32 bytes:
# (3,R)(3,G)(3,B)(3,A)
OP_LDC = 3

def color_stream(r_int, g_int, b_int, a_int):
    """Los 32 bytes que representan 4 instrucciones Ldc_R4 en el stream IFix."""
    return (b''.join([i2b(OP_LDC), i2b(r_int),
                      i2b(OP_LDC), i2b(g_int),
                      i2b(OP_LDC), i2b(b_int),
                      i2b(OP_LDC), i2b(a_int)]))

def to_float(i):
    return struct.unpack('<f', struct.pack('<i', i))[0]

# ---------------------------------------------------------------------------
#  ★  COLORES DEL PANEL  —  CAMBIA AQUÍ  ★
#
#  Formato: (R_int, G_int, B_int, A_int)
#  Los valores originales fueron extraídos directamente del binario.
#  Método y posición de cada color están en SOURCE/07_color_map.txt
# ---------------------------------------------------------------------------

# ── 1. FONDO del panel
#    Original: azul/morado oscuro  RGBA(0.060, 0.030, 0.120, 0.96)
#    Encontrado en: method[19] instr[83]  byte=0x009927
COLOR_FONDO_PANEL     = (1031127695, 1022739087, 1039516303, 1064682127)

# ── 2. COLOR ACTIVO (feature encendida, título, acento principal)
#    Original: morado claro  RGBA(0.850, 0.550, 1.0, 1.0)
#    Encontrado en: method[19] instr[133]  byte=0x009AB7
COLOR_ACTIVO          = (1062836634, 1057803469, 1065353216, 1065353216)

# ── 3. FONDO BOTÓN INACTIVO
#    Original: gris azulado oscuro  RGBA(0.045, 0.065, 0.100, 0.95)
#    Encontrado en: method[68] instr[44]  byte=0x01547F
COLOR_BTN_INACTIVO    = (1027101164, 1032134328, 1036831949, 1064514355)

# ── 4. FONDO HEADER / barra superior
#    Original: gris azulado  RGBA(0.070, 0.085, 0.110, 0.92)
#    Encontrado en: method[42] instr[3]  byte=0x011817
COLOR_HEADER          = (1032805417, 1034818683, 1038174126, 1064011039)

# ── 5. COLOR DORADO (acento secundario)
#    Original: dorado  RGBA(1.0, 0.760, 0.300, 1.0)
#    Encontrado en: method[73] instr[190]  byte=0x016377
COLOR_DORADO          = (1065353216, 1061326684, 1050253722, 1065353216)

# ── 6. PANEL OSCURO semitransparente (fondos de sección)
#    Original: RGBA(0.120, 0.130, 0.150, 0.850)
#    Encontrado en: method[112] instr[30]  byte=0x021D3F
COLOR_PANEL_OSCURO    = (1039516303, 1040522936, 1041865114, 1062836634)

# ── 7. ROJO/ALERTA (encabezado activo, señal peligro)
#    Original: rojo rosáceo  RGBA(0.960, 0.200, 0.220, 1.0)
#    Encontrado en: method[5], method[88], method[124]
COLOR_ROJO_ALERTA     = (1064682127, 1045220557, 1046562734, 1065353216)

# ---------------------------------------------------------------------------
# LÓGICA DE PARCHE
# ---------------------------------------------------------------------------

def patch_color(data: bytearray, orig: tuple, new: tuple, label: str) -> bytearray:
    """Reemplaza TODAS las ocurrencias de orig por new en el stream binario."""
    if orig == new:
        print(f'  [--]   {label}: sin cambio')
        return data
    old_b = color_stream(*orig)
    new_b = color_stream(*new)
    count = 0
    pos = 0
    while True:
        idx = bytes(data).find(old_b, pos)
        if idx == -1:
            break
        data[idx:idx + 32] = new_b
        pos = idx + 32
        count += 1
    if count == 0:
        old_vals = seq_bytes(orig)
        pos2 = bytes(data).find(old_vals)
        if pos2 != -1:
            print(f'  [WARN] {label}: encontrado como vals pero no como instrucciones completas (offset 0x{pos2:X})')
        else:
            r, g, b, a = [to_float(v) for v in orig]
            print(f'  [MISS] {label}: RGBA({r:.3f},{g:.3f},{b:.3f},{a:.3f}) no encontrado')
    else:
        print(f'  [OK]   {label}: {count} reemplazo(s)')
    return data

def main():
    if not SRC_BYTES.exists():
        sys.exit(
            f'ERROR: No se encuentra el binario fuente:\n  {SRC_BYTES}\n'
            f'Extrae primero el archivo del .3105 y configura SRC_BYTES en este script.'
        )

    data = bytearray(SRC_BYTES.read_bytes())
    print(f'Archivo cargado: {len(data):,} bytes\n')

    patches = [
        (COLOR_FONDO_PANEL,  (1031127695, 1022739087, 1039516303, 1064682127), 'FONDO_PANEL'),
        (COLOR_ACTIVO,       (1062836634, 1057803469, 1065353216, 1065353216), 'COLOR_ACTIVO'),
        (COLOR_BTN_INACTIVO, (1027101164, 1032134328, 1036831949, 1064514355), 'BTN_INACTIVO'),
        (COLOR_HEADER,       (1032805417, 1034818683, 1038174126, 1064011039), 'HEADER'),
        (COLOR_DORADO,       (1065353216, 1061326684, 1050253722, 1065353216), 'DORADO'),
        (COLOR_PANEL_OSCURO, (1039516303, 1040522936, 1041865114, 1062836634), 'PANEL_OSCURO'),
        (COLOR_ROJO_ALERTA,  (1064682127, 1045220557, 1046562734, 1065353216), 'ROJO_ALERTA'),
    ]

    for new_color, orig_color, label in patches:
        data = patch_color(data, orig_color, new_color, label)

    OUT_BYTES.write_bytes(data)
    size_orig = SRC_BYTES.stat().st_size
    size_new  = OUT_BYTES.stat().st_size
    print(f'\n✓ Generado: {OUT_BYTES}')
    print(f'  Original: {size_orig:,} bytes | Recoloreado: {size_new:,} bytes')
    if size_orig == size_new:
        print('  Tamaños iguales: OK (patch no cambia el tamaño del archivo)')

if __name__ == '__main__':
    main()
