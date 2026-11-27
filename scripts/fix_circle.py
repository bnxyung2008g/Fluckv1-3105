"""
X final: círculo negro, X blanca delgada con puntas redondeadas.
"""
import io, base64, hashlib, plistlib, os, uuid, sys
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw

sys.path.insert(0, r'C:\Users\J\Desktop\SRC CODE ASSEMBLY PROXY')
from ifix_codec import parse_ifix
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SRC_B = Path(r'C:\Users\J\Desktop\MI PROJECT\SOURCE\assembly-csharp-patch-FLUCK.bytes')
OUT_B = Path(r'C:\Users\J\Desktop\MI PROJECT\SOURCE\assembly-csharp-patch-FLUCK.bytes')
OUT_3 = Path(r'C:\Users\J\Desktop\MI PROJECT\FLUCK V1.0.0.3105')
BUNDLE_ID  = 'com.dts.freefireth'
SCHEMA_VER = 3

def encode_7bit(n):
    r=[]
    while n>127: r.append((n&0x7F)|0x80); n>>=7
    r.append(n); return bytes(r)

def make_x_logo():
    S   = 512
    pad = int(S * 0.13)   # ~67 — margen desde borde
    lw  = int(S * 0.13)   # ~67 — grosor del brazo

    # Canvas RGBA transparente
    img  = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Círculo negro sólido
    draw.ellipse([0, 0, S-1, S-1], fill=(0, 0, 0, 255))

    # Dos líneas blancas diagonales
    draw.line([(pad, pad), (S-pad, S-pad)], fill=(255,255,255,255), width=lw)
    draw.line([(S-pad, pad), (pad, S-pad)], fill=(255,255,255,255), width=lw)

    # Puntas redondeadas en los 4 extremos
    r = lw // 2
    for px, py in [(pad,pad),(S-pad,S-pad),(S-pad,pad),(pad,S-pad)]:
        draw.ellipse([px-r, py-r, px+r, py+r], fill=(255,255,255,255))

    # Máscara circular — recorta las esquinas
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S-1, S-1], fill=255)
    img.putalpha(mask)

    return img.resize((128, 128), Image.LANCZOS)

def compress_to_target(img, target_len, label=''):
    for size in [128, 96, 80, 64, 56, 48, 40, 32]:
        img_r = img if size==64 else img.resize((size,size), Image.LANCZOS)
        for level in range(9,-1,-1):
            buf=io.BytesIO()
            img_r.save(buf,format='PNG',optimize=True,compress_level=level)
            b64=base64.b64encode(buf.getvalue()).decode('ascii')
            if len(b64)<=target_len:
                padded=b64+' '*(target_len-len(b64))
                print(f'  {label}: {size}px lv{level} PNG={len(buf.getvalue())}b OK')
                return buf.getvalue(),padded
    return None,None

def inject_string(data_bytes, sidx, new_b64):
    data=bytearray(data_bytes)
    p=parse_ifix(bytes(data),2795)
    old=p['strings'][sidx].encode('utf-8')
    lb=encode_7bit(len(old))
    idx=bytes(data).find(lb+old)
    if idx==-1: print(f'  MISS [{sidx}]'); return None
    ne=new_b64.encode('utf-8')
    if len(ne)!=len(old): print(f'  LEN ERR [{sidx}]'); return None
    data[idx+len(lb):idx+len(lb)+len(old)]=ne
    print(f'  [OK] string[{sidx}] @ 0x{idx:X}')
    return bytes(data)

def seal(pt,key,aad):
    n=os.urandom(12); return n+AESGCM(key).encrypt(n,pt,aad)

def build_3105(payload):
    now=datetime.utcnow(); pid=str(uuid.uuid4()).upper()
    ckey=os.urandom(32); rid=str(uuid.uuid4()).upper()
    rules=[{'id':rid,'bundleID':BUNDLE_ID,
        'relativePath':'Documents/contentcache/Compulsory/ios/gameassetbundles/codepatch/assembly-csharp-patch.T0mFTHJhcvgBJrIRhg8bEapnUTM~3D',
        'replacementFilename':'assembly-csharp-patch.T0mFTHJhcvgBJrIRhg8bEapnUTM~3D',
        'replacementData':payload}]
    digs={rid:hashlib.sha256(payload).digest()}
    proj={'id':pid,'name':'FLUCK V1.2.0','author':'Dev @BNXYUNG7',
        'isPrivate':False,'createdAt':now,'updatedAt':now,
        'bundleIdentifiers':[BUNDLE_ID],'directories':[],'rules':rules}
    pl=plistlib.dumps({'project':proj,'replacementDigests':digs},fmt=plistlib.FMT_BINARY)
    aad=f'3105PATCH/v{SCHEMA_VER}/payload/{pid}'.encode()
    enc=seal(pl,ckey,aad)
    env={'schemaVersion':SCHEMA_VER,'packageID':pid,'isPasswordProtected':False,
        'publicContentKey':ckey,'keyFingerprint':hashlib.sha256(ckey).digest(),'encryptedPayload':enc}
    pkg=b'3105PATCH\x00'+plistlib.dumps(env,fmt=plistlib.FMT_BINARY)
    OUT_3.write_bytes(pkg)
    e2=plistlib.loads(pkg[10:])
    pt2=AESGCM(e2['publicContentKey']).decrypt(e2['encryptedPayload'][:12],e2['encryptedPayload'][12:],aad)
    b2=plistlib.loads(pt2)
    assert hashlib.sha256(b2['project']['rules'][0]['replacementData']).digest()==digs[rid]
    return pkg

# MAIN
print('Generando X: delgada + puntas redondeadas...')
img = make_x_logo()

c = img.size[0]//2
print(f'  Centro (blanco): {img.getpixel((c,c))}')
print(f'  Arriba  (negro): {img.getpixel((c,2))}')
print(f'  Esquina (trans): {img.getpixel((0,0))}')

# Preview sobre fondo gris
bg = Image.new('RGB',(512,512),(128,128,128))
fg = img.resize((512,512), Image.LANCZOS)
bg.paste(fg,(0,0),fg)
bg.save(r'C:\Users\J\Desktop\MI PROJECT\logo_X_preview.png')
print('Preview guardado')

_, b64_408 = compress_to_target(img, 8480, '408')
_, b64_800 = compress_to_target(img, 8604, '800')

print('\nInyectando...')
src  = SRC_B.read_bytes()
data = inject_string(src,  408, b64_408)
data = inject_string(data, 800, b64_800)
OUT_B.write_bytes(data)

pkg = build_3105(data)
print(f'\nLISTO -> {OUT_3}')
print(f'Tamaño: {len(pkg):,} bytes | Dev @BNXYUNG7 | Sin pass OK')
