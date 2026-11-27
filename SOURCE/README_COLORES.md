# FLUCK V1.0.0 — Guía para cambiar colores del panel

## Estructura del proyecto

```
Fluckv1-3105/
├── output/
│   └── FLUCK V1.0.0.3105              ← .3105 listo para instalar
├── scripts/
│   ├── inject_x_v3.py                 ← Inyecta logo X personalizado
│   ├── fix_circle.py                  ← Variante del logo X
│   └── decrypt_vault.py               ← Experimental: intento de descifrado del vault
└── SOURCE/
    ├── README_COLORES.md              ← este archivo
    ├── COLORS_EDIT.py                 ← ★ EDITA Y EJECUTA ESTE ★
    ├── 00_summary.txt                 ← resumen del IFix
    ├── 01_fixes.txt                   ← los 4 métodos parcheados
    ├── 02_types.txt                   ← 117 tipos referenciados
    ├── 03_extern_methods.txt          ← 214 llamadas externas
    ├── 04_strings.txt                 ← 1188 strings del IFix (base64 cifrado)
    ├── 05_fields.txt                  ← 404 campos de clase
    ├── 06_bytecode_raw.txt            ← bytecode de los 215 métodos
    ├── 07_color_map.txt               ← MAPA COMPLETO de colores con offsets exactos
    └── assembly-csharp-patch-RECOLORED.bytes  ← se genera al correr COLORS_EDIT.py
```

> **Nota:** `COLORS_EDIT.py` requiere que el binario extraído del `.3105`
> (`assembly-csharp-patch.T0mFTHJhcvgBJrIRhg8bEapnUTM~3D`) esté disponible
> en la ruta configurada en `SRC_BYTES`. La dependencia `ifix_codec` no está
> incluida en este repositorio.

---

## Mapa de colores del panel (extraídos del binario real)

| Constante en COLORS_EDIT.py | RGBA real                    | Descripción                     | Método/Offset  |
|-----------------------------|------------------------------|---------------------------------|----------------|
| `COLOR_FONDO_PANEL`         | (0.06, 0.03, 0.12, 0.96)    | Fondo principal del panel       | m[19] 0x9927   |
| `COLOR_ACTIVO`              | (0.85, 0.55, 1.0, 1.0)      | Feature activa / acento         | m[19] 0x9AB7   |
| `COLOR_BTN_INACTIVO`        | (0.045, 0.065, 0.1, 0.95)   | Fondo botón feature apagada     | m[68] 0x1547F  |
| `COLOR_HEADER`              | (0.07, 0.085, 0.11, 0.92)   | Barra superior / header         | m[42] 0x11817  |
| `COLOR_DORADO`              | (1.0, 0.76, 0.3, 1.0)       | Acento dorado secundario        | m[73] 0x16377  |
| `COLOR_PANEL_OSCURO`        | (0.12, 0.13, 0.15, 0.85)    | Fondos de sección interior      | m[112] 0x21D3F |
| `COLOR_ROJO_ALERTA`         | (0.96, 0.20, 0.22, 1.0)     | Rojo (alerta, estado crítico)   | m[5], m[88]    |

El archivo `07_color_map.txt` tiene la lista completa de las 59 secuencias de color con sus offsets exactos.

---

## Pasos para cambiar un color

### 1. Abre `SOURCE/COLORS_EDIT.py`

Cambia el valor de la constante que quieras. Ejemplo: fondo naranja oscuro:

```python
COLOR_FONDO_PANEL = (1032805417, 1022739087, 0, 1064682127)
#                    R=0.07       G=0.03    B=0  A=0.96
```

### 2. Para convertir un color a ints usa este snippet

```python
import struct
def to_int(f):
    return struct.unpack('<i', struct.pack('<f', f))[0]

# Ejemplo: naranja #FF7700 = R=1.0, G=0.467, B=0.0, A=1.0
print(to_int(1.0))    # → 1065353216
print(to_int(0.467))  # → 1054791475
print(to_int(0.0))    # → 0
```

### 3. Configura las rutas en COLORS_EDIT.py

Edita `SRC_BYTES` y `OUT_BYTES` al inicio del script para que apunten a las
ubicaciones correctas en tu equipo.

### 4. Ejecuta el script

```
python SOURCE/COLORS_EDIT.py
```

Salida esperada:
```
Archivo cargado: 3,971,675 bytes
  [OK]   FONDO_PANEL: 1 reemplazo(s)
  ...
✓ Generado: assembly-csharp-patch-RECOLORED.bytes
  Tamaños iguales: OK
```

### 5. Empaqueta en un nuevo .3105

Copia `assembly-csharp-patch-RECOLORED.bytes` como payload y usa tu
herramienta de empaquetado `.3105` para generar el nuevo archivo.

---

## Combinaciones de colores de ejemplo

### Tema Naranja
```python
COLOR_FONDO_PANEL  = (1017159841, 1017159841, 1017159841, 1064682127)
COLOR_ACTIVO       = (1065353216, 1055131975, 0, 1065353216)
COLOR_HEADER       = (1032805417, 1021396910, 0, 1064011039)
```

### Tema Verde (hacker style)
```python
COLOR_FONDO_PANEL  = (0, 1017159841, 0, 1064682127)
COLOR_ACTIVO       = (0, 1065353216, 0, 1065353216)
COLOR_HEADER       = (0, 1022739087, 0, 1064011039)
COLOR_DORADO       = (0, 1061158912, 0, 1065353216)
```

### Tema Cian / Blue
```python
COLOR_FONDO_PANEL  = (1017159841, 1021396910, 1032805417, 1064682127)
COLOR_ACTIVO       = (0, 1061158912, 1065353216, 1065353216)
COLOR_HEADER       = (1017159841, 1022739087, 1034818683, 1064011039)
COLOR_DORADO       = (0, 1062836634, 1065353216, 1065353216)
```
