#!/usr/bin/env python3
"""Системный фон по умолчанию (b20+): тёмный нейтральный градиент 1920x1080 (#1c2430 слева вверху -> #0a0c10 справа
внизу) вместо логотипа "Orange pi" из BSP (common/overlay/.../default_wallpaper*.png), виден при выходе из приложений.
Пишет default_wallpaper.png и default_wallpaper_white.png в drawable-nodpi и drawable-sw720dp-nodpi.
использование: t95_wallpaper.py device/softwinner/apollo/apollo-t95/overlay/frameworks/base/core/res/res   (нужен Pillow)"""
import os, sys
from PIL import Image

res = sys.argv[1]
W, H = 1920, 1080
a, b = (0x1c, 0x24, 0x30), (0x0a, 0x0c, 0x10)
im = Image.new('RGB', (W, H))
px = im.load()
for y in range(H):
    for x in range(W):
        t = x / W * 0.4 + y / H * 0.6
        px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
for d in ('drawable-nodpi', 'drawable-sw720dp-nodpi'):
    os.makedirs(os.path.join(res, d), exist_ok=True)
    for n in ('default_wallpaper.png', 'default_wallpaper_white.png'):
        im.save(os.path.join(res, d, n), optimize=True)
