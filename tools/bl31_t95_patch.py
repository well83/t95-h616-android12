#!/usr/bin/env python3
# BL31 (ARM Trusted Firmware) Allwinner для H618, адаптация под T95 (H616).
# Использование: python3 bl31_t95_patch.py longan/device/config/chips/h618/bin/bl31.bin longan/device/config/chips/h618/bin/bl31_t95.bin
# 1) 0x1F4C: cbz -> b: пропуск «hardware check», который на H616 даёт PANIC.
# 2) 0x1CF0..0x1D00 (PSCI SYSTEM_OFF): при RTC GPR[2]=0xe (CONFIG_SUNXI_FAKE_POWEROFF) СРАЗУ уходит в box standby
#    (функция 0x1B2C, та же, что U-Boot вызывает через SMC 0x8000ff14), вместо сброса. На T95 сброс обнуляет весь
#    домен RTC (включая GPR), поэтому флаг до U-Boot никогда не доходит. При пробуждении (пульт) сброс
#    -> обычная холодная загрузка (GPR обнулены). Проверено на боксе 09.10.2026.
# Проверяется хэш оригинала (SDK Orange Pi 13.07.2023).
import sys, hashlib
src, dst = sys.argv[1], sys.argv[2]
d = bytearray(open(src, 'rb').read())
h = hashlib.sha256(d).hexdigest()
assert h.startswith('66ecc8d528bc0cb5'), 'bl31.bin отличается от ожидаемого: ' + h
def w(a, old, new):
    assert d[a:a + 4] == old.to_bytes(4, 'little'), hex(a)
    d[a:a + 4] = new.to_bytes(4, 'little')
w(0x1F4C, 0x34000040, 0x14000002)  # cbz w0,0x1f54 -> b 0x1f54
w(0x1CF0, 0x940014dc, 0xaa1303e0)  # bl reset      -> mov x0,x19 (сохранённый DT)
w(0x1CF4, 0xd503207f, 0x97ffff8e)  # wfi           -> bl 0x1b2c (box standby)
w(0x1CF8, 0xb00000a0, 0x940014da)  # adrp          -> bl 0x7060 (сброс при пробуждении)
w(0x1CFC, 0x91022000, 0xd503207f)  # add           -> wfi
w(0x1D00, 0x940021e9, 0x17ffffff)  # bl printf     -> b 0x1cfc
open(dst, 'wb').write(d)
print('записан', dst, hashlib.sha256(d).hexdigest())
