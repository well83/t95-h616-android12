#!/usr/bin/env python3
"""sys_config.fex Orange Pi Zero 3 (configs/p2) -> T95 H616 AXP313A + NAND (configs/t95-axp313).
Сток платы H616-T95MAX-AXP313A-V2.0 (прошивка A29-0712) совпадает с A27 во всём, кроме таблиц DRAM. Берём:
  - из стока (sys_config.fex прошивки A29): секции DRAM (dram_para*, dram_select_para: select_mode = 1, вариант
    выбирается по GPIO PI1/PI9/PI13), twi_para, gpio_bias (банк PC на 1.8 В, как в стоке), axp1530_power_sply
    (+ dcdc1 0.96 В)
  - от Zero3 всё остальное (PMIC тот же), с: [target] burn_secure_mode = 1 и [platform] secure_without_OS = 0
    (SoC T95 с прожжённым secure boot); [card2_boot_para] sdc_io_1v8 = 1 как у Zero3 и в стоке
  - nand0_used = 0 и storage_type = -1 как в стоке: U-Boot сам ищет NAND
использование: t95_axp313_sys_config.py p2/sys_config.fex stock_sys_config.fex t95-axp313/sys_config.fex"""
import re, sys
zero3, stock, dst = sys.argv[1:4]

def sections(text):
    """[(имя, текст секции вместе с заголовком)] в порядке файла"""
    parts = re.split(r'(?m)^(?=\[[^\]]+\]\s*$)', text)
    out = []
    for p in parts:
        m = re.match(r'\[([^\]]+)\]', p)
        out.append((m.group(1) if m else None, p))
    return out

z = sections(open(zero3, encoding='latin-1').read())
s = dict(sections(open(stock, encoding='latin-1').read().replace('\r\n', '\n')))
FROM_STOCK = re.compile(r'^(dram_para\d*|dram_select_para|twi_para|gpio_bias|axp1530_power_sply)$')

out = []
names = set()
for name, txt in z:
    names.add(name)
    if name and FROM_STOCK.match(name):
        assert name in s, name
        txt = s[name] if s[name].endswith('\n\n') else s[name].rstrip('\n') + '\n\n'
    out.append(txt)
    # варианты DRAM стока (dram_para1..N), которых нет у Zero3, — сразу после [dram_para]
    if name == 'dram_para':
        for sn in s:
            if sn and re.match(r'^dram_para\d+$', sn) and sn not in dict(z):
                out.append(s[sn] if s[sn].endswith('\n\n') else s[sn].rstrip('\n') + '\n\n')
d = ''.join(out)

def set_key(sec, key, val):
    """задаёт key = val в секции (добавляет строку после заголовка, если её нет)"""
    global d
    m = re.search(r'(?m)^\[' + re.escape(sec) + r'\]\s*$', d); assert m, sec
    end = re.search(r'(?m)^\[', d[m.end():]); end = m.end() + (end.start() if end else len(d) - m.end())
    body = d[m.end():end]
    pat = re.compile(r'(?m)^' + re.escape(key) + r'\s*=.*$')
    body = pat.sub(f'{key} = {val}', body, count=1) if pat.search(body) else f'\n{key} = {val}' + body
    d = d[:m.end()] + body + d[end:]

set_key('platform', 'secure_without_OS', '0')
set_key('target', 'burn_secure_mode', '1')
set_key('power_sply', 'dcdc1_vol', '1000960')
open(dst, 'w', encoding='latin-1').write(d)
print('ok', dst)
