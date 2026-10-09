#!/usr/bin/env python3
"""sys_config.fex Orange Pi Zero 3 (configs/p2) -> T95 H616 (configs/t95).
В проверенной на приставке цепочке OmniROM sboot (DRAM) брал СТОКОВЫЙ sys_config T95, а U-Boot — исправленный
от Zero3; здесь файл один, поэтому:
  - из стока T95 (sys_config.fex прошивки): секции DRAM (dram_para*, dram_select_para), twi_para, gpio_bias
    (банк PC на 3.3 В: eMMC T95 на 3.3 В при старте)
  - от Zero3 всё остальное, с: [axp806_power_sply] dcdcc/dcdce как в стоке, [card2_boot_para] sdc_io_1v8 = 0,
    [target] burn_secure_mode = 1 и [platform] secure_without_OS = 0 (у SoC T95 прожжён secure boot)
использование: t95_sys_config.py p2/sys_config.fex stock_sys_config.fex t95/sys_config.fex"""
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
s = dict(sections(open(stock, encoding='latin-1').read()))
FROM_STOCK = re.compile(r'^(dram_para\d*|dram_select_para|twi_para|gpio_bias)$')

out = []
for name, txt in z:
    if name and FROM_STOCK.match(name):
        assert name in s, name
        txt = s[name] if s[name].endswith('\n\n') else s[name].rstrip('\n') + '\n\n'
    out.append(txt)
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
set_key('axp806_power_sply', 'dcdcc_vol', '1000960')
set_key('axp806_power_sply', 'dcdce_vol', '1003300')
set_key('card2_boot_para', 'sdc_io_1v8', '0')
open(dst, 'w', encoding='latin-1').write(d)
print('ok', dst)
