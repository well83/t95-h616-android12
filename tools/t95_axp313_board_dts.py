#!/usr/bin/env python3
"""board.dts Orange Pi Zero 3 (longan configs/p2/linux-5.4) -> T95 H616 AXP313A + NAND (configs/t95-axp313/linux-5.4).
Плата H616-T95MAX-AXP313A-V2.0: PMIC AXP313A (= AXP1530, как у Zero3), память raw NAND (TSOP-48) вместо eMMC,
DDR3. DTB стоковой прошивки T95 A27 (общая для плат AXP806/eMMC и AXP313A/NAND) описывает AXP1530 так же, как Zero3,
поэтому узел PMIC берётся от Zero3 без изменений. От T95 (t95_board_dts.py) берётся всё, кроме PMIC и eMMC:
  1. PMIC AXP1530 Zero3 без изменений (dcdc2 = CPU, dcdc3 = DRAM, aldo1 1.8 В, dldo1 3.3 В)
  2. NAND: nand0 включён (U-Boot включает его и сам при загрузке с NAND), eMMC sdc2 выключена (те же выводы PC),
     SPI выключен (выводы PC)
  3. Ethernet: gmac0 (RGMII Zero3) off, gmac1 (RMII -> EPHY AC200) on; twi3 (AC200) на PA10/PA11 в режиме engine
  4. LED PH6/PH7, VBUS USB на PH8, USB0 host, card-detect SD-карты PI16
  5. framebuffer 1920x1080, пульт NEC 0xfe02 power 0x40 (пробуждение), pinctrl sleep ИК = default
  6. OPP CPU: на стоковой прошивке scaling_available_frequencies = 480 600 792 1008 1200 1512 и dcdc2 1,12 В
     -> bin 1 стоковой A27 (opp-supported-hw 0x01), те же напряжения, что у моей T95
  7. WiFi/BT AP6334 (BCM43342): тактовая 32 кГц (LPO) на модуль через PG10 (x32kfout), как в стоковой A27
     (losc_out от hosc32k = 24 МГц / 750); без неё Bluetooth BCM не работает
  8. standby_param как в стоковой A27: только vcc-dram (dcdc3). Значения Zero3 (vdd-cpua, vdd-sys, vcc-io) BL31
     выключает во сне -> приставка не просыпается (только по питанию)
  9. NAND: nand0_close_model_match = 1, как в стоковых DTB (A29 NAND, A32). Иначе для Micron с одинаковым ID
     (2c 84 64 3c a9 04: FxxL85C71KSBAB / KSBAR / MT29F128G08CBEBB3W) драйвер выбирает запись по имени из
     ONFI parameter page, а не первую по ID, как сток
 10. NAND: выводы nand0@0/@1 с allwinner,muxsel (стиль sdc2). U-Boot (fdt_set_all_pin) берёт их из DT ядра
     (working_fdt) и без muxsel не настраивает выводы -> NAND не найдена (FES: "storage NAND, size 0").
     drive 1 как в стоковых DTB A27/A32
использование: t95_axp313_board_dts.py p2/linux-5.4/board.dts t95-axp313/linux-5.4/board.dts"""
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

sub('model = "Orange Pi Zero 3";', 'model = "T95 H616 AXP313A";')

# 4. VBUS порта USB: PH8 (PC16 — вывод NAND)
sub('\t\tgpio = <&pio PC 16 GPIO_ACTIVE_HIGH>;\n\t\tenable-active-high;\n',
    '\t\tgpio = <&pio PH 8 GPIO_ACTIVE_HIGH>;\n\t\tenable-active-high;\n\t\tregulator-always-on;\n')

# 2. NAND вместо eMMC: sdc2 у Zero3 уже выключена, проверяем; nand0 включаем
assert re.search(r'&sdc2 \{[^}]*status = "disabled";', d), 'sdc2 должна быть disabled'
sub_re(r'(&nand0 \{.*?)status = "disabled";', r'\1status = "okay";')
# 9. выбор записи таблицы ID NAND как в стоке (только по ID)
sub_re(r'(&nand0 \{.*?)(\tstatus = "okay";)', r'\1\tnand0_close_model_match = <1>;\n\2')

# 10. выводы NAND для U-Boot: allwinner,muxsel (после sdc2@2, как sdc0/sdc2)
sub_re(r'(\tsdc2_pins_c: sdc2@2 \{.*?\n\t\};\n)',
       r'\1\n\t/* T95 NAND: U-Boot (fdt_set_all_pin по working_fdt) требует allwinner,muxsel; drive 1, как в стоковых A27/A32 */\n'
       r'\tnand0_pins_a: nand0@0 {\n\t\tallwinner,pins = "PC0", "PC1", "PC2", "PC5",\n'
       r'\t\t\t\t "PC8", "PC9", "PC10", "PC11",\n\t\t\t\t "PC12", "PC13", "PC14", "PC15",\n\t\t\t\t "PC16";\n'
       r'\t\tallwinner,function = "nand0";\n\t\tallwinner,muxsel = <2>;\n\t\tallwinner,drive = <1>;\n\t\tallwinner,pull = <0>;\n\t};\n\n'
       r'\tnand0_pins_b: nand0@1 {\n\t\tallwinner,pins = "PC4", "PC6", "PC3", "PC7";\n'
       r'\t\tallwinner,function = "nand0";\n\t\tallwinner,muxsel = <2>;\n\t\tallwinner,drive = <1>;\n\t\tallwinner,pull = <1>;\n\t};\n')

