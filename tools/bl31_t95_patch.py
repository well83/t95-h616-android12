#!/usr/bin/env python3
# BL31 (ARM Trusted Firmware) Allwinner для H618, адаптация под T95 (H616).
# Использование: python3 bl31_t95_patch.py [--fakeoff] longan/device/config/chips/h618/bin/bl31.bin longan/device/config/chips/h618/bin/bl31_t95.bin
# 1) 0x1F4C: cbz -> b: пропуск «hardware check», который на H616 даёт PANIC. Нужен всегда.
# 2) только с --fakeoff (старый обход, сборки b13/b14): 0x1CF0..0x1D00 (PSCI SYSTEM_OFF) при RTC GPR[2]=0xe
#    (CONFIG_SUNXI_FAKE_POWEROFF) СРАЗУ уходит в box standby (функция 0x1B2C, та же, что U-Boot вызывает через
#    SMC 0x8000ff14), вместо сброса. С b16 не нужен: настоящая причина (бит 4 регистра AXP806 0x32, его
#    включает sboot, и каждый сброс обнулял домен RTC) исправлена в U-Boot/ядре (patches/09), и работает
#    штатная схема Allwinner (флаг -> сброс -> U-Boot -> standby).
# Проверяется хэш оригинала (SDK Orange Pi 13.07.2023).
import sys, hashlib
args = sys.argv[1:]
fakeoff = '--fakeoff' in args
src, dst = [a for a in args if a != '--fakeoff']
d = bytearray(open(src, 'rb').read())
h = hashlib.sha256(d).hexdigest()
assert h.startswith('66ecc8d528bc0cb5'), 'bl31.bin отличается от ожидаемого: ' + h
def w(a, old, new):
    assert d[a:a + 4] == old.to_bytes(4, 'little'), hex(a)
    d[a:a + 4] = new.to_bytes(4, 'little')
w(0x1F4C, 0x34000040, 0x14000002)  # cbz w0,0x1f54 -> b 0x1f54
if fakeoff:
    w(0x1CF0, 0x940014dc, 0xaa1303e0)  # bl reset      -> mov x0,x19 (сохранённый DT)
    w(0x1CF4, 0xd503207f, 0x97ffff8e)  # wfi           -> bl 0x1b2c (box standby)
    w(0x1CF8, 0xb00000a0, 0x940014da)  # adrp          -> bl 0x7060 (сброс при пробуждении)
    w(0x1CFC, 0x91022000, 0xd503207f)  # add           -> wfi
    w(0x1D00, 0x940021e9, 0x17ffffff)  # bl printf     -> b 0x1cfc
open(dst, 'wb').write(d)
print('записан', dst, hashlib.sha256(d).hexdigest())
