#!/usr/bin/env python3
"""Громкость звука загрузки: умножает part0/audio.wav в bootanimation.zip на 10^(dB/20) и пишет zip без сжатия
(STORED, как требует bootanimation). В b19 звук на -24 дБ от оригинала AW (пик 26295 -> 1659).
Файл: device/softwinner/apollo/common/media/bootanimation/bootanimation.zip (общий для всех плат T95).
использование: t95_bootsound.py оригинал.zip новый.zip -24"""
import array, io, struct, sys, zipfile

src, dst, db = sys.argv[1], sys.argv[2], float(sys.argv[3])
zi = zipfile.ZipFile(src)
w = zi.read('part0/audio.wav')
assert w[:4] == b'RIFF' and w[8:12] == b'WAVE'
p, fmt = 12, None
while p < len(w):
    cid, sz = w[p:p + 4], struct.unpack('<I', w[p + 4:p + 8])[0]
    if cid == b'fmt ':
        fmt = struct.unpack('<HHIIHH', w[p + 8:p + 24])
    if cid == b'data':
        ds, dl = p + 8, sz
        break
    p += 8 + sz + (sz & 1)
assert fmt and fmt[5] == 16, 'нужен PCM 16 бит'
a = array.array('h')
a.frombytes(w[ds:ds + dl])
k = 10 ** (db / 20)
b = array.array('h', (max(-32768, min(32767, round(x * k))) for x in a))
print('пик %d -> %d (x%.4f)' % (max(map(abs, a)), max(map(abs, b)), k))
nw = w[:ds] + b.tobytes() + w[ds + dl:]
out = io.BytesIO()
zo = zipfile.ZipFile(out, 'w', zipfile.ZIP_STORED)
for i in zi.infolist():
    ni = zipfile.ZipInfo(i.filename, i.date_time)
    ni.compress_type, ni.external_attr = zipfile.ZIP_STORED, i.external_attr
    zo.writestr(ni, nw if i.filename == 'part0/audio.wav' else zi.read(i.filename))
zo.close()
open(dst, 'wb').write(out.getvalue())
