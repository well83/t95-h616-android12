#!/usr/bin/env python3
"""board.dts Orange Pi Zero 3 (longan configs/p2/linux-5.4) -> T95 H616 (configs/t95/linux-5.4).
Те же аппаратные исправления, что были проверены на OmniROM (приставка загрузилась 02.10), но в исходниках:
  1. PMIC AXP1530 -> AXP806 (i2c s_twi0 0x36): dcdca CPU DVFS, dcdcc 0.96 В, dcdcd DRAM DDR3 1.5 В, dcdce 3.3 В, bldo1 1.8 В
  2. eMMC sdc2 включена, DDR52 50 МГц (без HS200/HS400), как в стоке; U-Boot: sdc_io_1v8 = 0
  3. Ethernet: gmac0 (RGMII Zero3) off, gmac1 (RMII -> EPHY AC200) on; twi3 (AC200) на PA10/PA11 в режиме engine
  4. LED PH6/PH7, VBUS USB на PH8, SPI off (выводы eMMC/LED), USB0 host, card-detect SD-карты PI16
  5. framebuffer 1920x1080, пульт NEC 0xfe02 power 0x40 (пробуждение), pinctrl sleep ИК = default
  6. OPP CPU измерены на T95 (сток, 29.09)
использование: t95_board_dts.py p2/linux-5.4/board.dts t95/linux-5.4/board.dts"""
import re, sys
src, dst = sys.argv[1:3]
d = open(src).read()

def sub(old, new, count=1):
    global d
    n = d.count(old)
    assert n == count, f'{n} вхождений (ожидалось {count}): {old[:70]!r}'
    d = d.replace(old, new)

def sub_re(pat, new, flags=re.M | re.S):
    global d
    d, n = re.subn(pat, new, d, count=1, flags=flags)
    assert n == 1, f'нет вхождений: {pat[:70]!r}'

sub('model = "Orange Pi Zero 3";', 'model = "T95 H616";')

# 4. VBUS порта USB: PH8 (сток usbc1), всегда включён (PC16 на Zero3 — вывод eMMC у T95)
sub('\t\tgpio = <&pio PC 16 GPIO_ACTIVE_HIGH>;\n\t\tenable-active-high;\n',
    '\t\tgpio = <&pio PH 8 GPIO_ACTIVE_HIGH>;\n\t\tenable-active-high;\n\t\tregulator-always-on;\n')

# 1. ссылки на регуляторы: AXP1530 -> AXP806 с той же функцией
sub('cpu-supply = <&reg_dcdc2>;', 'cpu-supply = <&reg_dcdca>;')
for a, b in (('reg_dldo1', 'reg_dcdce'), ('reg_aldo1', 'reg_bldo1'), ('reg_dcdc1', 'reg_dcdcc')):
    d = d.replace(f'<&{a}>', f'<&{b}>')

# 2. eMMC
sub_re(r'(&sdc2 \{\n)\tmax-frequency = <100000000>;\n\tmmc-ddr-1_8v;\n\tmmc-hs200-1_8v;\n\tmmc-hs400-1_8v;\n',
       r'\1\tmax-frequency = <50000000>;\n\tmmc-ddr-1_8v;\n\tctl-spec-caps = <0x8>;\n')
sub_re(r'(&sdc2 \{.*?)status = "disabled";', r'\1status = "okay";')
sub_re(r'(card2_boot_para@3 \{.*?sdc_io_1v8 = )<0x1>;', r'\1<0x0>;')

# 4. card-detect SD: PI16 (PF6 на T95 не подключён, проверено в Armbian)
sub('cd-gpios = <&pio PF 6 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>;',
    'cd-gpios = <&pio PI 16 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>;')

# 4. SPI flash/spi1 Zero3 занимают выводы eMMC (PC0/PC2-4) и LED (PH6-8)
sub_re(r'(&spi0 \{.*?)status = "okay";', r'\1status = "disabled";')
sub_re(r'(&spi1 \{.*?)status = "okay";', r'\1status = "disabled";')

# 3. twi3 = AC200 на PA10/PA11, режим engine (twi_drv_used 0), как в стоке
sub_re(r'(twi3_pins_a: twi3@0 \{\n\t\tpins = )"PH4", "PH5";', r'\1"PA10", "PA11";')
sub_re(r'(twi3_pins_b: twi3@1 \{\n\t\tpins = )"PH4", "PH5";', r'\1"PA10", "PA11";')
sub_re(r'(&twi3 \{.*?twi_drv_used = )<1>;', r'\1<0>;')