# 4. card-detect SD: PI16
sub('cd-gpios = <&pio PF 6 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>;',
    'cd-gpios = <&pio PI 16 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>;')

# 2. SPI flash/spi1 Zero3 занимают выводы NAND (PC0/PC2-4) и LED (PH6-8)
sub_re(r'(&spi0 \{.*?)status = "okay";', r'\1status = "disabled";')
sub_re(r'(&spi1 \{.*?)status = "okay";', r'\1status = "disabled";')

# 3. twi3 = AC200 на PA10/PA11, режим engine (twi_drv_used 0), как в стоке
sub_re(r'(twi3_pins_a: twi3@0 \{\n\t\tpins = )"PH4", "PH5";', r'\1"PA10", "PA11";')
sub_re(r'(twi3_pins_b: twi3@1 \{\n\t\tpins = )"PH4", "PH5";', r'\1"PA10", "PA11";')
sub_re(r'(&twi3 \{.*?twi_drv_used = )<1>;', r'\1<0>;')

# 3. Ethernet
sub_re(r'(&gmac0 \{.*?)status = "okay";', r'\1status = "disabled";')
sub_re(r'(&gmac1 \{.*?)status = "disabled";', r'\1status = "okay";')

# 4. LED T95 (сток normal_led PH6, standby_led PH7) вместо PC12/PC13 Zero3 (выводы NAND)
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

# 6. OPP CPU (питание CPU здесь dcdc2 AXP313A): bin 1 стоковой A27 (подтверждён на стоке: макс. 1512 МГц)
opps = [(480, 900000), (600, 900000), (792, 900000), (1008, 920000), (1200, 980000), (1512, 1120000)]
dele = ''.join(f'\t/delete-node/ opp@{f}000000;\n' for f in
               (480, 600, 720, 792, 936, 1008, 1032, 1104, 1200, 1296, 1320, 1344, 1416, 1512))
new = ''.join(f'\n\topp@{f}000000 {{\n\t\topp-hz = /bits/ 64 <{f}000000>;\n\t\topp-microvolt = <{v}>;\n'
              f'\t\tclock-latency-ns = <244144>; /* 8 32k periods */\n\t\topp-supported-hw = <0xff>;\n\t}};\n'
              for f, v in opps)
d += ('\n/* T95 AXP313A: OPP = bin 1 стоковой прошивки A27 (как на стоке: 480..1512 МГц) */\n'
      '&cpu_opp_table {\n' + dele + new + '};\n')

# 7. 32 кГц на AP6334: PG10 = x32kfout, osc32k-out от dcxo-32k-out (24 МГц / 750), как в стоке
x32k = ('\t\tclocks = <&rtc_ccu CLK_OSC32K_OUT>;\n'
        '\t\tassigned-clocks = <&rtc_ccu CLK_OSC32K_OUT>;\n'
        '\t\tassigned-clock-parents = <&rtc_ccu CLK_DCXO_32K_OUT>;\n')
sub('\twlan: wlan {\n\t\tcompatible = "allwinner,sunxi-wlan";\n',
    '\twlan: wlan {\n\t\tcompatible = "allwinner,sunxi-wlan";\n' + x32k)
sub('\tbt: bt {\n\t\tcompatible = "allwinner,sunxi-bt";\n',
    '\tbt: bt {\n\t\tcompatible = "allwinner,sunxi-bt";\n' + x32k)
d += ('\n/* T95 AXP313A: 32 кГц (LPO) для AP6334 на PG10, как в стоковой A27 */\n'
      '&pio {\n\tx32kfout_pin: x32kfout@0 {\n\t\tpins = "PG10";\n\t\tfunction = "x32kfout";\n'
      '\t\tdrive-strength = <20>;\n\t\tbias-pull-up;\n\t};\n};\n\n'
      '&rfkill {\n\tpinctrl-names = "default";\n\tpinctrl-0 = <&x32kfout_pin>;\n};\n')

# 8. standby_param как в стоке A27: во сне остаётся только vcc-dram (dcdc3)
sub('\t\tstandby_param: standby_param {\n\t\t\tvdd-cpua = <0x2>;\n\t\t\tvdd-sys= <0x1>;\n'
    '\t\t\tvcc-io = <0x10>;\n\t\t\tvcc-dram = <0x4>;\n\t\t};\n',
    '\t\tstandby_param: standby_param {\n\t\t\tvcc-dram = <0x4>;\n\t\t};\n')

open(dst, 'w').write(d)
print('ok', dst)
