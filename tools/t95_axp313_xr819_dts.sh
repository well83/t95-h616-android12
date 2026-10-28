#!/bin/bash
# Вариант с Wi-Fi XR819 для папки платы: configs/t95-axp313 (H61X-T95MAX-AXP313A-V3) или configs/t95-axp806
# (b24-xr819: H616-T95MAX-V4.0 с XR819 вместо UWE5622). Меняет board.dts и linux-5.4/board.dts.
# - банк PG (SDIO Wi-Fi) на 3,3 В, как в стоковой X29 (без sdio-used-1v8): vcc-pg-supply = reg_pio3_3
# - sdc1 без режимов UHS (XR819 = SDIO 2.0)
# - в &btlpm добавлен device_type = "btlpm": wireless_switch.ko ищет узел через of_find_node_by_type(), без него
#   инициализация падает и xr819.ko не загружается (Unknown symbol wlan_reg_enable / wlan_set_reset_pin)
# Только для сборок с XR819: wireless_switch.ko есть в modules.load всех плат, на других платах он выключил бы Wi-Fi.
# использование: t95_axp313_xr819_dts.sh <longan>/device/config/chips/h618/configs/<t95-axp313|t95-axp806>
#                (сохраните оба board.dts до сборки и верните их после)
set -euo pipefail
C=${1:?папка configs/t95-axp313 или t95-axp806}
# board.dts может быть ссылкой на linux-5.4/board.dts: каждый файл меняется один раз
for f in $(realpath $C/board.dts $C/linux-5.4/board.dts | sort -u); do
  sed -i 's|vcc-pg-supply = <&reg_pio1_8>;|vcc-pg-supply = <\&reg_pio3_3>;|' $f
  sed -i '/^&sdc1 {/,/^};/{/sd-uhs-/d}' $f
  sed -i '/^&btlpm {/a\	device_type = "btlpm";' $f
  grep -q 'vcc-pg-supply = <&reg_pio3_3>;' $f
  ! sed -n '/^&sdc1 {/,/^};/p' $f | grep -q sd-uhs
  sed -n '/^&sdc0 {/,/^};/p' $f | grep -q sd-uhs-sdr104
  sed -n '/^&btlpm {/,/^};/p' $f | grep -q 'device_type = "btlpm";'
done
echo "OK $C: PG 3,3 В, sdc1 без UHS, device_type btlpm"