# 1. PMIC
pmu_old = re.search(r'\tpmu0: pmu\{\n.*?\n\t\};\n(?=\};)', d, re.S)
assert pmu_old, 'узел pmu0'
def reg(lbl, name, mn=None, mx=None, extra=''):
    s = f'\t\t\t{lbl}{name} {{\n\t\t\t\tregulator-name = "axp806-{name}";\n'
    if mn is None:
        return s + '\t\t\t};\n\n'
    s += f'\t\t\t\tregulator-min-microvolt = <{mn}>;\n\t\t\t\tregulator-max-microvolt = <{mx}>;\n'
    return s + extra + '\t\t\t\tregulator-always-on;\n\t\t\t};\n\n'
pmu = ('\tpmu0: pmu{\n\t\tcompatible = "x-powers,axp806";\n\t\treg = <0x36>;\n\t\t/* irq line nc */\n'
       '\t\twakeup-source;\n\n'
       '\t\tstandby_param: standby_param {\n\t\t\tvcc-dram = <0x8>;\n\t\t};\n\n'
       '\t\t/* T95: напряжения измерены на стоке; фиксированные — с min = max */\n\t\tregulators{\n'
       + reg('reg_dcdca: ', 'dcdca', 810000, 1160000, '\t\t\t\tregulator-ramp-delay = <200>;\n')
       + reg('', 'dcdcb')
       + reg('reg_dcdcc: ', 'dcdcc', 960000, 960000)
       + reg('reg_dcdcd: ', 'dcdcd', 1500000, 1500000)
       + reg('reg_dcdce: ', 'dcdce', 3300000, 3300000)
       + reg('', 'aldo1', 3300000, 3300000) + reg('', 'aldo2', 3300000, 3300000) + reg('', 'aldo3', 3300000, 3300000)
       + reg('reg_bldo1: ', 'bldo1', 1800000, 1800000)
       + ''.join(reg('', n) for n in ('bldo2', 'bldo3', 'bldo4', 'cldo1', 'cldo2', 'cldo3', 'sw'))).rstrip('\n') \
      + '\n\t\t};\n\t};\n'
d = d[:pmu_old.start()] + pmu + d[pmu_old.end():]

# 3. Ethernet
sub_re(r'(&gmac0 \{.*?)status = "okay";', r'\1status = "disabled";')
sub_re(r'(&gmac1 \{.*?)status = "disabled";', r'\1status = "okay";')

# 4. LED T95 (сток normal_led PH6, standby_led PH7) вместо выводов PC12/PC13 (eMMC) Zero3
sub('gpio_pin_1 = <&pio PC 12 GPIO_ACTIVE_LOW>;', 'gpio_pin_1 = <&pio PH 6 GPIO_ACTIVE_LOW>;')
sub('gpio_pin_2 = <&pio PC 13 GPIO_ACTIVE_HIGH>;', 'gpio_pin_2 = <&pio PH 7 GPIO_ACTIVE_HIGH>;')

# 5. framebuffer 1080p (HWC берёт размер из fb0)
sub_re(r'fb0_width( *)= <1280>;', r'fb0_width\1= <1920>;')
sub_re(r'fb0_height( *)= <720>;', r'fb0_height\1= <1080>;')

# 5. ИК: пульт T95 + состояние sleep = default (BL31 читает кнопку power с приёмника во сне)
sub('\tpinctrl-1 = <&s_cir0_pins_b>;', '\tpinctrl-1 = <&s_cir0_pins_a>;')
sub('ir_power_key_code1 = <0x1a>;', 'ir_power_key_code1 = <0x40>;')
sub('ir_addr_code1 = <0xfb04>;', 'ir_addr_code1 = <0xfe02>;')

# 4. USB0 в режиме host (второй порт USB-A)
sub_re(r'(&usbc0 \{.*?usb_port_type\t*= )<0x0>;', r'\1<0x1>;\n\tusb_host_init_state\t= <0x1>;')

# 6. OPP CPU
opps = [(480, 900000), (600, 900000), (792, 900000), (1008, 920000), (1200, 980000), (1512, 1120000)]
dele = ''.join(f'\t/delete-node/ opp@{f}000000;\n' for f in
               (480, 600, 720, 792, 936, 1008, 1032, 1104, 1200, 1296, 1320, 1344, 1416, 1512))
new = ''.join(f'\n\topp@{f}000000 {{\n\t\topp-hz = /bits/ 64 <{f}000000>;\n\t\topp-microvolt = <{v}>;\n'
              f'\t\tclock-latency-ns = <244144>; /* 8 32k periods */\n\t\topp-supported-hw = <0xff>;\n\t}};\n'
              for f, v in opps)
d += ('\n/* T95: напряжения CPU измерены на стоковой прошивке (lean8-root, 29.09.2026), один bin */\n'
      '&cpu_opp_table {\n' + dele + new + '};\n')

open(dst, 'w').write(d)
print('ok', dst)
