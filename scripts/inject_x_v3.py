"""
Logo X final: fondo negro redondo, X BLANCA gruesa redondeada.
Exacto para el botón flotante oscuro del menú.
"""
import struct, sys, base64, io, hashlib, plistlib, os, uuid
from pathlib import Path
from datetime import datetime

sys.path.insert(0, r'C:\Users\J\Desktop\SRC CODE ASSEMBLY PROXY')
from ifix_codec import parse_ifix
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from PIL import Image, ImageDraw

SRC_B  = Path(r'C:\Users\J\Desktop\MI PROJECT\SOURCE\assembly-csharp-patch-FLUCK.bytes')
OUT_B  = Path(r'C:\Users\J\Desktop\MI PROJECT\SOURCE\assembly-csharp-patch-FLUCK.bytes')
OUT_3  = Path(r'C:\Users\J\Desktop\MI PROJECT\FLUCK V1.0.0.3105')
BUNDLE_ID  = 'com.dts.freefireth'
SCHEMA_VER = 3
TARGET_408 = 8480
TARGET_800 = 8604

def encode_7bit(n):
    r=[]
    while n>127: r.append((n&0x7F)|0x80); n>>=7
    r.append(n); return bytes(r)

def make_x_logo():
    """
    Fondo negro redondo.
    X BLANCA con brazos muy gruesos y puntas perfectamente redondeadas.
    """
    SIZE = 128
    img = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))  # transparente
    draw = ImageDraw.Draw(img)

    # Círculo negro de fondo
    draw.ellipse([0,0,SIZE-1,SIZE-1], fill=(20,20,20,255))

    # X BLANCA gruesa
    pad = 22
    lw  = 24

    draw.line([(pad,pad),(SIZE-pad,SIZE-pad)], fill=(255,255,255,255), width=lw)
    draw.line([(SIZE-pad,pad),(pad,SIZE-pad)], fill=(255,255,255,255), width=lw)

    # Puntas redondeadas blancas
    r = lw//2
    for px,py in [(pad,pad),(SIZE-pad,SIZE-pad),(SIZE-pad,pad),(pad,SIZE-pad)]:
        draw.ellipse([px-r,py-r,px+r,py+r], fill=(255,255,255,255))

    return img

def compress_to_target(img, target_len):
    for size in [128,96,80,64,56,48,40,32]:
        img_r = img.resize((size,size), Image.LANCZOS)
        for level in range(9,-1,-1):
            buf=io.BytesIO()
            img_r.save(buf,format='PNG',optimize=True,compress_level=level)
            png_b=buf.getvalue()
            b64=base64.b64encode(png_b).decode('ascii')
            if len(b64)<=target_len:
                return png_b, b64+' '*(target_len-len(b64))
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
    now=datetime.utcnow()
    pid=str(uuid.uuid4()).upper(); ckey=os.urandom(32); rid=str(uuid.uuid4()).upper()
    rules=[{'id':rid,'bundleID':BUNDLE_ID,
        'relativePath':'Documents/contentcache/Compulsory/ios/gameassetbundles/codepatch/assembly-csharp-patch.T0mFTHJhcvgBJrIRhg8bEapnUTM~3D',
        'replacementFilename':'assembly-csharp-patch.T0mFTHJhcvgBJrIRhg8bEapnUTM~3D',
        'replacementData':payload}]
    digs={rid:hashlib.sha256(payload).digest()}
    proj={'id':pid,'name':'FLUCK V1.0.0','author':'Dev @BNXYUNG7','isPrivate':False,
        'createdAt':now,'updatedAt':now,'bundleIdentifiers':[BUNDLE_ID],'directories':[],'rules':rules}
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

print('='*50)
print('FLUCK V1.0.0 — Boton: fondo negro + X blanca')
print('='*50)

img = make_x_logo()
img.save(r'C:\Users\J\Desktop\MI PROJECT\logo_X_preview.png')
print('Preview: logo_X_preview.png')

png408,b64_408 = compress_to_target(img, TARGET_408)
print(f'[408] PNG={len(png408)}b  B64={len(b64_408)}ch')

png800,b64_800 = compress_to_target(img, TARGET_800)
print(f'[800] PNG={len(png800)}b  B64={len(b64_800)}ch')

src = SRC_B.read_bytes()
data = inject_string(src,  408, b64_408)
data = inject_string(data, 800, b64_800)
OUT_B.write_bytes(data)

pkg = build_3105(data)
print(f'\nLISTO → {OUT_3}')
print(f'Tamano: {len(pkg):,} bytes | Sin pass | Dev @BNXYUNG7')
